from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
import os
import glob

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

UPLOAD_DIR = '/opt/airflow/data/upload'
MAIN_CSV = 'iot-temp.csv'

def inc_extract(**context):
    all_files = glob.glob(os.path.join(UPLOAD_DIR, '*.csv'))
    new_files = [f for f in all_files if os.path.basename(f).lower() != MAIN_CSV.lower()]
    
    if not new_files:
        context['ti'].xcom_push(key='has_data', value=False)
        return 0
    
    dfs = [pd.read_csv(f) for f in new_files]
    df = pd.concat(dfs, ignore_index=True)
    
    temp_path = f"/tmp/inc_data_{context['ds_nodash']}.parquet"
    df.to_parquet(temp_path, index=False)
    
    context['ti'].xcom_push(key='has_data', value=True)
    context['ti'].xcom_push(key='data_path', value=temp_path)
    return len(df)

def inc_load(**context):
    ti = context['ti']
    has_data = ti.xcom_pull(key='has_data', task_ids='inc_extract')
    
    if not has_data:
        return
    
    temp_path = ti.xcom_pull(key='data_path', task_ids='inc_extract')
    df = pd.read_parquet(temp_path)
    
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    df.to_sql('iot_temp_raw', engine, if_exists='append', index=False)
    
    os.remove(temp_path)

def inc_transform(**context):
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    
    query = """
        SELECT * FROM iot_temp_raw 
        WHERE TO_TIMESTAMP(noted_date, 'DD-MM-YYYY HH24:MI') > 
              COALESCE((SELECT MAX(event_time) FROM iot_temp_clean), '1900-01-01')
    """
    raw_df = pd.read_sql(query, engine)
    
    if raw_df.empty:
        return
    
    df = raw_df[raw_df['out/in'] == 'In'].copy()
    df['event_time'] = pd.to_datetime(df['noted_date'], format='%d-%m-%Y %H:%M')
    df['noted_date'] = df['event_time'].dt.date
    df = df.drop_duplicates(subset=['id', 'room_id/id', 'noted_date', 'temp', 'out/in'])
    
    df[['id', 'room_id/id', 'noted_date', 'event_time', 'temp', 'out/in']].to_sql(
        'iot_temp_clean', engine, if_exists='append', index=False
    )

def inc_calc(**context):
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/data_warehouse')
    df = pd.read_sql('SELECT * FROM iot_temp_clean', engine)
    
    daily = df.groupby('noted_date')['temp'].max().reset_index()
    hottest = daily.nlargest(5, 'temp').copy()
    hottest['type'] = 'hottest'
    coldest = daily.nsmallest(5, 'temp').copy()
    coldest['type'] = 'coldest'
    
    result = pd.concat([hottest, coldest])
    result.to_sql('iot_temp_hot_cold_days', engine, if_exists='replace', index=False)

def archive_files(**context):
    ti = context['ti']
    has_data = ti.xcom_pull(key='has_data', task_ids='inc_extract')
    
    if not has_data:
        return
    
    import shutil
    STORAGE_DIR = '/opt/airflow/data/storage'
    
    all_files = glob.glob(os.path.join(UPLOAD_DIR, '*.csv'))
    new_files = [f for f in all_files if not f.endswith(MAIN_CSV)]
    
    for f in new_files:
        name = os.path.basename(f)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{os.path.splitext(name)[0]}_{ts}.csv"
        dest = os.path.join(STORAGE_DIR, new_name)
        shutil.move(f, dest)

with DAG(
    'iot_temp_incremental_load',
    default_args=default_args,
    description='Инкрементальная загрузка',
    schedule_interval=None,
    catchup=False,
    tags=['iot', 'incremental'],
) as dag:
    
    start = DummyOperator(task_id='start')
    
    extract = PythonOperator(
        task_id='inc_extract',
        python_callable=inc_extract,
        provide_context=True,
    )
    
    load = PythonOperator(
        task_id='inc_load',
        python_callable=inc_load,
        provide_context=True,
    )
    
    transform = PythonOperator(
        task_id='inc_transform',
        python_callable=inc_transform,
        provide_context=True,
    )
    
    calc = PythonOperator(
        task_id='inc_calc',
        python_callable=inc_calc,
        provide_context=True,
    )
    
    archive = PythonOperator(
        task_id='archive',
        python_callable=archive_files,
        provide_context=True,
    )
    
    end = DummyOperator(task_id='end')
    
    start >> extract >> load >> transform >> calc >> archive >> end