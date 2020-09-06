from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 tests=[],
                 redshift_conn_id='',
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.tests=tests
        self.redshift_conn_id=redshift_conn_id

    def execute(self, context):
        self.log.info("Data quality Check Started")
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        for test in self.tests:
            results=redshift.get_records(test['query'])
            num_records = results[0][0]
            if num_records != test['expected_result'] :
                raise ValueError(f"Data quality check failed.")
            self.log.info(f"Data quality Check passed for table.")
        