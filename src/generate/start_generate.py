from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import boto3
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


class EnvironmentVariables(BaseSettings):
    table_name: str
    identifier: str
    url_action_run: str


jst = ZoneInfo("Asia/Tokyo")
env = EnvironmentVariables()

table: Table = boto3.resource("dynamodb").Table(env.table_name)


def main():
    update_state()


def update_state():
    attributes = {
        "stateGenerate": "DEPLOYING",
        "updatedAt": datetime.now(jst).isoformat(),
    }
    resp = table.update_item(
        Key={"identifier": env.identifier},
        UpdateExpression="set "
        + ", ".join([f"#{k} = :{k}" for k in attributes.keys()]),
        ExpressionAttributeNames={f"#{k}": k for k in attributes.keys()},
        ExpressionAttributeValues={f":{k}": v for k, v in attributes.items()},
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]


if __name__ == "__main__":
    main()
