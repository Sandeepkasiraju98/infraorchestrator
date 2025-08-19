import json
import boto3
import os

table_name = os.environ.get("DYNAMODB_TABLE_NAME")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")

    if method == "GET":
        response = table.scan()
        return {
            "statusCode": 200,
            "body": json.dumps(response.get("Items", []))
        }

    elif method == "POST":
        body = json.loads(event.get("body", "{}"))
        table.put_item(Item=body)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Item inserted"})
        }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Unsupported method"})
    }
