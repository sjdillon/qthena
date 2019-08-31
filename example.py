import qthena


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
    event['region'] = 'us-west-2'
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
