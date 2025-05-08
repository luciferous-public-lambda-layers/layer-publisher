from __future__ import annotations

import json
import os
from enum import Enum
from hashlib import sha3_224
from typing import TYPE_CHECKING

import boto3
from humps import pascalize
from pydantic import BaseModel

from layer_publisher.utils.models import BuildConfig, Layer
from layer_publisher.utils.s3 import generate_bucket_name

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sts import STSClient


class Architecture(Enum):
    AMD = "Amd"
    ARM = "Arm"
    NONE = ""


class DescriptionData(BaseModel):
    identifier: str
    hash: str
    packages: str
    note: str | None = None


sts: STSClient = boto3.client("sts")
s3: S3Client = boto3.client("s3")


def main():
    account_id = get_account_id()
    region = load_region()
    bucket_name = generate_bucket_name(account_id=account_id, region=region)
    create_bucket(bucket_name=bucket_name, region=region)

    # generate sam template
    layer = Layer.load()
    config = BuildConfig.load()
    target_runtimes = filter_runtimes(
        all_runtimes=config.runtimes, ignore_versions=layer.get_ignore_versions()
    )
    desc_data = calc_description_data(layer=layer)
    all_architectures = calc_architectures(
        is_architecture_split=layer.isArchitectureSplit
    )
    sam = generate_template(
        all_architectures=all_architectures,
        target_runtimes=target_runtimes,
        desc_data=desc_data,
    )

    with open("sam.yml", "w") as f:
        f.write(sam)

    script = generate_script(bucket_name=bucket_name, identifier=desc_data.identifier)

    with open("deploy.sh", "w") as f:
        f.write(script)


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


def filter_runtimes(
    *, all_runtimes: list[str], ignore_versions: list[str]
) -> list[str]:
    return [x for x in all_runtimes if x not in ignore_versions]


def calc_description_data(*, layer: Layer) -> DescriptionData:
    data = {
        "identifier": layer.identifier,
        "packages": ", ".join(layer.packages),
    }

    if layer.note:
        data["note"] = layer.note

    text = json.dumps(data, ensure_ascii=False)
    encoded = sha3_224(text.encode()).hexdigest()
    return DescriptionData(hash=encoded, **data)


def calc_architectures(*, is_architecture_split: bool) -> list[Architecture]:
    if is_architecture_split:
        return [Architecture.AMD, Architecture.ARM]
    else:
        return [Architecture.NONE]


def generate_logical_name_suffix(*, arch: Architecture, runtime: str) -> str:
    return "{runtime}{arch}".format(
        arch=arch.value, runtime=pascalize(runtime).replace(".", "")
    )


def generate_logical_name_layer(*, arch: Architecture, runtime: str) -> str:
    return f"Layer{generate_logical_name_suffix(arch=arch, runtime=runtime)}"


def _generate_layer_content_uri(*, arch: Architecture, runtime: str) -> list[str]:
    return [
        "      ContentUri: modules/{arch}/{runtime}".format(
            arch="arm" if arch == Architecture.ARM else "amd", runtime=runtime
        )
    ]


def _generate_layer_layer_name(
    *, identifier: str, arch: Architecture, runtime: str
) -> list[str]:
    return [
        "      LayerName: LuciferousPublicLayer{pascalized_identifier}{suffix}".format(
            pascalized_identifier=pascalize(identifier),
            suffix=generate_logical_name_suffix(arch=arch, runtime=runtime),
        )
    ]


def _generate_layer_compatible_architectures(*, arch: Architecture) -> list[str]:
    mapping = {
        Architecture.ARM.name: ["        - arm64"],
        Architecture.AMD.name: ["        - x86_64"],
        Architecture.NONE.name: ["        - arm64", "        - x86_64"],
    }
    return ["      CompatibleArchitectures:"] + mapping[arch.name]


def _generate_layer_compatible_runtimes(*, runtime: str) -> list[str]:
    return ["      CompatibleRuntimes:", "        - {runtime}".format(runtime=runtime)]


def _generate_layer_description(*, desc_data: DescriptionData) -> list[str]:
    lines = [
        "      Description: |",
        "        identifier=== {}".format(desc_data.identifier),
        "        hash=== {}".format(desc_data.hash),
        "        packages=== {}".format(desc_data.packages),
    ]
    if desc_data.note:
        lines.append(f"        note=== {desc_data.note}")
    return lines


def generate_layer(
    *, arch: Architecture, runtime: str, desc_data: DescriptionData
) -> list[str]:
    # modules/<{amd, arm}>/<{python3.13, python3.12}>/python
    lines = [
        "  {}:".format(generate_logical_name_layer(arch=arch, runtime=runtime)),
        "    Type: AWS::Serverless::LayerVersion",
        "    Properties:",
        "      RetentionPolicy: Retain",
    ]
    lines += _generate_layer_content_uri(arch=arch, runtime=runtime)
    lines += _generate_layer_layer_name(
        identifier=desc_data.identifier, arch=arch, runtime=runtime
    )
    lines += _generate_layer_compatible_architectures(arch=arch)
    lines += _generate_layer_compatible_runtimes(runtime=runtime)
    lines += _generate_layer_description(desc_data=desc_data)
    lines += [""]
    return lines


def _generate_permission_logical_name(*, arch: Architecture, runtime: str) -> list[str]:
    return [f"  Permission{generate_logical_name_suffix(arch=arch, runtime=runtime)}:"]


def _generate_permission_layer_version_arn(
    *, arch: Architecture, runtime: str
) -> list[str]:
    return [
        "      LayerVersionArn: !Ref {logical_name}".format(
            logical_name=generate_logical_name_layer(arch=arch, runtime=runtime)
        )
    ]


def generate_permission(*, arch: Architecture, runtime: str):
    lines = _generate_permission_logical_name(arch=arch, runtime=runtime)
    lines += [
        "    Type: AWS::Lambda::LayerVersionPermission",
        "    DeletionPolicy: Retain",
        "    UpdateReplacePolicy: Retain",
        "    Properties:",
        "      Action: lambda:GetLayerVersion",
        "      Principal: '*'",
    ]
    lines += _generate_permission_layer_version_arn(arch=arch, runtime=runtime)
    lines += [""]
    return lines


def generate_template(
    *,
    all_architectures: list[Architecture],
    target_runtimes: list[str],
    desc_data: DescriptionData,
) -> str:
    lines = ["Transform: AWS::Serverless-2016-10-31", "Resources:"]

    for arch in all_architectures:
        for runtime in target_runtimes:
            lines += generate_layer(arch=arch, runtime=runtime, desc_data=desc_data)
            lines += generate_permission(arch=arch, runtime=runtime)

    return "\n".join(lines)


def generate_script(*, bucket_name: str, identifier: str) -> str:
    return "\n".join(
        [
            "aws cloudformation package --s3-bucket {bucket_name} --template-file sam.yml --output-template-file template.yml".format(
                bucket_name=bucket_name
            ),
            "sam deploy --stack-name Layer{pascalize_identifier} --template-file template.yml".format(
                pascalize_identifier=pascalize(identifier)
            ),
        ]
    )


if __name__ == "__main__":
    main()
