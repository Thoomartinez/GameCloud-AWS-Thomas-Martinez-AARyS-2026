import json
import os
import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

def handler(event, context):
    for registro in event["Records"]:

        data = json.loads(registro["body"])
        jugador = data["jugador"]
        juego = data["juego"]
        puntaje = int(data["puntaje"])

        try:
            table.put_item(
                Item={"juego": juego, "jugador": jugador, "puntaje": puntaje},
                ConditionExpression="attribute_not_exists(puntaje) OR puntaje < :nuevo",
                ExpressionAttributeValues={":nuevo": puntaje},
            )
            print(f"GUARDADO juego={juego} jugador={jugador} puntaje={puntaje}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                # No es un error real: ya hay un puntaje igual o mejor
                print(f"IGNORADO juego={juego} jugador={jugador} puntaje={puntaje} (no supera el mejor)")
            else:
                raise
