import json
import logging
import boto3
import uuid

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

lambda_client = boto3.client('lambda')
required_fields = set(['payment_method', 'payment_id', 'payment_secret'])


def init_logger():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


@xray_recorder.capture('validate')
def validate(message):
    fields = [f for f in message.__dict__ if not f.startswith('_')]
    assert len(required_fields.intersection(fields)) >= len(required_fields), 'Validation failed: some fields are missing.'


def make_response(response_code=200, payload=None):
    return {
            "statusCode": response_code,
            "headers": {
                "x-custom-header": "my custom header value"
            },
            "body": json.dumps(payload or {})
        }


def handle_request(event, context):
    try:
        init_logger()
        validate(event.get('body'))
        return make_response(200, {'payment_id': uuid.uuid4()})
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f'generic exception: {err_msg}')
        return {
            "statusCode": 500,
            "body": json.dumps({"result": f'{ex.__class__.__name__}: {err_msg}'})
        }