import json
import logging
import boto3
import uuid
import traceback
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

lambda_client = boto3.client('lambda')


def init_logger():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


@xray_recorder.capture('validate')
def validate(message, required_fields):
    fields = [f for f in message if not f.startswith('_')]
    assert len(required_fields.intersection(fields)) >= len(
        required_fields), 'Validation failed: some fields are missing.'


@xray_recorder.capture('make_response')
def make_response(response_code=200, payload=None):
    return {
        "statusCode": response_code,
        "headers": {
            "x-custom-header": "my custom header value",
            'Content-Type': 'application/json'
        },
        # "body": json.dumps(payload or {})
        "body": payload or {}
    }


@xray_recorder.capture('handle_reservation')
def handle_reservation(message):
    required_fields = set(['product_id', 'qty'])
    validate(message, required_fields)
    return make_response(200, {'reservation_id': str(uuid.uuid4())})


@xray_recorder.capture('handle_pickup')
def handle_pickup(message):
    required_fields = set(['reservation_id'])
    validate(message, required_fields)
    return make_response(200, {'reservation_id': str(uuid.uuid4())})


def handle_request(event, context):
    operations = {
        'reservation': handle_reservation,
        'pickup': handle_pickup
    }
    try:
        init_logger()
        print(f'event --> {event}')
        if isinstance(event, str):
            event = json.loads(event)
        return_message = operations.get(event.get('operation'))(event)
        return_message.get('headers')['x-inventory-version'] = context.function_version
        return return_message
    except Exception as ex:
        err_msg = str(ex)
        traceback.print_exc()
        logger.error(f'{ex.__class__.__name__}: {err_msg}')
        return make_response(500, {"result": f'{ex.__class__.__name__}: {err_msg}'})
