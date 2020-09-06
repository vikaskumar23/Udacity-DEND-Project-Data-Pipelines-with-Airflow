from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id='',
                 table='',
                 append_mode=False,
                 sql='',
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id=redshift_conn_id
        self.table=table
        self.append_mode=append_mode
        self.sql=sql

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        if not self.append_mode:
            self.log.info(f"Clearing data from destination Redshift table {self.table}")
            redshift.run("DELETE FROM {}".format(self.table))
        redshift.run("INSERT INTO {} {}".format(self.table,self.sql))
        self.log.info(f"Data successfully inserted into {self.table}")
