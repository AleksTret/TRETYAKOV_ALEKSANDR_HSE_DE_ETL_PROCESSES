from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'analytics_marts',
    default_args=default_args,
    schedule_interval=None,  # Ручной запуск
    catchup=False,
    tags=['analytics', 'marts', 'postgres'],
) as dag:
    
    def create_user_activity_mart():
        # TODO: создать витрину по активности пользователей
        print("Creating user activity mart...")
        pass
    
    def create_support_tickets_mart():
        # TODO: создать витрину по тикетам поддержки
        print("Creating support tickets mart...")
        pass
    
    user_activity_task = PythonOperator(
        task_id='create_user_activity_mart',
        python_callable=create_user_activity_mart
    )
    
    support_tickets_task = PythonOperator(
        task_id='create_support_tickets_mart',
        python_callable=create_support_tickets_mart
    )
    
    [user_activity_task, support_tickets_task]