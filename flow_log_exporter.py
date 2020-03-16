"""
Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Chris McHenry"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

import boto3
import json
import os
from datetime import datetime, timedelta

BUCKET_NAME = os.getenv('BUCKET_NAME')
LOG_GROUP_NAME = os.getenv('LOG_GROUP_NAME')

def lambda_handler(event, context):
    #Get previous recent sync
    print('Loading previous sync time...')
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=BUCKET_NAME,Key='latest_export.json')
        latest_export_time = json.loads(obj['Body'].read())[0]
        print('Latest export time:'+str(latest_export_time))
    except s3.exceptions.NoSuchKey:
        print('No existing latest export time.  Setting time to 30 minutes ago.')
        latest_export_time = 0

    backup_ts = int((datetime.now()-timedelta(minutes=30)).strftime("%s"))*1000
    latest_export_time = max(backup_ts,latest_export_time)

    client = boto3.client('logs')

    response = client.describe_log_streams(
        logGroupName=LOG_GROUP_NAME,
        orderBy='LastEventTime',
        descending=True,
        limit=1000
    )

    latest_log_time = 0

    for log_stream in response['logStreams']:
        if log_stream['lastEventTimestamp'] > latest_log_time:
            latest_log_time = log_stream['lastEventTimestamp']
    
    print('Latest log time:'+str(latest_log_time))

    if latest_log_time > latest_export_time:
        print('Creating export task')
        response = client.create_export_task(
            taskName='test_export_'+str(latest_log_time),
            logGroupName=LOG_GROUP_NAME,
            fromTime=latest_export_time,
            to=latest_log_time,
            destination=BUCKET_NAME
        )
        print(response)
        print('Updating latest export time')
        print(json.dumps([latest_log_time]))
        s3.put_object(Body=json.dumps([latest_log_time]), Bucket=BUCKET_NAME, Key='latest_export.json')
    else:
        print('Up to date!')
    

#lambda_handler(1,1)