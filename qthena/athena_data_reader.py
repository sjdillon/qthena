#!python
# ==========================================================#
# title          :athena_data_access.py
# description    :handles getting data from aws athena
# author         :sjdillon
# date           :08/27/2019
# python_version :3.7
# ==========================================================================
import logging
import time
import qthena.boto_manager as bm
import qthena.config as config

logging.basicConfig(format="%(asctime)s - %(thread)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CommandRunner:
    """ Executes commands against AWS Athena """

    def __init__(self, event, bucket, s3_query_results_path):
        if 'debug' in event and event['debug'] is True:
            self._set_logger(logging.DEBUG)
        self.event = event
        self.bucket = bucket
        self.s3_query_results_path = s3_query_results_path
        self.event['service'] = 'athena'
        self.client = self.get_client()
        self.load_config()
        if 'db' in event:
            self.database_name = event['db']
        else:
            self.database_name = 'default'
        if 'sleep_seconds' in event:
            logger.info('overriding sleep_seconds')
            self.sleep_seconds = event['sleep_seconds']
        self.s3_output = 's3://{bucket}/{s3_query_results_path}/'.format(bucket=self.bucket,
                                                                         s3_query_results_path=self.s3_query_results_path)

    def _set_logger(self, level=logging.INFO):
        logger.setLevel(level)

    def get_client(self, service=None):
        """ get boto client for service """
        event = self.event
        if service:
            event['service'] = service
        bc = bm.BotoClientManager(event)
        return bc.get_client()

    def load_config(self):
        for k, v in list(config._CONFIG.items()):
            setattr(self, k, v)
        return self

    def run_query(self, query):
        """
         start an athena query and return query id
        :param query:query string to run againstathena
        :return:uuid
        """
        if "create database" in query.lower():
            database_name = 'default'
        else:
            database_name = self.database_name
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database_name},
            ResultConfiguration={'OutputLocation': self.s3_output, })
        logger.info('execution_id: {}, query: {}'.format(response['QueryExecutionId'], query))
        return response['QueryExecutionId']

    def get_results(self, quid):
        """
        get the records for the query executed
        :param quid:query execution id
        :return:dict resultset
        """
        response = self.client.get_query_results(QueryExecutionId=quid)
        logger.info(response)
        return response

    def get_query_state(self, query_id):
        """
        check to see if the query is running, failed or completed
        :param query_id:query execution id
        :return:dict with status info on success/failure and details
        """
        response = self.client.get_query_execution(QueryExecutionId=query_id)
        status = response['QueryExecution']['Status']['State']
        results = {'status': status}
        if status == 'SUCCEEDED':
            results['run_time_ms'] = response['QueryExecution']['Statistics']['EngineExecutionTimeInMillis']
            results['bytes_scanned'] = response['QueryExecution']['Statistics']['DataScannedInBytes']
        if status == 'FAILED':
            results['error'] = response['QueryExecution']['Status']['StateChangeReason']
        logger.info(results)
        return results

    def wait_for_query(self, quid):
        """
        wait for query to complete - used for synchronous execution
        :param quid: query execution id
        :return:bool
        """
        sleep_seconds = self.sleep_seconds
        while True:
            response = self.get_query_state(query_id=quid)
            status = response['status']
            logger.info('query status: {} '.format(status))
            if status in ['SUCCEEDED']:
                return True
            elif status in ['RUNNING', 'QUEUED']:
                logger.info('sleeping - ({}) seconds'.format(sleep_seconds))
                time.sleep(sleep_seconds)
            elif status in ['FAILED']:
                logger.error(response['error'])
                return False
            else:
                return False

    def run_dml(self, query):
        """
         run query and return dataset
        :param query:query string to run against athena
        :return:dict resultset
        """
        quid = self.run_query(query)
        self.wait_for_query(quid)
        results = self.get_results(quid)
        logger.debug(results)
        return results

    def select(self, query, to_list=False):
        """
        Runs a command and returns resultset
        :param query:query string to pass to athena
        :param to_list:bool- return list if True, dict if False
        :return:dict or list resultset
        """
        if to_list:
            return results_to_list(self.run_dml(query))
        return self.run_dml(query)

    def run_ddl(self, ddl):
        """
        run a command and return success or failure state
        :param ddl: command to run against athena
        :return:dict with status info on success/failure and details
        """
        quid = self.run_query(ddl)
        self.wait_for_query(quid)
        results = self.get_query_state(quid)
        logger.info(results)
        return results


# # generic helpers
def results_to_list(results):
    """
    convert api response to a list
    :param results:dict resultset form athena
    :return:list
    """
    columns = [
        col['Label']
        for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    listed_results = []
    for res in results['ResultSet']['Rows'][0:]:
        values = []
        for field in res['Data']:
            try:
                values.append(list(field.values())[0])
            except Exception:
                values.append(list(' '))
        listed_results.append(dict(list(zip(columns, values))))
    return listed_results
