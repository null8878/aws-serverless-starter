import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "items")
table = dynamodb.Table(table_name)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def create(event, context)():
    """TODO: Add docstring."""
    try:
        body = json.loads(event.get("body", "{}"))

        if not body.get("name"):
            return {
                "statusCode": 400,
                "headers": _cors_headers(),
                "body": json.dumps({"error": "name is required"}),
            }

        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "id": item_id,
            "name": body["name"],
            "description": body.get("description", ""),
            "created_at": now,
            "updated_at": now,
        }

        if "tags" in body:
            item["tags"] = body["tags"]

        table.put_item(Item=item)

        return {
            "statusCode": 201,
            "headers": _cors_headers(),
            "body": json.dumps(item, cls=DecimalEncoder),
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": str(e)}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": "internal server error"}),
        }


def get(event, context):
    try:
        item_id = event["pathParameters"]["id"]

        response = table.get_item(Key={"id": item_id})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "headers": _cors_headers(),
                "body": json.dumps({"error": "item not found"}),
            }

        return {
            "statusCode": 200,
            "headers": _cors_headers(),
            "body": json.dumps(item, cls=DecimalEncoder),
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": str(e)}),
        }


def list_items(event, context):
    try:
        limit = int(event.get("queryStringParameters", {}).get("limit", 20))
        limit = min(limit, 100)

        scan_kwargs = {"Limit": limit}
        done = False
        items = []

        while not done:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            if "LastEvaluatedKey" in response:
                scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            else:
                done = True

        return {
            "statusCode": 200,
            "headers": _cors_headers(),
            "body": json.dumps(
                {"items": items, "count": len(items)},
                cls=DecimalEncoder,
            ),
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": str(e)}),
        }


def update(event, context):
    try:
        item_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body", "{}"))

        update_expr = "SET updated_at = :updated_at"
        expr_values = {":updated_at": datetime.now(timezone.utc).isoformat()}
        expr_names = {}

        if "name" in body:
            update_expr += ", #n = :name"
            expr_values[":name"] = body["name"]
            expr_names["#n"] = "name"

        if "description" in body:
            update_expr += ", description = :desc"
            expr_values[":desc"] = body["description"]

        if "tags" in body:
            update_expr += ", tags = :tags"
            expr_values[":tags"] = body["tags"]

        response = table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names if expr_names else None,
            ReturnValues="ALL_NEW",
        )

        return {
            "statusCode": 200,
            "headers": _cors_headers(),
            "body": json.dumps(response["Attributes"], cls=DecimalEncoder),
        }

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "headers": _cors_headers(),
                "body": json.dumps({"error": "item not found"}),
            }
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": str(e)}),
        }


def delete(event, context):
    try:
        item_id = event["pathParameters"]["id"]

        table.delete_item(Key={"id": item_id})

        return {
            "statusCode": 204,
            "headers": _cors_headers(),
            "body": "",
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "headers": _cors_headers(),
            "body": json.dumps({"error": str(e)}),
        }


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json",
    }
