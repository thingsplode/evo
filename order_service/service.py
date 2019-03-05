import json
import logging
import os
import boto3
import traceback
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

lambda_client = boto3.client('lambda')
inventory_service_name = os.environ.get('inventory_service', 'inventory_service')
payment_service_name = os.environ.get('payment_service', 'payment_service')
shipping_service_name = os.environ.get('shipping_service', 'shipping_service')
required_fields = set(['product_id', 'qty', 'amount', 'currency', 'payment_method', 'payment_id', 'payment_secret'])


def init_logger():
    global logger
    logger = logging.getLogger()
    logging.getLogger('aws_xray_sdk').setLevel(logging.WARNING)
    logger.setLevel(logging.INFO)


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
    return reservation_response


@xray_recorder.capture('payment')
def payment(request, stage):
    payment_response = lambda_client.invoke(FunctionName=f'{payment_service_name}:{stage}',
                                            InvocationType='RequestResponse',
                                            LogType='Tail',
                                            Payload=json.dumps(request))
    return payment_response


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
        reservation_response = reserve(request, stage)
        logger.debug(f'-  reservation response -> ${reservation_response}')
        rsp = json.loads(reservation_response['Payload'].read())
        logger.debug(f' - rsp [type{type(rsp)}] -> {rsp}')

        reservation_code = rsp.get('statusCode')
        if reservation_code > 299:
            return make_response(reservation_code, rsp.get('body'))

        reservation_id = rsp.get('body').get('reservation_id')
        pmt_rsp = payment({'reservation_id': reservation_id,
                           'amount': request.get('amount'),
                           'currency': request.get('currency'),
                           'payment_id': request.get('payment_id'),
                           'payment_secret': request.get('payment_secret')
                           }, stage)
        logger.debug(f'-  payment response -> ${pmt_rsp}')
        rsp = json.loads(pmt_rsp['Payload'].read())
        logger.debug(f'payload rsp => {rsp}')
        if rsp.get('statusCode') > 299:
            return make_response(rsp.get('statusCode'), rsp.get('body'))

        ship_it({'reservation_id': reservation_id}, stage)
        return {
            "statusCode": 200,
            "headers": {
                "x-stage": stage
            },
            "body": json.dumps({
                "result": "OK",
                "reservation_id": reservation_id
            })
        }
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f'{ex.__class__.__name__}: {err_msg}')
        traceback.print_exc()
        return make_response(500, {"result@order": f'{ex.__class__.__name__}: {err_msg}'})
