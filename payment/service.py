import json
import logging
import boto3
import uuid
import traceback

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

lambda_client = boto3.client('lambda')
function_name = None
required_fields = set(['payment_id', 'payment_secret'])


def init_logger():
    global logger
    logger = logging.getLogger()
    logging.getLogger('aws_xray_sdk').setLevel(logging.WARNING)
    logger.setLevel(logging.INFO)


@xray_recorder.capture('validate')
def validate(message):
    fields = [f for f in message if not f.startswith('_')]
    assert len(required_fields.intersection(fields)) >= len(required_fields), 'Validation failed: some fields are missing.'


def make_response(response_code=200, payload=None):
    return {
            "statusCode": response_code,
            "headers": {
                "x-source": function_name
            },
            # "body": json.dumps(payload or {})
            "body": payload or {}
        }


def handle_request(event, context):
    try:
        init_logger()
        global function_name
        function_name = context.function_name
        logger.info(f'incoming event {event}')
        validate(event)
        return make_response(200, {'payment_id': str(uuid.uuid4())})
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f'generic exception: {err_msg}')
        traceback.print_exc()
        return make_response(500, {"result@payment": f'{ex.__class__.__name__}: {err_msg}'})
