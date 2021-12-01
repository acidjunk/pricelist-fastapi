sam validate
sam build --use-container --debug
sam package --s3-bucket fastapi-pricelist-backend-staging --output-template-file out.yml --region eu-central-1
sam deploy --template-file out.yml --stack-name fastapi-pricelist-backend-staging --region eu-central-1 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
