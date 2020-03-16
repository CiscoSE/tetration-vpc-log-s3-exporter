# Tetration S3 Log Exporter
Lambda function to create a recurring S3 export task for VPC flow logs to be consumed by Tetration

## Overview
Tetration supports ingesting VPC Flow Logs to assist in policy discovery, simulation and compliance alerting for endpoints in AWS that cannot have a Tetration agent installed.  In the current release of Tetration Software (3.3.x) the workflow is as follows.

1. Create a VPC Flow Log configuration to export logs to Cloudwatch
2. Create a CloudWatch task to export a specific time period of logs to an S3 bucket
3. Tetration downloads and reads the discrete export and processes the flows.

For this to be a recurring event, export tasks will need to be created on a regular basis to export logs to S3.  This can be done automatically with a script.  This repository contains a function that can be run in AWS as a Lambda.

## Permissions
The Lambda function must have the appropriate rights to create an export task for the specific CloudWatch stream.  It must also have Read-Write capabiliies to the target S3 Bucket.

## How the Lambda Function Works
On execution the function:
1. Reads an environment variable which tell it which CloudWatch stream to create an export task
2. Reads an environment variable which tell it which S3 bucket to export to
3. Reads a file in the S3 bucket that determines when the last time a successful export was completed
4. Checks the CloudWatch stream to see if any new data has arrived since the last successful export
5. If new data has arrived, it initiates an export task to export the new VPC Flow Log data to the S3 bucket
6. If the export task is successfully created, it updates the S3 file with a new timestamp for the most recent export

## Files
* LICENSE - This repository leverages the Cisco Sample Code license, and should be used for reference purposes only
* flow_log_exporter.py - Python function that can be run in Lambda to initiate 

## Environment Variables
* BUCKET_NAME - The name of the target S3 bucket. This should match the configuration in Tetration for where it is attempting to download S3 Flow Logs
* LOG_GROUP_NAME - The name of the CloudWatch Log Group Name for the VPC Flow Logs

## Pre-requisites
This function only leverage libraries that are already present in the default Lambda Python 3.x environemnt, so the file can simply be cut and paste into the Lambda UI in AWS console and no packaging is required.

## Tips
* Use CloudWatch events to schedule a recuring Lambda execution similar to cron on Linux.
* There is no reason this function couldn't also be used on any machine that can schedule execution of a Python script as a recurring task.
* Make sure to configure the Environment variables in Lambda appropriately
* In Lambda, the boto3 library for accessing the AWS APIs inherits the permissions of the role applied to the Lambda function.  If the function fails, ensure that it has appropriate permissions.
