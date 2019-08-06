import os
import csv
import boto3
import pprint
import logging
import json
import decimal
from os import path

def _file_path(file_name):
    basepath = path.dirname(__file__)
    return path.abspath(path.join(basepath, file_name))

def read_to_dicts(file_name='./DDB-surveys-questions-responses.csv'):
    file_path = _file_path(file_name)

    dict_list = []
    with open(file_path, 'r') as opened_file:
        reader = csv.DictReader(opened_file)
        for line in reader:
            dict_list.append(line)
    return dict_list

def write_to_ddb(entries, table_id=None):
    dynamodb = boto3.resource('dynamodb')
    agencies_table_id = table_id or os.environ['AGENCY_TABLE_ID']
    print(f"agencies_table_id {agencies_table_id}")
    table = dynamodb.Table(agencies_table_id)

    # make floats decimals
    for entry in entries:
        for k, v in entry.items():
            if isinstance(v, float):
                entry[k] = decimal.Decimal(v)


    for entry in entries:
        item = { k:v for k,v in entry.items() if v != '' }
        table.put_item(Item=item)

if __name__ == '__main__':
    data = read_to_dicts('./DDB-surveys-questions-responses.csv')
    write_to_ddb(data)
    data = read_to_dicts('./DDB-agencies.csv')
    write_to_ddb(data)


