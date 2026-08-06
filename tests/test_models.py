import json
import os

import boto3
import pytest
from moto import mock_aws

os.environ["TABLE_NAME"] = "test-items"
os.environ["STAGE"] = "test"

from functions.shared.models import create, delete, get, list_items, root, update


@pytest.fixture
def table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="test-items",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


def test_root():
    resp = root({}, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["service"] == "AWS Serverless Starter"


def test_create_requires_name(table):
    resp = create({"body": json.dumps({})}, None)
    assert resp["statusCode"] == 400


def test_crud_lifecycle(table):
    created = create({"body": json.dumps({"name": "widget", "tags": ["a"]})}, None)
    assert created["statusCode"] == 201
    item = json.loads(created["body"])
    item_id = item["id"]
    assert item["name"] == "widget"

    fetched = get({"pathParameters": {"id": item_id}}, None)
    assert fetched["statusCode"] == 200
    assert json.loads(fetched["body"])["id"] == item_id

    listed = list_items({}, None)
    assert listed["statusCode"] == 200
    assert json.loads(listed["body"])["count"] == 1

    updated = update(
        {"pathParameters": {"id": item_id}, "body": json.dumps({"name": "gadget"})},
        None,
    )
    assert updated["statusCode"] == 200
    assert json.loads(updated["body"])["name"] == "gadget"

    deleted = delete({"pathParameters": {"id": item_id}}, None)
    assert deleted["statusCode"] == 204

    missing = get({"pathParameters": {"id": item_id}}, None)
    assert missing["statusCode"] == 404
