from __future__ import annotations

import json
from os import makedirs
from typing import TYPE_CHECKING

import boto3
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient


class EnvironmentVariables(BaseSettings):
    aws_default_region: str


env = EnvironmentVariables()
client: LambdaClient = boto3.client("lambda")


def main():
    path = generate_path()
    all_layer_names = list_layer_names()
    layers = list_layer_versions(all_layer_names=all_layer_names)
    with open(path, "w") as f:
        json.dump(
            {"region": env.aws_default_region, "layers": layers}, f, ensure_ascii=False
        )


def generate_path() -> str:
    dirname = f"dist/layers/{env.aws_default_region}"
    makedirs(dirname, exist_ok=True)
    return f"{dirname}/layers.json"


def list_layer_names() -> list[str]:
    result = []

    for resp in client.get_paginator("list_layers").paginate():
        result += [x["LayerName"] for x in resp["Layers"]]

    return result


def list_layer_versions(*, all_layer_names: list[str]) -> list[dict]:
    result = []

    for layer_name in all_layer_names:
        for resp in client.get_paginator("list_layer_versions").paginate(
            LayerName=layer_name
        ):
            result += [x for x in resp["LayerVersions"]]

    return result


if __name__ == "__main__":
    main()
