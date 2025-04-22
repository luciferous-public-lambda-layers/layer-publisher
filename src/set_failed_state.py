from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import boto3
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_events import EventBridgeClient


class EnvironmentVariables(BaseSettings):
    table_name: str
    identifier: str
    url_action_run: str
    event_bus_name: str


jst = ZoneInfo("Asia/Tokyo")
env = EnvironmentVariables()
all_keys = ["stateLayer", "updatedAt", "githubActionsUrl"]

table: Table = boto3.resource("dynamodb").Table(env.table_name)
events: EventBridgeClient = boto3.client("events")

resp = table.update_item(
    Key={"identifier": env.identifier},
    UpdateExpression="set " + ", ".join([f"#{k} = :{k}" for k in all_keys]),
    ExpressionAttributeNames={f"#{k}": k for k in all_keys},
    ExpressionAttributeValues={
        ":stateLayer": "FAILED",
        ":updatedAt": datetime.now(jst).isoformat(),
        ":githubActionsUrl": env.url_action_run,
    },
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

payload_dict = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<!channel> `{datetime.now(tz=jst).isoformat()}`",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*System Name:* `public-lambda-layer-publisher`",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Identifier:* `{env.identifier}`"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*System Name:* failed in publishing"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Management Page:* <https://management.public-layers.luciferous.app/layer/{env.identifier}|link>",
            },
        },
    ]
}

count = 0
while count < 3:
    count += 1
    resp = events.put_events(
        Entries=[
            {
                "Source": "a",
                "DetailType": "a",
                "Detail": json.dumps(payload_dict),
                "EventBusName": env.event_bus_name,
            }
        ]
    )
    if resp["FailedEntryCount"] == 0:
        count = 999
