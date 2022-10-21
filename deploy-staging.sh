sam validate --template-file template-staging.yml
sam build --template-file template-staging.yml --use-container --debug
#sam package --s3-bucket api-staging-prijslijst-info --template-file template-staging.yml --output-template-file out.yml --region eu-central-1
#sam deploy --template-file out.yml --stack-name api-staging-prijslijst-info --region eu-central-1 --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
