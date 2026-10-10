import base64
import json
import os
import boto3

QUEUE_URL = os.environ["QUEUE_URL"]
GAMES = ["doom", "pacman"]
sqs = boto3.client("sqs")

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def read_body(event):
    body = event.get("body")
    if body is None:
        raise ValueError("Falta el cuerpo de la peticion")
    if isinstance(body, dict):
        return body
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body)

def validate(data):
    if not isinstance(data, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")

    jugador = data.get("jugador")
    juego = data.get("juego")
    puntaje = data.get("puntaje")

    if not isinstance(jugador, str) or not jugador.strip():
        raise ValueError("'jugador' debe ser un texto no vacío")
    if not isinstance(juego, str) or not juego.strip():
        raise ValueError("'juego' debe ser un texto no vacío")
    if juego not in GAMES:
        raise ValueError("'juego' no valido")
    if isinstance(puntaje, bool) or not isinstance(puntaje, int):
        raise ValueError("'puntaje' debe ser un número entero")

    return {"jugador": jugador.strip(), "juego": juego.strip(), "puntaje": puntaje}

def handler(event, context):
    try:
        puntaje = validate(read_body(event))
    except (ValueError, json.JSONDecodeError) as e:
        return response(400, {"error": str(e)})

    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(puntaje))
    return response(202, {"mensaje": "Puntaje recibido", "puntaje": puntaje})
