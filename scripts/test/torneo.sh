#!/bin/bash
# --- Configuración ---
awsl() { aws --endpoint-url=http://localhost:4566 "$@"; }
API_ID=$(awsl apigatewayv2 get-apis --query 'Items[0].ApiId' --output text)
URL="http://$API_ID.execute-api.localhost:4566/scores"
QUEUE_URL=$(awsl sqs get-queue-url --queue-name puntajes --query QueueUrl --output text)

JUGADORES=(ana bob pedro diego eva lucas sofia juan)
JUEGOS=(doom pacman)

estado_cola() {
  echo "[$(date +%T)] Estado de la cola:"
  awsl sqs get-queue-attributes --queue-url "$QUEUE_URL" \
    --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
    --query Attributes --output table
}

echo '--ESTADO INICIAL--'
estado_cola

# --- Envío de 50 puntajes en paralelo ---
rm -f /tmp/codigos.txt
for i in $(seq 1 50); do
  j=${JUGADORES[$((RANDOM % ${#JUGADORES[@]}))]}
  g=${JUEGOS[$((RANDOM % ${#JUEGOS[@]}))]}
  p=$((RANDOM % 10000))
  curl -s -o /dev/null -w "%{http_code}\n" -X POST "$URL" \
    -H 'Content-Type: application/json' \
    -d "{\"jugador\":\"$j\",\"juego\":\"$g\",\"puntaje\":$p}" >> /tmp/codigos.txt &
done

echo '--DURANTE PICO DE TORNEO--'
estado_cola
wait          # espera a que terminen los 50 envíos
echo '--DESPUES DE PICO--'
estado_cola

echo "Códigos HTTP recibidos:"
sort /tmp/codigos.txt | uniq -c

sleep 10      # tiempo para que la Lambda consuma los mensajes
echo '--ESTADO COLA FINAL--'
estado_cola   # una vez procesados
