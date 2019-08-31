# qthena
[![Build Status](https://travis-ci.org/sjdillon/qthena.svg?branch=master)](https://travis-ci.org/sjdillon/qthena)

**qthena** helps getting data from aws athena.

* `athena_data_access.py` -- main class and helper functions for querying athena
* `boto_manager.py` -- creates and manages boto sessions and clients, allows mocking playback and recording.  Used in the unit tests.

# What does qthena mean?
- **"q"** - query
- **"thena"** - as in _a_**thena**
- it has nothing to do with queues

# Requirements
- Python 3.7

# Quick start
Install qthena 

`$ pip install git+https://github.com/sjdillon/qthena.git`

Set up credentials (in e.g. ~/.aws/credentials):

```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET`
```

set up a default region (in e.g. ~/.aws/config):
```buildoutcfg
[default]
region=us-east-1
```


# Usage
- running a `show databases` query
```
import qthena
import os

def create_event():
    """
    creates an event for unit tests
    :return: dict
    """
    prefix1 = 'sjd'
    prefix2 = 'illon'
    env = 'dev'
    region = 'us-west-2'

    event = dict()
    event['region'] ='us-west-2'
    event['sleep_seconds'] = 0
    bucket_format = "s3-{prefix1}-{prefix2}-{env}-{region}-data"
    event['bucket'] = bucket_format.format(prefix1=prefix1,
                                           prefix2=prefix2,
                                           env=env,
                                           region=region)
    event['s3_query_results_path'] = "awsathenadata/queryresults"
    return event

# create an event with parameters
event = create_event()

# create a runner
runner = qthena.CommandRunner(event, event['bucket'], event['s3_query_results_path'])

# run a query
q = 'show databases'
results = runner.select(q, to_list=True)

for r in results:
    print(r)

```
## logs
```
2019-08-26 19:59:49,272 - 16340 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2019-08-26 19:59:49,372 - 16340 - INFO - overriding sleep_seconds
2019-08-26 19:59:50,056 - 16340 - INFO - execution_id: 4fbfe579-6a2e-4917-b579-4246818cad74, query: show databases
2019-08-26 19:59:50,189 - 16340 - INFO - {'status': 'RUNNING'}
2019-08-26 19:59:50,190 - 16340 - INFO - query status: RUNNING 
2019-08-26 19:59:50,190 - 16340 - INFO - sleeping - (5) seconds
2019-08-26 19:59:55,324 - 16340 - INFO - {'status': 'SUCCEEDED', 'run_time_ms': 276, 'bytes_scanned': 0}
2019-08-26 19:59:55,325 - 16340 - INFO - query status: SUCCEEDED 
2019-08-26 19:59:55,580 - 16340 - INFO - {'UpdateCount': 0, 'ResultSet': {'Rows': [{'Data': [{'VarCharValue': 'athena'}]}, {'Data': [{'VarCharValue': 'default'}]}, {'Data': [{'VarCharValue': 'product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_dev_product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_abc_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_abc_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_123'}]}, {'Data': [{'VarCharValue': 'test_database'}]}], 'ResultSetMetadata': {'ColumnInfo': [{'CatalogName': 'hive', 'SchemaName': '', 'TableName': '', 'Name': 'database_name', 'Label': 'database_name', 'Type': 'string', 'Precision': 0, 'Scale': 0, 'Nullable': 'UNKNOWN', 'CaseSensitive': False}]}}, 'ResponseMetadata': {'RequestId': 'e1e56dc5-10b1-4101-91cc-a3e82a5b145a', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Mon, 26 Aug 2019 23:59:54 GMT', 'x-amzn-requestid': 'e1e56dc5-10b1-4101-91cc-a3e82a5b145a', 'content-length': '1379', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
```
## output
```
16
```

# DataFrame example
- run query and convert to a pandas dataframe

`pip install pandas`

```
import pandas as pd

# helper function
def results_to_df(results):
    """
    convert athena api response to a dataframe
    :param results:dict resultset form athena
    :return:pandas dataframe
    """
    columns = [
        col['Label']
        for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    listed_results = []
    for res in results['ResultSet']['Rows'][1:]:
        values = []
        for field in res['Data']:
            try:
                values.append(list(field.values())[0])
            except Exception:
                values.append(list(' '))
        listed_results.append(dict(list(zip(columns, values))))
    return pd.DataFrame(listed_results)

# run a query against Athena
q = "select * from sjd_abc_dev.delta limit 6"
results = runner.select(q,to_list=False)

# convert results to a dataframe
df=results_to_df(results)

print (df[['vid','sid','pid','hit','miss']])`
```

## Output

```
	vid sid         pid	hit	miss
0	5	store9876	114	3	2
1	5	store9876	116	2	3
2	5	store9876	111	0	5
3	5	store9876	88	0	5
4	5	store9876	111	2	3
5	5	store9876	114	3	2
```


# Run the tests
Install pytest 

`$ pip install pytest` 

clone the project 

`$ pip install  git+https://github.com/sjdillon/qthena.git`

`cd qthena`

Run the tests

`$ pytest -sv `

Output
```buildoutcfg pytest output
platform linux -- Python 3.6.7, pytest-5.1.2, py-1.8.0, pluggy-0.12.0 -- /home/sjdillon/venv/py3/bin/python3
cachedir: .pytest_cache
rootdir: /home/sjdillon/tmp/qthena, inifile: pytest.ini
collected 4 items                                                                                                                                                                                          

qthena/tests/test_data_reader.py::test_data_access_run_query 2019-08-30 21:00:43,382 - 140057934497600 - INFO - playing back mock boto calls from /home/sjdillon/tmp/qthena/qthena/tests/mock_data
2019-08-30 21:00:43,388 - 140057934497600 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2019-08-30 21:00:43,415 - 140057934497600 - INFO - overriding sleep_seconds
2019-08-30 21:00:43,416 - 140057934497600 - INFO - execution_id: 78f29963-e1c6-4ebf-be7a-b9066b0448c2, query: show databases
PASSED
qthena/tests/test_data_reader.py::test_data_access_select_w_bucket 2019-08-30 21:00:43,429 - 140057934497600 - INFO - playing back mock boto calls from /home/sjdillon/tmp/qthena/qthena/tests/mock_data
2019-08-30 21:00:43,431 - 140057934497600 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2019-08-30 21:00:43,444 - 140057934497600 - INFO - overriding sleep_seconds
2019-08-30 21:00:43,444 - 140057934497600 - INFO - execution_id: 78f29963-e1c6-4ebf-be7a-b9066b0448c2, query: show databases
2019-08-30 21:00:43,445 - 140057934497600 - INFO - {'status': 'RUNNING'}
2019-08-30 21:00:43,445 - 140057934497600 - INFO - query status: RUNNING 
2019-08-30 21:00:43,445 - 140057934497600 - INFO - sleeping - (0) seconds
2019-08-30 21:00:43,445 - 140057934497600 - INFO - {'status': 'RUNNING'}
2019-08-30 21:00:43,445 - 140057934497600 - INFO - query status: RUNNING 
2019-08-30 21:00:43,445 - 140057934497600 - INFO - sleeping - (0) seconds
2019-08-30 21:00:43,446 - 140057934497600 - INFO - {'status': 'SUCCEEDED', 'run_time_ms': 324, 'bytes_scanned': 0}
2019-08-30 21:00:43,446 - 140057934497600 - INFO - query status: SUCCEEDED 
2019-08-30 21:00:43,446 - 140057934497600 - INFO - {'UpdateCount': 0, 'ResultSet': {'Rows': [{'Data': [{'VarCharValue': 'athena'}]}, {'Data': [{'VarCharValue': 'default'}]}, {'Data': [{'VarCharValue': 'product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_dev_product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_illon_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_illon_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_123'}]}, {'Data': [{'VarCharValue': 'test_database'}]}], 'ResultSetMetadata': {'ColumnInfo': [{'CatalogName': 'hive', 'SchemaName': '', 'TableName': '', 'Name': 'database_name', 'Label': 'database_name', 'Type': 'string', 'Precision': 0, 'Scale': 0, 'Nullable': 'UNKNOWN', 'CaseSensitive': False}]}}, 'ResponseMetadata': {'RequestId': 'b2fd6fe3-6262-48d7-b84a-d62dabada848', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Mon, 26 Aug 2019 17:53:52 GMT', 'x-amzn-requestid': 'b2fd6fe3-6262-48d7-b84a-d62dabada848', 'content-length': '1379', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
2019-08-30 21:00:43,446 - 140057934497600 - INFO - [{'database_name': 'athena'}, {'database_name': 'default'}, {'database_name': 'product'}, {'database_name': 'sjd_athena_dev_product'}, {'database_name': 'sjd_athena_integ_product'}, {'database_name': 'sjd_ops_product'}, {'database_name': 'sjd_illon_integ_product'}, {'database_name': 'sjd_illon_ops_product'}, {'database_name': 'sjd_123'}, {'database_name': 'test_database'}]
PASSED
qthena/tests/test_data_reader.py::test_data_access_select 2019-08-30 21:00:43,458 - 140057934497600 - INFO - playing back mock boto calls from /home/sjdillon/tmp/qthena/qthena/tests/mock_data
2019-08-30 21:00:43,460 - 140057934497600 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
2019-08-30 21:00:43,472 - 140057934497600 - INFO - overriding sleep_seconds
2019-08-30 21:00:43,473 - 140057934497600 - INFO - execution_id: 78f29963-e1c6-4ebf-be7a-b9066b0448c2, query: show databases
2019-08-30 21:00:43,473 - 140057934497600 - INFO - {'status': 'RUNNING'}
2019-08-30 21:00:43,473 - 140057934497600 - INFO - query status: RUNNING 
2019-08-30 21:00:43,473 - 140057934497600 - INFO - sleeping - (0) seconds
2019-08-30 21:00:43,474 - 140057934497600 - INFO - {'status': 'RUNNING'}
2019-08-30 21:00:43,474 - 140057934497600 - INFO - query status: RUNNING 
2019-08-30 21:00:43,474 - 140057934497600 - INFO - sleeping - (0) seconds
2019-08-30 21:00:43,474 - 140057934497600 - INFO - {'status': 'SUCCEEDED', 'run_time_ms': 324, 'bytes_scanned': 0}
2019-08-30 21:00:43,474 - 140057934497600 - INFO - query status: SUCCEEDED 
2019-08-30 21:00:43,475 - 140057934497600 - INFO - {'UpdateCount': 0, 'ResultSet': {'Rows': [{'Data': [{'VarCharValue': 'athena'}]}, {'Data': [{'VarCharValue': 'default'}]}, {'Data': [{'VarCharValue': 'product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_dev_product'}]}, {'Data': [{'VarCharValue': 'sjd_athena_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_illon_integ_product'}]}, {'Data': [{'VarCharValue': 'sjd_illon_ops_product'}]}, {'Data': [{'VarCharValue': 'sjd_123'}]}, {'Data': [{'VarCharValue': 'test_database'}]}], 'ResultSetMetadata': {'ColumnInfo': [{'CatalogName': 'hive', 'SchemaName': '', 'TableName': '', 'Name': 'database_name', 'Label': 'database_name', 'Type': 'string', 'Precision': 0, 'Scale': 0, 'Nullable': 'UNKNOWN', 'CaseSensitive': False}]}}, 'ResponseMetadata': {'RequestId': 'b2fd6fe3-6262-48d7-b84a-d62dabada848', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Mon, 26 Aug 2019 17:53:52 GMT', 'x-amzn-requestid': 'b2fd6fe3-6262-48d7-b84a-d62dabada848', 'content-length': '1379', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}
2019-08-30 21:00:43,475 - 140057934497600 - INFO - [{'database_name': 'athena'}, {'database_name': 'default'}, {'database_name': 'product'}, {'database_name': 'sjd_athena_dev_product'}, {'database_name': 'sjd_athena_integ_product'}, {'database_name': 'sjd_ops_product'}, {'database_name': 'sjd_illon_integ_product'}, {'database_name': 'sjd_illon_ops_product'}, {'database_name': 'sjd_123'}, {'database_name': 'test_database'}]
PASSED
qthena/tests/test_data_reader.py::test_results_to_list PASSED

============================================================================================ 4 passed in 0.22s =============================================================================================
(py3) sjdillon@sjdillon-UX331UA:~/tmp/qthena$ 


```