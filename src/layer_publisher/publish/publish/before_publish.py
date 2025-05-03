from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import boto3

from layer_publisher.utils.models import Layer
from layer_publisher.utils.s3 import generate_bucket_name
from layer_publisher.utils.variables import FILE_LAYER_INFO

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sts import STSClient


sts: STSClient = boto3.client("sts")
s3: S3Client = boto3.client("s3")


def main():
    layer = Layer.load()
    account_id = get_account_id()
    region = load_region()
    bucket_name = generate_bucket_name(account_id=account_id, region=region)
    create_bucket(bucket_name=bucket_name, region=region)


def get_account_id() -> str:
    resp = sts.get_caller_identity()
    return resp["Account"]


def load_region() -> str:
    return os.environ["AWS_REGION"]


def create_bucket(*, bucket_name: str, region: str):
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
    except (s3.exceptions.BucketAlreadyExists, s3.exceptions.BucketAlreadyOwnedByYou):
        pass


if __name__ == "__main__":
    main()
