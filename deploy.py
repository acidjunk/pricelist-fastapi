import os
import sys
import logging
import boto3
import yaml
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from pydantic.networks import PostgresDsn
from contextlib import closing


REGION_NAME = 'eu-central-1'
S3_BUCKET_PREFIX = 'formatics'
URL = "https://1n1v00okbh.execute-api.eu-central-1.amazonaws.com/prod"


def db_uri(new_db_name):
    try:
        database_uri = PostgresDsn.build(
            scheme="postgresql",
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_SERVER"),
            path=f"/{new_db_name or ''}"
        )
        url = make_url(database_uri)
        return url
    except TypeError as e:
        logging.error(e)

def create_db(new_db_name):
    url = db_uri(new_db_name)
    db_to_create = url.database
    url.database = "postgres"
    engine = create_engine(url)

    with closing(engine.connect()) as conn:
        conn.execute("COMMIT;")
        if conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_to_create}'").rowcount > 0:
            print("Skipping database creation: Database with this name already exists.")
        else:
            print(f"Database {db_to_create} created successfully.")
        # conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        # conn.execute("COMMIT;")
        # conn.execute(f'CREATE DATABASE "{db_to_create}";')

    return 0



def create_bucket(s3_client, new_bucket_name, region):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client.create_bucket(Bucket=new_bucket_name)
        else:
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=new_bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main(environment_name):
    client = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                          region_name=REGION_NAME)

    create_new_s3_bucket = True
    new_bucket_name = f"{S3_BUCKET_PREFIX}-{environment_name}"
    existing_buckets = client.list_buckets()

    for bucket in existing_buckets['Buckets']:
        if bucket['Name'] == new_bucket_name:
            create_new_s3_bucket = False
        print(bucket['Name'])

    if create_new_s3_bucket:
        create_bucket(client, new_bucket_name, REGION_NAME)
        print(f"S3 bucket {new_bucket_name} created successfully.")
    else:
        print("Skipping S3 Bucket creation: S3 bucket with this name already exists.")


def deploy():
    try:
        LAMBDA_S3_BUCKET = "fastapi-pricelist-backend-staging"
        API_NAME = "FastapiPricelistBackendStaging"
        BASE_PATH = "."
        STACK_NAME = "fastapi-pricelist-backend-staging"
        BUILD_DIR = "%s" % (BASE_PATH)

        if not os.path.exists(BUILD_DIR):
            os.mkdir(BUILD_DIR)

        os.system("cd %s && sam build --use-container --debug" % (BASE_PATH))
        os.system(
            "cd %s && sam package --template-file %s/template.yml --output-template-file out.yml --s3-bucket %s --region %s" % (
            BASE_PATH, BUILD_DIR, LAMBDA_S3_BUCKET, REGION_NAME))
        os.system(
            "cd %s && sam deploy --template-file out.yml --stack-name %s --capabilities CAPABILITY_IAM --region %s" % (
            BASE_PATH, STACK_NAME, REGION_NAME))

    except Exception as e:
        print(e)
        exit(1)



if __name__ == "__main__":
    load_dotenv()
    args = sys.argv
    # main(environment_name=args[1])
    # db_uri("api-staging")
    # create_db("priceliststaging")
    deploy()
