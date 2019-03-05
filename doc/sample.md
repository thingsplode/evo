```json
{
    "product_id":"234",
    "qty":"2",
    "amount":"30",
    "currency":"EUR",
    "payment_method":"CARD",
    "payment_id":"1234",
    "payment_secret":"123"
}
```

Incoming event:

```json
{
  "resource": "/order",
  "path": "/order",
  "httpMethod": "POST",
  "headers": null,
  "multiValueHeaders": null,
  "queryStringParameters": null,
  "multiValueQueryStringParameters": null,
  "pathParameters": null,
  "stageVariables": null,
  "requestContext": {
    "path": "/order",
    "accountId": "307733074768",
    "resourceId": "0dg0px",
    "stage": "test-invoke-stage",
    "domainPrefix": "testPrefix",
    "requestId": "a30c3b31-3f1d-11e9-ba27-d30f66b54a63",
    "identity": {
      "cognitoIdentityPoolId": null,
      "cognitoIdentityId": null,
      "apiKey": "test-invoke-api-key",
      "cognitoAuthenticationType": null,
      "userArn": "arn:aws:sts::307733074768:assumed-role/admin/csatam-Isengard",
      "apiKeyId": "test-invoke-api-key-id",
      "userAgent": "aws-internal/3 aws-sdk-java/1.11.498 Linux/4.9.137-0.1.ac.218.74.329.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.202-b08 java/1.8.0_202",
      "accountId": "307733074768",
      "caller": "AROAJ2DJRQ7HV4QRVH3Z2:csatam-Isengard",
      "sourceIp": "test-invoke-source-ip",
      "accessKey": "ASIAUPJSSCNIGASF2DUG",
      "cognitoAuthenticationProvider": null,
      "user": "AROAJ2DJRQ7HV4QRVH3Z2:csatam-Isengard"
    },
    "domainName": "testPrefix.testDomainName",
    "resourcePath": "/order",
    "httpMethod": "POST",
    "extendedRequestId": "WDwklE9DjoEFgjg=",
    "apiId": "xg240aq3he"
  },
  "body": "{\n    \"product_id\":\"234\",\n    \"qty\":\"2\",\n    \"amount\":\"30\",\n    \"currency\":\"EUR\",\n    \"payment_method\":\"CARD\",\n    \"payment_id\":\"1234\",\n    \"payment_secret\":\"123\"\n}",
  "isBase64Encoded": false
```

```json
{
  'aws_request_id': '850ec2b9-b51a-4672-ba09-40943dec49e7',
  'log_group_name': '/aws/lambda/order_service',
  'log_stream_name': '2019/03/05/[$LATEST]c961bf10e71749fb9a5b8361bfd2296a',
  'function_name': 'order_service',
  'memory_limit_in_mb': '128',
  'function_version': '$LATEST',
  'invoked_function_arn': 'arn:aws:lambda:eu-west-1:307733074768:function:order_service',
  'client_context': None,
  'identity': <bootstrap.CognitoIdentity
  object
  at
  0x7f8f5e5012b0>,
  '_epoch_deadline_time_in_ms': 1551773217120
}
```