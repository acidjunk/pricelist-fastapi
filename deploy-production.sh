cp template-production.yml template.yml 
sam validate
sam build --use-container --debug
sam package --s3-bucket api-production-prijslijst-info --output-template-file out.yml --region eu-central-1
sam deploy --template-file out.yml --stack-name api-production-prijslijst-info --region eu-central-1 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
