import os
import shutil
import sys
import logging
import boto3
import structlog
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from pydantic.networks import PostgresDsn
from contextlib import closing

REGION_NAME = "eu-central-1"
# Assuming: "staging" env =>
# api-staging-prijslijst-info
ENV_PREFIX = "api-"
ENV_SUFFIX = "-prijslijst-info"

logger = structlog.get_logger(__name__)

# Todo's
#- try to be describing about how trhis script should be used
#- there are a couple of names that will be generated: it would be nice to have them in the log
#- fix script for prod (and template also)

def env_database_uri():
    if (env_var := os.environ.get("DATABASE_URI")) is not None:
        print("Skipping database creation: DATABASE_URI env variable provided.")
        return str(make_url(env_var)) or None


def db_uri(new_db_name):
    try:
        database_uri = PostgresDsn.build(
            scheme="postgresql",
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_SERVER"),
            path=f"/{new_db_name or ''}",
        )
        url = make_url(database_uri)
        return url
    except TypeError as e:
        print("Try checking you env variables.")
        logging.error(e)


# NOTE: Needs a little change for SQLAlchemy 1.4
def create_db(new_db_name):
    url = db_uri(new_db_name)
    str_url = str(url)
    db_to_create = url.database
    url.database = "postgres"
    engine = create_engine(url)

    with closing(engine.connect()) as conn:
        conn.execute("COMMIT;")
        if conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_to_create}'").rowcount > 0:
            print("Skipping database creation: Database with this name already exists.")
        else:
            print(f"Database {db_to_create} created successfully.")
        # conn.execute("COMMIT;")
        # conn.execute(f'CREATE DATABASE "{db_to_create}";')
    return str_url


def create_bucket(s3_client, new_bucket_name, region):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    logger.info("creating new S3 bucket", bucket_name=new_bucket_name)
    try:
        if region is None:
            s3_client.create_bucket(Bucket=new_bucket_name)
        else:
            location = {"LocationConstraint": region}
            s3_client.create_bucket(Bucket=new_bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def deploy(new_bucket_name, environment_name, db_conn_str):
    stack_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
    logger.info("Determined stack_name", stack_name=stack_name)
    try:
        BASE_PATH = "."
        # BUILD_DIR = "%s/%s" % (BASE_PATH, ".aws-sam/build")
        #
        # if not os.path.exists(BUILD_DIR):
        #     os.mkdir(BUILD_DIR)

        os.system("cd %s && sam validate" % (BASE_PATH))
        os.system("cd %s && sam build --use-container --debug" % (BASE_PATH))
        os.system(
            "cd %s && sam package --s3-bucket %s --output-template-file out.yml --region %s"
            % (BASE_PATH, new_bucket_name, REGION_NAME)
        )
        os.system(
            "cd %s && sam deploy --template-file out.yml --stack-name %s --region %s --no-fail-on-empty-changeset "
            "--capabilities CAPABILITY_IAM" % (BASE_PATH, stack_name, REGION_NAME)
        )
        os.system(
            "cd %s && aws lambda get-function-configuration --function-name %s --region %s"
            % (BASE_PATH, stack_name, REGION_NAME)
        )

        # Todo: extract to a separate function that can handle setting env vars
        os.system(
            'cd %s && aws lambda update-function-configuration --function-name %s --region %s --environment "Variables={DATABASE_URI=%s}"'
            % (BASE_PATH, stack_name, REGION_NAME, db_conn_str)
        )

    except Exception as e:
        print(e)
        sys.exit(1)


def main(environment_name):
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=REGION_NAME,
    )

    create_new_s3_bucket = True
    new_bucket_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
    existing_buckets = client.list_buckets()

    for bucket in existing_buckets["Buckets"]:
        if bucket["Name"] == new_bucket_name:
            create_new_s3_bucket = False
    if create_new_s3_bucket:
        create_bucket(client, new_bucket_name, REGION_NAME)
    else:
        logger.info("Skipping bucket creation as it already exists")

    # db_conn_str = env_database_uri() or create_db(environment_name)
    # deploy(new_bucket_name, environment_name, db_conn_str)


def check_aws_tooling():
    return shutil.which("aws") is not None


if __name__ == "__main__":
    load_dotenv()
    args = sys.argv

    if len(args) <= 1:
        logger.error("Please provide a full env name")
        sys.exit()

    logger.info("Starting deployment for env", env=args[1])
    if not check_aws_tooling():
        logger.error("No AWS CLI found")
        sys.exit()
    main(environment_name=args[1])
