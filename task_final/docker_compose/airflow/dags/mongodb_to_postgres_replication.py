"""
DAG для репликации данных из MongoDB в PostgreSQL
Полная перезагрузка (TRUNCATE + INSERT) для каждой коллекции
"""

from datetime import datetime, timedelta
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException
import json 

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=10),
}

# Коллекции для обработки (имена в MongoDB)
COLLECTIONS = [
    'UserSessions',
    'EventLogs',
    'SupportTickets',
    'UserRecommendations',
    'ModerationQueue'
]

# Соответствие коллекций MongoDB и таблиц PostgreSQL
COLLECTION_TO_TABLE = {
    'UserSessions': 'user_sessions',
    'EventLogs': 'event_logs',
    'SupportTickets': 'support_tickets',
    'UserRecommendations': 'user_recommendations',
    'ModerationQueue': 'moderation_queue'
}

def parse_iso_date(date_str):
    """Преобразование ISO строки в datetime"""
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        date_str = date_str.replace('Z', '+00:00')
        return datetime.fromisoformat(date_str)
    except:
        return None

def transform_user_sessions(doc):
    """Трансформация для коллекции UserSessions"""
    doc.pop('_id', None)
    
    if not doc.get('session_id') or not doc.get('user_id'):
        return None
    
    doc['start_time'] = parse_iso_date(doc.get('start_time'))
    doc['end_time'] = parse_iso_date(doc.get('end_time'))
    doc['device'] = doc.get('device', 'unknown')
    doc['pages_visited'] = doc.get('pages_visited', [])
    doc['actions'] = doc.get('actions', [])
    
    return doc

def transform_event_logs(doc):
    """Трансформация для коллекции EventLogs"""
    doc.pop('_id', None)
    
    if not doc.get('event_id'):
        return None
    
    doc['timestamp'] = parse_iso_date(doc.get('timestamp'))
    doc['details'] = doc.get('details', {})
    
    return doc

def transform_support_tickets(doc):
    """Трансформация для коллекции SupportTickets"""
    doc.pop('_id', None)
    
    if not doc.get('ticket_id') or not doc.get('user_id'):
        return None
    
    doc['created_at'] = parse_iso_date(doc.get('created_at'))
    doc['updated_at'] = parse_iso_date(doc.get('updated_at'))
    doc['messages'] = doc.get('messages', [])
    doc['status'] = doc.get('status', 'open')
    doc['issue_type'] = doc.get('issue_type', 'other')
    
    return doc

def transform_user_recommendations(doc):
    """Трансформация для коллекции UserRecommendations"""
    doc.pop('_id', None)
    
    if not doc.get('user_id'):
        return None
    
    doc['last_updated'] = parse_iso_date(doc.get('last_updated'))
    doc['recommended_products'] = doc.get('recommended_products', [])
    
    return doc

def transform_moderation_queue(doc):
    """Трансформация для коллекции ModerationQueue"""
    doc.pop('_id', None)
    
    if not doc.get('review_id') or not doc.get('user_id'):
        return None
    
    doc['submitted_at'] = parse_iso_date(doc.get('submitted_at'))
    doc['rating'] = doc.get('rating')
    doc['flags'] = doc.get('flags', [])
    doc['moderation_status'] = doc.get('moderation_status', 'pending')
    
    return doc

TRANSFORM_FUNCTIONS = {
    'UserSessions': transform_user_sessions,
    'EventLogs': transform_event_logs,
    'SupportTickets': transform_support_tickets,
    'UserRecommendations': transform_user_recommendations,
    'ModerationQueue': transform_moderation_queue
}

