from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def full_extract_load():
    df = pd.read_csv('/opt/airflow/data/upload/iot-temp.csv')
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    df.to_sql('iot_temp_raw', engine, if_exists='replace', index=False)

def full_transform():
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    df = pd.read_sql('SELECT * FROM iot_temp_raw', engine)
    df = df[df['out/in'] == 'In']
    df['event_time'] = pd.to_datetime(df['noted_date'], format='%d-%m-%Y %H:%M')
    df['noted_date'] = df['event_time'].dt.date
    df = df.drop_duplicates(subset=['id', 'room_id/id', 'noted_date', 'temp', 'out/in'])
    df[['id', 'room_id/id', 'noted_date', 'event_time', 'temp', 'out/in']].to_sql(
        'iot_temp_clean', engine, if_exists='replace', index=False
    )

def full_calc():
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    df = pd.read_sql('SELECT * FROM iot_temp_clean', engine)
    daily = df.groupby('noted_date')['temp'].max().reset_index()
    hottest = daily.nlargest(5, 'temp').copy()
    hottest['type'] = 'hottest'
    coldest = daily.nsmallest(5, 'temp').copy()
    coldest['type'] = 'coldest'
    result = pd.concat([hottest, coldest])
    result.to_sql('iot_temp_hot_cold_days', engine, if_exists='replace', index=False)

with DAG(
    'iot_temp_full_load',
    default_args=default_args,
    description='Полная загрузка',
    schedule_interval=None,
    catchup=False,
    tags=['iot', 'full'],
) as dag:

    extract_load = PythonOperator(
        task_id='full_extract_load',
        python_callable=full_extract_load,
    )

    transform = PythonOperator(
        task_id='full_transform',
        python_callable=full_transform,
    )

    calc = PythonOperator(
        task_id='full_calc',
        python_callable=full_calc,
    )

    extract_load >> transform >> calc