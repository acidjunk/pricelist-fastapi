#!/usr/bin/env python3

# Copyright 2019-2022 Formatics.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -----------------------------------------------------------------------------
# USAGE/INSTRUCTIONS:
# -----------------------------------------------------------------------------
# This script can be used to setup the needed AWS Lambda Environment variables.
#
# You'll need a python with these packages to use the script:
# pydantic, pydantic, boto3, aws-sam-cli
#
#

import os
import shutil
import sys

REGION_NAME = "eu-central-1"
ENV_PREFIX = "api-"
ENV_SUFFIX = "-prijslijst-info"
ENV_VARS = [
    "ENVIRONMENT",
    "TESTING",
    "DATABASE_URI",
    "SESSION_SECRET",
    "JWT_ALGORITHM",
    "IMAGE_S3_ACCESS_KEY_ID",
    "IMAGE_S3_SECRET_ACCESS_KEY",
    "LAMBDA_ACCESS_KEY_ID",
    "LAMBDA_SECRET_ACCESS_KEY",
    "FIRST_SUPERUSER",
    "FIRST_SUPERUSER_PASSWORD",
]


def return_lambda_env_var(name, value):
    return f"{name}={value}"


def check_environment_before_deploy():
    for env in ENV_VARS:
        if not os.getenv(env):
            print(f"Please Ensure all needed ENV vars are inited. Could not find: {env}")
            print(
                "Hint; when using this by hand you can probably load the env vars with: "
                "'export $(cat env_staging | grep -v ^# | xargs)'"
            )
            sys.exit(1)


def check_aws_tooling():
    return shutil.which("aws") is not None


check_environment_before_deploy()
environment_name = sys.argv[1]
stack_name = f"{ENV_PREFIX}{environment_name}{ENV_SUFFIX}"
print(f"Derived stack name: {stack_name}")


envs = [return_lambda_env_var(env, os.getenv(env)) for env in ENV_VARS]
cmd = (
    f"aws lambda update-function-configuration --function-name {stack_name} "
    f'--region {REGION_NAME} --environment "Variables={{{",".join(envs)}}}"'
)
print(f"Executing CMD:\n{cmd}")
os.system(cmd)