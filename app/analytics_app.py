import sys
import os
import json
import pandas as pd
import orders_analytics
import boto3
from io import StringIO 

"""
Modify this lambda function to perform the following questions

1. Find the most profitable Region, and its profit
2. What shipping method is most common for each Category
3. Output a glue table containing the number of orders for each Category and Sub Category
"""

s3 = boto3.client('s3')
output_bucket = os.environ['OUTPUT_BUCKET']

def get_bucket_key_from_event(event : dict) -> tuple:
    "Returns the S3 path from the lambda event record"
    bucket = event['Records'][0]['s3']['bucket']['name'] #get bucket
    key = event['Records'][0]['s3']['object']['key'] #get key
    return  bucket, key

def get_file_basename(event: dict) -> str:
    "get filename from s3 event, makes it easier to link input file to output analytics"
    key = event['Records'][0]['s3']['object']['key'] #file basename in key
    basename = os.path.basename(key) #use os basename to get filename
    return basename
    #get filename from s3 key

def get_analytics_data(df: pd.DataFrame) -> list[tuple]:
    "perform analytics, return dataframes combined with their descriptors"
    most_profitable_region_df = orders_analytics.calculate_most_profitable_region(df)
    common_ship_method_df = orders_analytics.find_most_common_ship_method(df)
    number_of_orders_df = orders_analytics.find_number_of_order_per_category(df)
    #get all the analytics dataframes

    analytics_outputs = [(most_profitable_region_df, "most_profitable_region"), 
                         (common_ship_method_df, "common_ship_method"), 
                         (number_of_orders_df, "number_of_orders")]
    #there is probably a nicer way to do this but you can add on to it fairly easily if you want to do more analytics
    return analytics_outputs

def get_filepath_and_csv(filename: str, descriptor: str, df: pd.DataFrame) -> str:
    "create csv file and return path"
    csv_path = f"/tmp/{descriptor}_{filename}" #store in /tmp for lambda
    df.to_csv(csv_path, index=False)
    return csv_path

def process_df_and_upload(df: pd.DataFrame, filename: str, descriptor: str):
    "create csv file, get path, upload to s3"
    csv_path = get_filepath_and_csv(filename, descriptor, df) 
    s3.upload_file(csv_path, output_bucket, f"analytics/{descriptor}_{filename}") #upload using path
    return

def debug_write_error_log(message: str, bucket: str, name: str):
    "write error log to s3"
    log_key = f"logs/{name}_log.txt"
    s3.put_object(Bucket=bucket, Key=log_key, Body=message)
    return


def lambda_handler(event, context):
    "Lambda function to process S3 events and perform analytics on orders data"
    debug_write_error_log(f"Successfully started lambda", os.environ['OUTPUT_BUCKET'], "start")
    try:
        bucket, key = get_bucket_key_from_event(event)
        csv_obj = s3.get_object(Bucket=bucket, Key=key) #load csv from s3
        body = csv_obj['Body'] #get csv content
        csv_string = body.read().decode('utf-8') #decode to string
        df = pd.read_csv(StringIO(csv_string)) #use StringIO to read string as file for pandas
        debug_write_error_log(f"Successfully loaded file {key} from bucket {bucket}", os.environ['OUTPUT_BUCKET'], "load")
    except Exception as e:
        print(f"ERROR processing file: {str(e)}", file=sys.stderr)
        debug_write_error_log(f"ERROR processing file {key} from bucket {bucket}: {str(e)}", os.environ['OUTPUT_BUCKET'], "load")
        return { 'status': 500, 'error': str(e) }
        #in case anything goes wrong, throw an error

    try:
        filename = get_file_basename(event)
        analytics_outputs = get_analytics_data(df) #get all the analytics dataframes and their titles

        for analytics_df, descriptor in analytics_outputs:
            process_df_and_upload(analytics_df, filename, descriptor) #process and upload each dataframe
        debug_write_error_log(f"Successfully performed analytics on file {key} from bucket {bucket}", os.environ['OUTPUT_BUCKET'], "analytics")    
        return { 'status': 200}
    except Exception as e:
        print(f"ERROR performing analytics: {str(e)}", file=sys.stderr)
        debug_write_error_log(f"ERROR performing analytics on file {key} from bucket {bucket}: {str(e)}", os.environ['OUTPUT_BUCKET'], "analytics")
        return { 'status': 500, 'error': str(e) }
    
    





