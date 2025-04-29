from __future__ import annotations

import os
from typing import TYPE_CHECKING

import boto3

from layer_publisher.utils.s3 import generate_bucket_name

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket, S3ServiceResource
    from mypy_boto3_sts import STSClient


sts: STSClient = boto3.client("sts")
s3: S3ServiceResource = boto3.resource("s3")


def main():
    account_id = get_account_id()
    region = load_region()
    name_bucket = generate_bucket_name(account_id=account_id, region=region)
    bucket: Bucket = s3.Bucket(name_bucket)
    bucket.objects.all().delete()
    bucket.delete()


def get_account_id():
    resp = sts.get_caller_identity()
    return resp["Account"]


def load_region():
    return os.environ["AWS_REGION"]


if __name__ == "__main__":
    main()
