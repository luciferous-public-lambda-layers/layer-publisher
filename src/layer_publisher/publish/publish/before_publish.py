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
    layer = load_layer_info()
    account_id = get_account_id()
    region = load_region()
    bucket_name = generate_bucket_name(account_id=account_id, region=region)
    if not has_target_bucket(bucket_name=bucket_name, region=region):
        pass


def load_layer_info() -> Layer:
    with open(FILE_LAYER_INFO) as f:
        return Layer(**json.load(f))


def get_account_id() -> str:
    resp = sts.get_caller_identity()
    return resp["Account"]


def load_region() -> str:
    return os.environ["AWS_REGION"]


def has_target_bucket(*, bucket_name: str, region: str) -> bool:
    all_buckets = []
    for resp in s3.get_paginator("list_buckets").paginate(BucketRegion=region):
        all_buckets += [x for x in resp.get("Buckets", [])]

    return bucket_name in all_buckets


def create_bucket(*, bucket_name: str, region: str):
    s3.create_bucket(
        Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region}
    )


if __name__ == "__main__":
    main()
