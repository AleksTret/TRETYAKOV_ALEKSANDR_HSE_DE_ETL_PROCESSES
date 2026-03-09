"""
DAG для создания аналитических витрин в PostgreSQL
Полное перестроение витрин при каждом запуске
"""

from datetime import datetime, timedelta
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=10),
}

def create_user_activity_mart():
    """Создание витрины активности пользователей"""
    logger = logging.getLogger(__name__)
    logger.info("Начало создания витрины user_activity_mart")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_etl')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        # Проверка существования сырой таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_sessions'
            )
        """)
        if not cursor.fetchone()[0]:
            raise AirflowException("Таблица user_sessions не существует")
        
        # Создание витрины если не существует
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_mart (
                date DATE NOT NULL,
                total_sessions INTEGER NOT NULL,
                unique_users INTEGER NOT NULL,
                avg_session_duration_minutes NUMERIC(10,2),
                top_pages JSONB,
                top_actions JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Очистка витрины
        cursor.execute("TRUNCATE TABLE user_activity_mart")
        logger.info("Витрина user_activity_mart очищена")
        
        # Заполнение витрины
        cursor.execute("""
            WITH session_stats AS (
                SELECT 
                    DATE(start_time) as session_date,
                    COUNT(*) as total_sessions,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(EXTRACT(EPOCH FROM (end_time - start_time)) / 60) as avg_duration_minutes
                FROM user_sessions
                GROUP BY DATE(start_time)
            ),
            page_stats AS (
                SELECT 
                    DATE(s.start_time) as session_date,
                    p.page as page,
                    COUNT(*) as page_count
                FROM user_sessions s,
                    LATERAL unnest(s.pages_visited) as p(page)
                GROUP BY DATE(s.start_time), p.page
            ),
            top_pages_agg AS (
                SELECT 
                    session_date,
                    jsonb_agg(
                        jsonb_build_object('page', page, 'count', page_count)
                        ORDER BY page_count DESC
                    ) as top_pages
                FROM (
                    SELECT DISTINCT ON (session_date) 
                        session_date,
                        page,
                        page_count
                    FROM page_stats
                    ORDER BY session_date, page_count DESC
                    LIMIT 5
                ) t
                GROUP BY session_date
            ),
            action_stats AS (
                SELECT 
                    DATE(s.start_time) as session_date,
                    a.action as action,
                    COUNT(*) as action_count
                FROM user_sessions s,
                    LATERAL unnest(s.actions) as a(action)
                GROUP BY DATE(s.start_time), a.action
            ),
            top_actions_agg AS (
                SELECT 
                    session_date,
                    jsonb_agg(
                        jsonb_build_object('action', action, 'count', action_count)
                        ORDER BY action_count DESC
                    ) as top_actions
                FROM (
                    SELECT DISTINCT ON (session_date) 
                        session_date,
                        action,
                        action_count
                    FROM action_stats
                    ORDER BY session_date, action_count DESC
                    LIMIT 5
                ) t
                GROUP BY session_date
            )
            INSERT INTO user_activity_mart 
            (date, total_sessions, unique_users, avg_session_duration_minutes, top_pages, top_actions)
            SELECT 
                s.session_date,
                s.total_sessions,
                s.unique_users,
                ROUND(s.avg_duration_minutes::numeric, 2),
                COALESCE(p.top_pages, '[]'::jsonb),
                COALESCE(a.top_actions, '[]'::jsonb)
            FROM session_stats s
            LEFT JOIN top_pages_agg p ON s.session_date = p.session_date
            LEFT JOIN top_actions_agg a ON s.session_date = a.session_date
            ORDER BY s.session_date DESC
        """)
        
        conn.commit()
        
        # Проверка результата
        cursor.execute("SELECT COUNT(*) FROM user_activity_mart")
        count = cursor.fetchone()[0]
        logger.info(f"Витрина user_activity_mart создана, загружено {count} записей")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Ошибка при создании user_activity_mart: {str(e)}")
        raise

def create_support_tickets_mart():
    """Создание витрины эффективности поддержки"""
    logger = logging.getLogger(__name__)
    logger.info("Начало создания витрины support_tickets_mart")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_etl')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        # Проверка существования сырой таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'support_tickets'
            )
        """)
        if not cursor.fetchone()[0]:
            raise AirflowException("Таблица support_tickets не существует")
        
        # Создание витрины если не существует
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets_mart (
                status VARCHAR(20) NOT NULL,
                ticket_count INTEGER NOT NULL,
                avg_resolution_hours NUMERIC(10,2),
                issue_type_breakdown JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Очистка витрины
        cursor.execute("TRUNCATE TABLE support_tickets_mart")
        logger.info("Витрина support_tickets_mart очищена")
        
        # Заполнение витрины
        cursor.execute("""
            WITH ticket_stats AS (
                SELECT 
                    status,
                    COUNT(*) as ticket_count,
                    AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 3600) as avg_hours
                FROM support_tickets
                GROUP BY status
            ),
            issue_type_breakdown AS (
                SELECT 
                    status,
                    jsonb_object_agg(
                        issue_type,
                        ticket_count
                    ) as issue_types
                FROM (
                    SELECT 
                        status,
                        issue_type,
                        COUNT(*) as ticket_count
                    FROM support_tickets
                    GROUP BY status, issue_type
                ) t
                GROUP BY status
            )
            INSERT INTO support_tickets_mart 
            (status, ticket_count, avg_resolution_hours, issue_type_breakdown)
            SELECT 
                s.status,
                s.ticket_count,
                ROUND(s.avg_hours::numeric, 2),
                COALESCE(i.issue_types, '{}'::jsonb)
            FROM ticket_stats s
            LEFT JOIN issue_type_breakdown i ON s.status = i.status
            ORDER BY s.ticket_count DESC
        """)
        
        conn.commit()
        
        # Проверка результата
        cursor.execute("SELECT COUNT(*) FROM support_tickets_mart")
        count = cursor.fetchone()[0]
        logger.info(f"Витрина support_tickets_mart создана, загружено {count} записей")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Ошибка при создании support_tickets_mart: {str(e)}")
        raise

with DAG(
    'analytics_marts',
    default_args=default_args,
    description='Создание аналитических витрин',
    schedule_interval=None,
    catchup=False,
    tags=['analytics', 'marts', 'postgres'],
) as dag:
    
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    
    user_activity_task = PythonOperator(
        task_id='create_user_activity_mart',
        python_callable=create_user_activity_mart,
        trigger_rule='all_done'
    )
    
    support_tickets_task = PythonOperator(
        task_id='create_support_tickets_mart',
        python_callable=create_support_tickets_mart,
        trigger_rule='all_done'
    )
    
    start >> [user_activity_task, support_tickets_task] >> end