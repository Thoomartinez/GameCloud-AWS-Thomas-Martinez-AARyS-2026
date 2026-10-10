import json
import os
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ["TABLE_NAME"]
GAMES = ["doom", "pacman"]

table = boto3.resource("dynamodb").Table(TABLE_NAME)

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def top10(items):
    ord = sorted(items, key=lambda i: i["puntaje"], reverse=True)[:10]
    return [{"jugador": i["jugador"], "puntaje": int(i["puntaje"])} for i in ord]

def paginate(operation, **kwargs):
    items = []
    while True:
        resp = operation(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            return items
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

def handler(event, context):
    params = event.get("queryStringParameters") or {}
    game = (params.get("juego") or "").strip()

    if game:
        if game not in GAMES:
            return response(400, {"error": f"Game not found: {game}"})

        items = paginate(table.query, KeyConditionExpression=Key("juego").eq(game))
        return response(200, {game: top10(items)})

    per_game = {}
    for item in paginate(table.scan):
        per_game.setdefault(item["juego"], []).append(item)

    return response(200, {j: top10(items) for j, items in per_game.items()})
