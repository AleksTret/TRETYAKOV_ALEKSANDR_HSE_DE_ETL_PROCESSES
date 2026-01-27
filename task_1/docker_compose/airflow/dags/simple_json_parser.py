# airflow/dags/simple_json_parser.py
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    'simple_json_parser',
    schedule_interval=None,  
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    
    parse_json = PostgresOperator(
        task_id='extract_json_data',
        postgres_conn_id='postgres_default',
        # Преобразование JSON в плоскую структуру
        sql="""
            TRUNCATE TABLE pets_flat;

            INSERT INTO pets_flat (name, species, fav_foods, birth_year, photo_url)
            SELECT 
                pet.value->>'name',
                pet.value->>'species',
                pet.value->>'favFoods',
                pet.value->>'birthYear',
                pet.value->>'photo'
            FROM raw_pets_json,
                 jsonb_array_elements(json_data->'pets') as pet(value);
        """
    )
    
    parse_json