import uuid
import datetime
from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.yandex.operators.yandexcloud_dataproc import (
    DataprocCreateClusterOperator,
    DataprocCreatePysparkJobOperator,
    DataprocDeleteClusterOperator,
)

YC_DP_AZ = 'ru-central1-b'
YC_DP_SSH_PUBLIC_KEY = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHboOyrH6/xkFjrSvNpHhM8w4JO3lUaKCPqVXZ4WVU/p aleks@Mini_IT13'
YC_DP_SUBNET_ID = 'e2l27hjmntks8vk0g7tk'
YC_DP_SA_ID = 'aje6t2mcgufb243m7gjj'
YC_DP_METASTORE_URI = '10.129.0.21'
YC_BUCKET = 'kickstarter-data-bucket'

with DAG(
        'KICKSTARTER_ETL',
        schedule='@hourly',
        tags=['dataproc', 'spark'],
        start_date=datetime.datetime.now(),
        max_active_runs=1,
        catchup=False
) as dag:

    create_cluster = DataprocCreateClusterOperator(
        task_id='create_cluster',
        cluster_name=f'tmp-dp-{uuid.uuid4()}',
        ssh_public_keys=YC_DP_SSH_PUBLIC_KEY,
        service_account_id=YC_DP_SA_ID,
        subnet_id=YC_DP_SUBNET_ID,
        s3_bucket=YC_BUCKET,
        zone=YC_DP_AZ,
        cluster_image_version='2.1',
        masternode_resource_preset='s2.small',
        masternode_disk_type='network-ssd',
        masternode_disk_size=64,
        computenode_resource_preset='s2.small',
        computenode_disk_type='network-ssd',
        computenode_disk_size=64,
        computenode_count=1,
        services=['YARN', 'SPARK'],
        datanode_count=0,
        properties={
            'spark:spark.hive.metastore.uris': f'thrift://{YC_DP_METASTORE_URI}:9083',
        },
    )

    spark_job = DataprocCreatePysparkJobOperator(
        task_id='run_spark_agg',
        main_python_file_uri=f's3a://{YC_BUCKET}/scripts/spark_agg.py',
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id='delete_cluster',
        trigger_rule=TriggerRule.ALL_DONE,
    )

    create_cluster >> spark_job >> delete_cluster