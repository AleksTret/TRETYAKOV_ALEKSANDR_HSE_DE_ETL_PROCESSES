"""
Скрипт для генерации тестовых данных в MongoDB
"""

import random
from datetime import datetime, timedelta
from faker import Faker
import pymongo
from pymongo.errors import ConnectionFailure

# Конфигурация
MONGO_HOST = 'mongodb'
MONGO_PORT = 27017
MONGO_DB = 'test'

# Количество документов
COUNTS = {
    'UserSessions': 150,
    'EventLogs': 750,
    'SupportTickets': 40,
    'UserRecommendations': 25,
    'ModerationQueue': 50
}

# Инициализация Faker
fake = Faker('ru_RU')
fake_en = Faker('en_US')

# Возможные значения
DEVICE_TYPES = ['mobile', 'desktop', 'tablet']
ACTIONS = ['login', 'view_product', 'add_to_cart', 'remove_from_cart', 'checkout', 'logout', 'search', 'filter']
PAGES = ['/home', '/products', '/products/{id}', '/cart', '/checkout', '/profile', '/about', '/contact']
EVENT_TYPES = ['page_view', 'click', 'scroll', 'form_submit', 'error', 'api_call']
TICKET_STATUSES = ['open', 'in_progress', 'resolved', 'closed']
TICKET_ISSUE_TYPES = ['payment', 'technical', 'account', 'product', 'delivery', 'other']
MODERATION_STATUSES = ['pending', 'approved', 'rejected']
FLAGS = ['contains_images', 'contains_links', 'profanity', 'spam', 'duplicate']

def connect_to_mongodb():
    """Подключение к MongoDB"""
    try:
        client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}')
        client.admin.command('ping')
        return client[MONGO_DB]
    except ConnectionFailure as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        exit(1)

def clear_collections(db):
    """Очистка коллекций"""
    for collection in COUNTS.keys():
        db[collection].delete_many({})

def generate_user_sessions(db, num_docs):
    """Генерация сессий пользователей"""
    collection = db['UserSessions']
    users = [fake.uuid4() for _ in range(30)]
    
    sessions = []
    for _ in range(num_docs):
        user_id = random.choice(users)
        start_time = fake.date_time_between(start_date='-30d', end_date='now')
        end_time = start_time + timedelta(minutes=random.randint(1, 120))
        
        num_pages = random.randint(1, 10)
        pages = []
        for _ in range(num_pages):
            page = random.choice(PAGES)
            if '{id}' in page:
                page = page.replace('{id}', str(random.randint(1, 100)))
            pages.append(page)
        
        num_actions = random.randint(0, 8)
        session_actions = random.sample(ACTIONS, min(num_actions, len(ACTIONS)))
        
        session = {
            'session_id': f"sess_{fake.uuid4()[:8]}",
            'user_id': user_id,
            'start_time': start_time.isoformat() + 'Z',
            'end_time': end_time.isoformat() + 'Z',
            'pages_visited': pages,
            'device': random.choice(DEVICE_TYPES),
            'actions': session_actions
        }
        sessions.append(session)
    
    collection.insert_many(sessions)

def generate_event_logs(db, num_docs):
    """Генерация логов событий"""
    collection = db['EventLogs']
    
    events = []
    for _ in range(num_docs):
        timestamp = fake.date_time_between(start_date='-30d', end_date='now')
        
        event = {
            'event_id': f"evt_{fake.uuid4()[:8]}",
            'timestamp': timestamp.isoformat() + 'Z',
            'event_type': random.choice(EVENT_TYPES),
            'details': {
                'url': random.choice(PAGES).replace('{id}', str(random.randint(1, 100))),
                'user_agent': fake.user_agent(),
                'ip_address': fake.ipv4(),
                'value': random.randint(1, 1000) if random.random() > 0.7 else None
            }
        }
        events.append(event)
    
    collection.insert_many(events)

