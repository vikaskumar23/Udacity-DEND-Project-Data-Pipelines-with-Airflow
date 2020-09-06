from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries


default_args = {
    'owner': 'sparkify',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}

data_quality_checks=[{'query':'select count(*) from users where userid is null','expected_result':0},
          {'query':'select count(*) from songs where songid is null','expected_result':0},
          {'query':'select count(*) from songs where artistid is null','expected_result':0}]

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          catchup=False,
          schedule_interval='0 * * * *'
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

create_tables = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='redshift',
    dag=dag,
    sql="create_tables.sql",
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    table='public.staging_events',
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    json_paths='log_json_path.json',
    s3_bucket='udacity-dend',
    s3_key='log_data'
)


stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    table='public.staging_songs',
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    s3_bucket='udacity-dend',
    s3_key='song_data'
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    table='public.songplays',
    redshift_conn_id='redshift',
    sql=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='public.users',
    append_mode=False,
    sql=SqlQueries.user_table_insert
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='public.songs',
    append_mode=False,
    sql=SqlQueries.song_table_insert
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='public.artists',
    append_mode=False,
    sql=SqlQueries.artist_table_insert
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='public.time',
    append_mode=False,
    sql=SqlQueries.time_table_insert
)



run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    tests=data_quality_checks,
    redshift_conn_id='redshift'
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> create_tables
create_tables >> [stage_events_to_redshift, stage_songs_to_redshift]
[stage_events_to_redshift, stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_user_dimension_table,
                        load_song_dimension_table,
                        load_artist_dimension_table,
                        load_time_dimension_table]

[load_user_dimension_table,
 load_song_dimension_table,
 load_artist_dimension_table,
 load_time_dimension_table] >> run_quality_checks

run_quality_checks >> end_operator