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

dt_text = datetime.now(jst).isoformat()

attributes = {
    "stateLayer": "PUBLISHED",
    "updatedAt": dt_text,
    "lastPublishedAt": dt_text,
}

resp = table.update_item(
    Key={"identifier": env.identifier},
    UpdateExpression="set " + ", ".join([f"#{k} = :{k}" for k in attributes.keys()]),
    ExpressionAttributeNames={f"#{k}": k for k in attributes.keys()},
    ExpressionAttributeValues={f":{k}": v for k, v in attributes.items()},
    ReturnValues="ALL_NEW",
)

print(
    json.dumps(
        resp,
        indent=2,
        ensure_ascii=False,
        default=lambda x: {"type": str(type(x)), "value": str(x)},
    )
)
