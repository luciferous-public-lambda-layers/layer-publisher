from __future__ import annotations

import json
from datetime import datetime
from glob import glob
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import boto3
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from layer_publisher.utils.variables import FILE_SOURCE_DATA

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

    @property
    def sort_key(self) -> tuple[float, int, str]:
        mapping_arch = {"arm64,x86_64": 0, "x86_64": 1, "arm64": 2}

        version = float("-" + self.runtime[6:])
        arch = mapping_arch[",".join(sorted(self.architectures))]
        return version, arch, self.region


class AllLayers(BaseModel):
    all_layers: list[Layer]


class TmpMapping(BaseModel):
    created_at: str
    mapping: dict[str, Layer]


class FixedClassifiedLayers(BaseModel):
    identifier: str
    latest_layers: list[Layer]
    all_layers: list[Layer]


class SourceData(BaseModel):
    layers: list[FixedClassifiedLayers]


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


def load_layers(*, all_files: list[str]) -> AllLayers:
    result: list[Layer] = []

    exclude_arns = {
        "arn:aws:lambda:ap-northeast-1:043309354008:layer:dd530c3cdd49e5bdf0fbeaf774c0c63d484250ee5ae4b101647f6757bf1e180d:3"
    }

    for path in all_files:
        with open(path) as f:
            data = json.load(f)
        result += [
            convert_data(layer=x, region=data["region"])
            for x in data["layers"]
            if x["LayerVersionArn"] not in exclude_arns
        ]

    return AllLayers(all_layers=result)


def classify_layers(*, all_layers: list[Layer]) -> dict:
    result = {}
    for layer in all_layers:
        mapping_identifier = result.get(layer.identifier, {})

        mapping_hash = mapping_identifier.get(layer.hash, {})

        arches = ", ".join(layer.architectures)
        key_region_arch = f"{layer.runtime}:{arches}:{layer.region}"

        mapping_hash[key_region_arch] = layer
        mapping_identifier[layer.hash] = mapping_hash
        result[layer.identifier] = mapping_identifier

    return result


def fix_layers_for_identifier(
    *, identifier: str, mapping_hash: dict[str, dict[str, Layer]]
) -> FixedClassifiedLayers:
    # identifier -> hash -> runtime:arches:region
    array_hash = sorted(
        [
            TmpMapping(mapping=v, created_at=max([x.created_at for x in v.values()]))
            for k, v in mapping_hash.items()
        ],
        key=lambda x: x.created_at,
        reverse=True,
    )

    result = FixedClassifiedLayers(
        identifier=identifier, latest_layers=[], all_layers=[]
    )
    for i, mapping in enumerate(array_hash):
        node = sorted(mapping.mapping.values(), key=lambda x: x.sort_key)
        if i == 0:
            result.latest_layers += node
        result.all_layers += node
    return result


def aggregate_layers():
    all_files = list_files()
    all_layers = load_layers(all_files=all_files)
    mapping_layers = classify_layers(all_layers=all_layers.all_layers)
    source_data = SourceData(
        layers=[
            fix_layers_for_identifier(identifier=k, mapping_hash=v)
            for k, v in mapping_layers.items()
        ]
    )

    with open("all_layers.json", "w") as f:
        json.dump(all_layers.model_dump(), f, indent=2, ensure_ascii=False)
    with open("single_layer.json", "w") as f:
        json.dump(
            all_layers.all_layers[0].model_dump(), f, indent=2, ensure_ascii=False
        )

    with open(FILE_SOURCE_DATA, "w") as f:
        json.dump(source_data.model_dump(), f, indent=2, ensure_ascii=False)


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
