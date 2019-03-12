# evo
serverless evolutionary architectures


## Try it out
calling via curl
```bash
curl -i -X POST \
   -H "Content-Type:application/json" \
   -H "x-api-key:some-api-key" \
   -d \
'{
    "user_id":"1234",
    "product_id":"234",
    "qty":"2",
    "amount":"30",
    "currency":"EUR",
    "payment_method":"CARD",
    "payment_tool_id":"1234",
    "payment_secret":"123"
}' \
 'https://some-hash.execute-api.eu-west-1.amazonaws.com/dev/order'
```