def process_collection(collection_name, **context):
    """Основная функция обработки коллекции"""
    logger = logging.getLogger(__name__)
    logger.info(f"Начало обработки коллекции {collection_name}")
    
    try:
        mongo_hook = MongoHook(conn_id='mongo_default')
        mongo_client = mongo_hook.get_conn()
        mongo_db = mongo_client['test']
        mongo_collection = mongo_db[collection_name]
        
        # Получение данных 
        documents = list(mongo_collection.find())
        logger.info(f"Извлечено {len(documents)} документов из {collection_name}")
        
        if not documents:
            logger.info(f"Нет данных для коллекции {collection_name}")
            return
        
        # Трансформация данных
        transform_func = TRANSFORM_FUNCTIONS.get(collection_name)
        if not transform_func:
            raise AirflowException(f"Нет функции трансформации для {collection_name}")
        
        transformed_docs = []
        for doc in documents:
            transformed = transform_func(doc)
            if transformed:
                transformed_docs.append(transformed)
        
        logger.info(f"После трансформации: {len(transformed_docs)} документов")
        
        if not transformed_docs:
            logger.warning(f"Нет валидных документов для {collection_name}")
            return
        
        # Подключение к PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_etl')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        # Получаем имя таблицы из словаря соответствия
        table_name = COLLECTION_TO_TABLE[collection_name]
        
        # Проверка существования таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table_name,))
        if not cursor.fetchone()[0]:
            raise AirflowException(f"Таблица {table_name} не существует")
        
        # TRUNCATE таблицы
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        logger.info(f"Таблица {table_name} очищена")
        
        # Вставка данных
        if collection_name == 'UserSessions':
            for doc in transformed_docs:
                cursor.execute("""
                    INSERT INTO user_sessions 
                    (session_id, user_id, start_time, end_time, pages_visited, device, actions, loaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    doc['session_id'], doc['user_id'], doc['start_time'], doc['end_time'],
                    doc['pages_visited'], doc['device'], doc['actions']
                ))
        
        elif collection_name == 'EventLogs':
            for doc in transformed_docs:
                cursor.execute("""
                    INSERT INTO event_logs 
                    (event_id, timestamp, event_type, details, loaded_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    doc['event_id'], doc['timestamp'], doc['event_type'],
                    json.dumps(doc['details'])  # ← преобразуем в JSON-строку
                ))
        
        elif collection_name == 'SupportTickets':
            for doc in transformed_docs:
                cursor.execute("""
                    INSERT INTO support_tickets 
                    (ticket_id, user_id, status, issue_type, messages, created_at, updated_at, loaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    doc['ticket_id'], doc['user_id'], doc['status'], doc['issue_type'],
                    json.dumps(doc['messages']),  # ← преобразуем в JSON-строку
                    doc['created_at'], doc['updated_at']
                ))
        
        elif collection_name == 'UserRecommendations':
            for doc in transformed_docs:
                cursor.execute("""
                    INSERT INTO user_recommendations 
                    (user_id, recommended_products, last_updated, loaded_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    doc['user_id'], doc['recommended_products'], doc['last_updated']
                ))
        
        elif collection_name == 'ModerationQueue':
            for doc in transformed_docs:
                cursor.execute("""
                    INSERT INTO moderation_queue 
                    (review_id, user_id, product_id, review_text, rating, moderation_status, flags, submitted_at, loaded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    doc['review_id'], doc['user_id'], doc['product_id'], doc['review_text'],
                    doc['rating'], doc['moderation_status'], doc['flags'], doc['submitted_at']
                ))
        
        conn.commit()
        logger.info(f"Загружено {len(transformed_docs)} документов в {table_name}")
        
        cursor.close()
        conn.close()
        mongo_client.close()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке {collection_name}: {str(e)}")
        raise

with DAG(
    'mongodb_to_postgres_replication',
    default_args=default_args,
    description='Репликация данных из MongoDB в PostgreSQL',
    schedule_interval=None,
    catchup=False,
    tags=['mongodb', 'postgres', 'replication'],
) as dag:
    
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    
    tasks = []
    for collection in COLLECTIONS:
        task = PythonOperator(
            task_id=f'process_{collection}',
            python_callable=process_collection,
            op_kwargs={'collection_name': collection},
            trigger_rule='all_done'
        )
        tasks.append(task)
        
        start >> task
        task >> end