def generate_support_tickets(db, num_docs):
    """Генерация обращений в поддержку"""
    collection = db['SupportTickets']
    users = list(db['UserSessions'].distinct('user_id'))
    if not users:
        users = [fake.uuid4() for _ in range(10)]
    
    tickets = []
    for _ in range(num_docs):
        created_at = fake.date_time_between(start_date='-30d', end_date='now')
        updated_at = created_at
        if random.random() > 0.3:
            updated_at = created_at + timedelta(hours=random.randint(1, 72))
        
        num_messages = random.randint(1, 5)
        messages = []
        for i in range(num_messages):
            sender = 'user' if i == 0 else random.choice(['user', 'support'])
            messages.append({
                'sender': sender,
                'message': fake.text(max_nb_chars=200),
                'timestamp': (created_at + timedelta(hours=i*2)).isoformat() + 'Z'
            })
        
        ticket = {
            'ticket_id': f"ticket_{fake.uuid4()[:8]}",
            'user_id': random.choice(users) if users else fake.uuid4(),
            'status': random.choice(TICKET_STATUSES),
            'issue_type': random.choice(TICKET_ISSUE_TYPES),
            'messages': messages,
            'created_at': created_at.isoformat() + 'Z',
            'updated_at': updated_at.isoformat() + 'Z'
        }
        tickets.append(ticket)
    
    collection.insert_many(tickets)

def generate_user_recommendations(db, num_docs):
    """Генерация рекомендаций"""
    collection = db['UserRecommendations']
    users = list(db['UserSessions'].distinct('user_id'))
    if not users:
        users = [fake.uuid4() for _ in range(10)]
    
    unique_users = list(set(users))[:num_docs]
    
    recommendations = []
    for user_id in unique_users:
        num_products = random.randint(3, 8)
        products = [f"prod_{random.randint(100, 999)}" for _ in range(num_products)]
        
        recommendation = {
            'user_id': user_id,
            'recommended_products': products,
            'last_updated': fake.date_time_between(start_date='-7d', end_date='now').isoformat() + 'Z'
        }
        recommendations.append(recommendation)
    
    collection.insert_many(recommendations)

def generate_moderation_queue(db, num_docs):
    """Генерация очереди модерации"""
    collection = db['ModerationQueue']
    users = list(db['UserSessions'].distinct('user_id'))
    if not users:
        users = [fake.uuid4() for _ in range(10)]
    
    reviews = []
    for _ in range(num_docs):
        num_flags = random.randint(0, 3)
        review_flags = random.sample(FLAGS, min(num_flags, len(FLAGS)))
        
        review = {
            'review_id': f"rev_{fake.uuid4()[:8]}",
            'user_id': random.choice(users) if users else fake.uuid4(),
            'product_id': f"prod_{random.randint(100, 999)}",
            'review_text': fake.text(max_nb_chars=500) if random.random() > 0.2 else fake_en.text(max_nb_chars=500),
            'rating': random.randint(1, 5),
            'moderation_status': random.choice(MODERATION_STATUSES),
            'flags': review_flags,
            'submitted_at': fake.date_time_between(start_date='-30d', end_date='now').isoformat() + 'Z'
        }
        reviews.append(review)
    
    collection.insert_many(reviews)

def print_statistics(db):
    """Вывод статистики"""
    total = 0
    for collection in COUNTS.keys():
        count = db[collection].count_documents({})
        total += count
    print(f"Сгенерировано {total} документов")

def main():
    db = connect_to_mongodb()
    clear_collections(db)
    
    generate_user_sessions(db, COUNTS['UserSessions'])
    generate_event_logs(db, COUNTS['EventLogs'])
    generate_support_tickets(db, COUNTS['SupportTickets'])
    generate_user_recommendations(db, COUNTS['UserRecommendations'])
    generate_moderation_queue(db, COUNTS['ModerationQueue'])
    
    print_statistics(db)

if __name__ == "__main__":
    main()