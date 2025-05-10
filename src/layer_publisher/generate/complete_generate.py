from __future__ import annotations

import json
from datetime import datetime
from glob import glob
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import boto3
from pydantic import BaseModel
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class EnvironmentVariables(BaseSettings):
    table_name: str
    identifier: str
    bucket_name_layers_data: str


class Layer(BaseModel):
    identifier: str
    hash: str
    packages: str
    note: str | None = None
    runtime: str
    architectures: list[str]
    layer_version_arn: str
    created_at: str
    region: str


jst = ZoneInfo("Asia/Tokyo")
env = EnvironmentVariables()

table: Table = boto3.resource("dynamodb").Table(env.table_name)


def main():
    aggregate_layers()
    update_state()


def list_files() -> list[str]:
    return sorted(glob("layers/**/*.json", recursive=True))


def convert_data(*, layer: dict, region: str) -> Layer:
    description: str = layer["Description"]
    data = {}
    for line in description.split("\n"):
        if not line:
            continue
        key, value = line.split("=== ")
        data[key] = value
    return Layer(
        runtime=layer["CompatibleRuntimes"][0],
        architectures=layer["CompatibleArchitectures"],
        layer_version_arn=layer["LayerVersionArn"],
        created_at=layer["CreatedDate"],
        region=region,
        **data,
    )


def load_layers(*, all_files: list[str]) -> list[Layer]:
    result = []

    for path in all_files:
        with open(path) as f:
            data = json.load(f)
        result += [convert_data(layer=x, region=data["region"]) for x in data["layers"]]

    return result


def aggregate_layers():
    all_files = list_files()
    all_layers = load_layers(all_files=all_files)
    with open("all_layers.json", "w") as f:
        json.dump(all_layers, f, indent=2, ensure_ascii=False)


def update_state():
    dt_text = datetime.now(jst).isoformat()
    attributes = {
        "stateGenerate": "PUBLISHED",
        "updatedAt": dt_text,
        "lastGeneratedAt": dt_text,
    }
    resp = table.update_item(
        Key={"identifier": env.identifier},
        UpdateExpression="set "
        + ", ".join([f"#{k} = :{k}" for k in attributes.keys()]),
        ExpressionAttributeNames={f"#{k}": k for k in attributes.keys()},
        ExpressionAttributeValues={f":{k}": v for k, v in attributes.items()},
        ReturnValues="ALL_NEW",
    )
    print("=== updated item ===")
    print(
        json.dumps(
            resp,
            indent=2,
            ensure_ascii=False,
            default=lambda x: {"type": str(type(x)), "value": str(x)},
        )
    )


if __name__ == "__main__":
    main()
