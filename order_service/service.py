import json
import logging
import os
import boto3
import traceback
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])
lambda_client = boto3.client('lambda')

log_level = os.environ.get('LOG_LEVEL', logging.INFO)
inventory_service_name = os.environ.get('inventory_service', 'inventory_service')
payment_service_name = os.environ.get('payment_service', 'payment_service')
shipping_service_name = os.environ.get('shipping_service', 'shipping_service')
required_fields = set(['product_id', 'qty', 'amount', 'currency', 'payment_method', 'payment_tool_id', 'payment_secret'])


def init_logger():
    global logger
    logger = logging.getLogger()
    logging.getLogger('aws_xray_sdk').setLevel(logging.WARNING)
    logger.setLevel(log_level)


@xray_recorder.capture('make_response')
def make_response(response_code=200, payload=None):
    return {
        "statusCode": response_code,
        "headers": {
            "x-custom-header": "my custom header value",
            'Content-Type': 'application/json'
        },
        "body": json.dumps(payload or {})
    }


@xray_recorder.capture('validate')
def validate(message):
    fields = [f for f in message if not f.startswith('_')]
    assert len(required_fields.intersection(fields)) >= len(
        required_fields), 'Validation failed: some fields are missing.'


@xray_recorder.capture('reserve')
def reserve(request, stage):
    reservation_response = lambda_client.invoke(FunctionName=f'{inventory_service_name}:{stage}',
                                                InvocationType='RequestResponse',
                                                LogType='Tail',
                                                Payload=json.dumps({
                                                    'operation': 'reservation',
                                                    'product_id': request.get('product_id'),
                                                    'qty': request.get('qty')
                                                }))
    logger.debug(f'-  reservation response -> ${reservation_response}')
    payload = json.loads(reservation_response['Payload'].read())
    logger.info(f' - reservation payload [type{type(payload)}] -> {payload}')
    return payload.get('statusCode') if 'statusCode' in payload else 500, payload


@xray_recorder.capture('payment')
def payment(request, stage):
    payment_response = lambda_client.invoke(FunctionName=f'{payment_service_name}:{stage}',
                                            InvocationType='RequestResponse',
                                            LogType='Tail',
                                            Payload=json.dumps(request))
    logger.debug(f'-  payment response -> ${payment_response}')
    payload = json.loads(payment_response['Payload'].read())
    logger.info(f'payment payload => {payload}')
    return payload.get('statusCode') if 'statusCode' in payload else 500, payload


@xray_recorder.capture('shipment')
def ship_it(request, stage):
    lambda_client.invoke(FunctionName=f'{shipping_service_name}:{stage}',
                         InvocationType='Event',
                         LogType='Tail',
                         Payload=json.dumps(request))


def handle_request(event, context):
    try:
        init_logger()
        stage = event.get('requestContext').get('stage', '$LATEST')
        request = json.loads(event.get('body'))
        validate(request)
        reservation_code, rsp = reserve(request, stage)
        if reservation_code > 299:
            return make_response(reservation_code, rsp.get('body'))

        reservation_id = rsp.get('body').get('reservation_id')
        pmt_code, pmt_rsp = payment({'reservation_id': reservation_id,
                                     'amount': request.get('amount'),
                                     'currency': request.get('currency'),
                                     'payment_tool_id': request.get('payment_tool_id'),
                                     'payment_secret': request.get('payment_secret')
                                     }, stage)

        if pmt_code > 299:
            return make_response(pmt_code, rsp.get('body'))

        ship_it({'reservation_id': reservation_id}, stage)
        return {
            "statusCode": 201,
            "headers": {
                "x-stage": stage
            },
            "body": json.dumps({
                "result": "OK",
                "reservation_id": reservation_id,
                "payment_id": pmt_rsp.get('body').get('payment_id')
            })
        }
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f'{ex.__class__.__name__}: {err_msg}')
        traceback.print_exc()
        return make_response(500, {"result@order": f'{ex.__class__.__name__}: {err_msg}'})
