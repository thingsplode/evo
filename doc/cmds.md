```bash
pushd venv/lib/python3.7/site-packages && zip -r9 ../../../../order_service.zip . && popd && zip -g order_service.zip order_service/service.py
zip -g order_service.zip order_service/*
```


```bash
aws lambda create-function --function-name order_service \ 
--zip-file fileb://order_service.zip \ 
--handler order_service.service.handle_request --runtime python3.7 \
--role "arn:aws:iam::307733074768:role/lambda_executor" \
--environment Variables="{inventory_service=inventory_service}"
```

```bash
aws lambda update-function-code --function-name order_service --zip-file fileb://order_service.zip
```

```bash
aws lambda publish-version --function-name order_service
aws lambda create-alias --function-name order_service --name dev --function-version 1   
```

```bash
aws lambda create-alias --function-name inventory_service --name dev --function-version "\$LATEST"
```