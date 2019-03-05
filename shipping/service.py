import json
import logging
import os
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])


lambda_client = boto3.client('lambda')
inventory_service_name = os.environ['inventory_service']
required_fields = set(['reservation_id'])


def init_logger():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


@xray_recorder.capture('validate')
def validate(message):
    fields = [f for f in message if not f.startswith('_')]
    assert len(required_fields.intersection(fields)) >= len(
        required_fields), 'Validation failed: some fields are missing.'


def handle_request(event, context):
    try:
        init_logger()
        validate(event.get('body'))
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f'generic exception: {err_msg}')
        return {
            "statusCode": 500,
            "body": json.dumps({"result@shipping": f'{ex.__class__.__name__}: {err_msg}'})
        }
