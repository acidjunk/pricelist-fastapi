sam validate --template-file template-production.yml
sam build --template-file template-production.yml --use-container --debug
sam package --s3-bucket api-production-prijslijst-info --template-file template-production.yml --output-template-file out.yml --region eu-central-1
sam deploy --template-file out.yml --stack-name api-production-prijslijst-info --region eu-central-1 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
