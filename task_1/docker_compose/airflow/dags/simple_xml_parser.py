# airflow/dags/simple_xml_parser.py
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    'simple_xml_parser',
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    
    parse_xml = PostgresOperator(
        task_id='extract_xml_data',
        postgres_conn_id='postgres_default',
        sql="""
            TRUNCATE TABLE nutrition_flat, daily_values;
            
            WITH data AS (
                SELECT xml_data FROM raw_nutrition_xml
            )
            INSERT INTO daily_values (nutrient, daily_value, units)
            SELECT 
                unnest(ARRAY['total-fat', 'saturated-fat', 'cholesterol', 'sodium', 'carb', 'fiber', 'protein']),
                unnest(xpath('/nutrition/daily-values/*/text()', (SELECT xml_data FROM data)))::text::decimal,
                unnest(xpath('/nutrition/daily-values/*/@units', (SELECT xml_data FROM data)))::text;
            
            INSERT INTO nutrition_flat (
                food_name, manufacturer, serving_size, serving_units,
                calories_total, calories_fat, total_fat, saturated_fat,
                cholesterol, sodium, carbs, fiber, protein,
                vitamin_a, vitamin_c, calcium, iron
            )
            SELECT 
                (xpath('/food/name/text()', food))[1]::text,
                (xpath('/food/mfr/text()', food))[1]::text,
                (xpath('/food/serving/text()', food))[1]::text,
                (xpath('/food/serving/@units', food))[1]::text,
                (xpath('/food/calories/@total', food))[1]::text::int,
                (xpath('/food/calories/@fat', food))[1]::text::int,
                (xpath('/food/total-fat/text()', food))[1]::text::decimal,
                (xpath('/food/saturated-fat/text()', food))[1]::text::decimal,
                (xpath('/food/cholesterol/text()', food))[1]::text::int,
                (xpath('/food/sodium/text()', food))[1]::text::int,
                (xpath('/food/carb/text()', food))[1]::text::decimal,
                (xpath('/food/fiber/text()', food))[1]::text::decimal,
                (xpath('/food/protein/text()', food))[1]::text::decimal,
                (xpath('/food/vitamins/a/text()', food))[1]::text::int,
                (xpath('/food/vitamins/c/text()', food))[1]::text::int,
                (xpath('/food/minerals/ca/text()', food))[1]::text::int,
                (xpath('/food/minerals/fe/text()', food))[1]::text::int
            FROM raw_nutrition_xml,
                 unnest(xpath('/nutrition/food', xml_data)) as food;
        """
    )
    
    parse_xml