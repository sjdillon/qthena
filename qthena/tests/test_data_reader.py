#!python
# ==========================================================#
# project        :sjdillon
# title          :test_data_reader.py
# description    :unit test qthena
# author         :sjdillon
# date           :08/26/2019
# python_version :3.7
# notes          :
# ==========================================================#
import logging
import os
import qthena.athena_data_reader as data_access

logging.basicConfig(format="%(asctime)s - %(thread)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_event():
    """
    creates an event for unit tests
    :return: dict
    """
    os.environ['region'] = 'us-west-2'
    os.environ['profile'] = 'default'
    os.environ['prefix1'] = 'sjd'
    os.environ['prefix2'] = 'illon'
    os.environ['env'] = 'dev'
    prefix1 = os.environ['prefix1']
    prefix2 = os.environ['prefix2']
    env = os.environ['env']
    region = os.environ['region']

    event = dict()
    event['region'] = os.environ['region']
    # 0 sleep for mocked unit tests
    event['sleep_seconds'] = 0
    bucket_format = "s3-{prefix1}-{prefix2}-{env}-{region}-data"
    event['bucket'] = bucket_format.format(prefix1=prefix1,
                                           prefix2=prefix2,
                                           env=env,
                                           region=region)
    event['s3_query_results_path'] = "awsathenadata/queryresults"
    return event


generic_event = create_event()


def is_uuid(uuid):
    """
    Check if value is a proper uuid
    :param uuid: string to check
    :return: bool
    """
    import re
    UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    if UUID_PATTERN.match(uuid):
        return True
    return False


def run_data_access_run_query(event=generic_event, mode='playback'):
    """
    Test running a query against athena
    :param event: generic event with aws env details
    :param mode: boto aws client or mocked client
    :return: assert
    """
    # GIVEN an event
    if mode:
        event['mock_mode'] = mode
        event['mock_data_path'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_data')
        event['debug'] = False
    # WHEN we run a query using a CommandRunner
    runner = data_access.CommandRunner(event, bucket=event['bucket'],
                                       s3_query_results_path=event['s3_query_results_path'])
    results = runner.run_query('show databases')
    # THEN we get a uuid returned
    assert len(results) == 36
    assert is_uuid(results)


def run_data_access_select(event=generic_event, mode='playback'):
    """
    Test running a select returning data
    :param event: generic event with aws env details
    :param mode: boto aws client or mocked client
    :return: assert
    """
    # GIVEN an event
    if mode:
        event['mock_mode'] = mode
        event['mock_data_path'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_data')
        event['debug'] = False
    # WHEN we run a select using a CommandRunner
    runner = data_access.CommandRunner(event,
                                       bucket=event['bucket'],
                                       s3_query_results_path=event['s3_query_results_path'])
    results = runner.select('show databases', to_list=True)
    logger.info(results)
    # THEN we get a list of results
    assert results
    assert isinstance(results, list)


def run_data_access_select_w_bucket(event=generic_event, mode='playback'):
    """
    Test running a select with a bucket specified
    :param event: generic event with aws env details
    :param mode: boto aws client or mocked client
    :return: assert
    """
    # GIVEN an event that overrides the default bucket
    event['bucket'] = "s3-sjd-illon-integ-us-west-2-data"
    if mode:
        event['mock_mode'] = mode
        event['mock_data_path'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_data')
        event['debug'] = False
    # WHEN we run a select using a CommandRunner
    runner = data_access.CommandRunner(event, bucket=event['bucket'],
                                       s3_query_results_path=event['s3_query_results_path'])
    results = runner.select('show databases', to_list=True)
    logger.info(results)
    # THEN we get a list of results
    assert results
    assert isinstance(results, list)


def test_data_access_run_query(params=generic_event, mode='playback'):
    run_data_access_run_query(params, mode)


def test_data_access_select_w_bucket(params=generic_event, mode='playback'):
    run_data_access_select_w_bucket(params, mode)


def test_data_access_select(params=generic_event, mode='playback'):
    run_data_access_select(params, mode)


def test_results_to_list():
    """
    Test results_to_list helper function
    :return:list
    """
    # GIVEN a dictionary resultset from athena
    resultset = {'ResultSet': {'Rows': [{'Data': [{'VarCharValue': 'athena'}]}],
                               'ResultSetMetadata': {'ColumnInfo': [
                                   {'CatalogName': 'hive',
                                    'SchemaName': '',
                                    'TableName': '',
                                    'Name': 'database_name',
                                    'Label': 'database_name',
                                    'Type': 'string', 'Precision': 0, 'Scale': 0, 'Nullable': 'UNKNOWN',
                                    'CaseSensitive': False}]}}}
    # WHEN we convert to a list
    results = data_access.results_to_list(resultset)
    # THEN a list is returned
    assert isinstance(results, list)
