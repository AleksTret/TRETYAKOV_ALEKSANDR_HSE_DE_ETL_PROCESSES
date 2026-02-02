# airflow/dags/iot_temp_etl.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_raw_data():
    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_conn()
    df = pd.read_sql_query("SELECT * FROM iot_temp_raw", conn)
    conn.close()
    return df

def transform_data(**context):
    ti = context['ti']
    df = ti.xcom_pull(task_ids='extract_raw_data')
    
    df = df[df['out_in'] == 'In'].copy()
    df['noted_date'] = pd.to_datetime(df['noted_date'], format='%d-%m-%Y %H:%M')
    df['noted_date_only'] = df['noted_date'].dt.date
    df['year'] = df['noted_date'].dt.year
    df['month'] = df['noted_date'].dt.month
    df['day'] = df['noted_date'].dt.day
    
    p5 = df['temp'].quantile(0.05)
    p95 = df['temp'].quantile(0.95)
    df = df[(df['temp'] >= p5) & (df['temp'] <= p95)]
    
    return df

def load_clean_data(**context):
    ti = context['ti']
    df = ti.xcom_pull(task_ids='transform_data')
    
    df_clean = df[['id', 'room_id', 'noted_date_only', 'temp', 'out_in', 'year', 'month', 'day']]
    df_clean = df_clean.rename(columns={'noted_date_only': 'noted_date'})
    
    hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = hook.get_sqlalchemy_engine()
    
    with engine.begin() as conn:
        conn.execute("TRUNCATE TABLE iot_temp_clean")
        df_clean.to_sql('iot_temp_clean', conn, if_exists='append', index=False)

def calculate_hot_cold_days(**context):
    ti = context['ti']
    df = ti.xcom_pull(task_ids='transform_data')
    
    daily_max = df.groupby('noted_date_only')['temp'].max().reset_index()
    daily_max = daily_max.rename(columns={'noted_date_only': 'noted_date'})
    
    hottest = daily_max.nlargest(5, 'temp').copy()
    hottest['ranking_type'] = 'hottest'
    hottest['rank'] = range(1, 6)
    
    coldest = daily_max.nsmallest(5, 'temp').copy()
    coldest['ranking_type'] = 'coldest'
    coldest['rank'] = range(1, 6)
    
    result = pd.concat([hottest, coldest])
    result['year'] = result['noted_date'].apply(lambda x: x.year)
    result = result.rename(columns={'temp': 'max_temp'})
    
    hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = hook.get_sqlalchemy_engine()
    
    with engine.begin() as conn:
        conn.execute("TRUNCATE TABLE iot_temp_hot_cold_days")
        result.to_sql('iot_temp_hot_cold_days', conn, if_exists='append', index=False)

with DAG(
    'iot_temp_etl',
    default_args=default_args,
    description='ETL для температурных данных IoT',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    
    extract_task = PythonOperator(
        task_id='extract_raw_data',
        python_callable=extract_raw_data,
    )
    
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )
    
    load_clean_task = PythonOperator(
        task_id='load_clean_data',
        python_callable=load_clean_data,
    )
    
    calc_hot_cold_task = PythonOperator(
        task_id='calculate_hot_cold_days',
        python_callable=calculate_hot_cold_days,
    )
    
    extract_task >> transform_task >> [load_clean_task, calc_hot_cold_task]