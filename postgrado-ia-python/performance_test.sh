#!/bin/bash
# Performance Test - Health Check Load Test
# Prueba de rendimiento: 50 usuarios concurrentes
# Endpoint: GET /health (no requiere API key)

OUTPUT_FILE="performance_test_results.txt"
NUM_USERS=50
REQUESTS_PER_USER=10
ENDPOINT="http://localhost:8000/health"

echo "=== PRUEBA DE RENDIMIENTO - SISTEMA RAG CHATBOT ===" | tee $OUTPUT_FILE
echo "Timestamp: $(date)" | tee -a $OUTPUT_FILE
echo "Endpoint: $ENDPOINT" | tee -a $OUTPUT_FILE
echo "Usuarios concurrentes: $NUM_USERS" | tee -a $OUTPUT_FILE
echo "Requests por usuario: $REQUESTS_PER_USER" | tee -a $OUTPUT_FILE
echo "Total requests: $((NUM_USERS * REQUESTS_PER_USER))" | tee -a $OUTPUT_FILE
echo "=======================================" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

# Crear archivo temporal para resultados
RESULTS_FILE=$(mktemp)
SUCCESS_COUNT=0
FAILURE_COUNT=0
TOTAL_TIME=0
MIN_TIME=999999
MAX_TIME=0

# Function to make requests
make_requests() {
    local user_id=$1
    for i in $(seq 1 $REQUESTS_PER_USER); do
        START=$(date +%s%N)
        RESPONSE=$(curl -s -w "\n%{http_code}" "$ENDPOINT" 2>/dev/null)
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        END=$(date +%s%N)
        
        # Calcular latencia en ms
        LATENCY=$(( (END - START) / 1000000 ))
        
        echo "$LATENCY,$HTTP_CODE" >> "$RESULTS_FILE"
        
        if [ "$HTTP_CODE" = "200" ]; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            FAILURE_COUNT=$((FAILURE_COUNT + 1))
        fi
    done
}

# Ejecutar pruebas en paralelo
echo "Iniciando pruebas concurrentes..." | tee -a $OUTPUT_FILE
for user in $(seq 1 $NUM_USERS); do
    make_requests $user &
done

# Esperar a que todas las pruebas terminen
wait

echo "Pruebas completadas." | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

# Procesar resultados
if [ -f "$RESULTS_FILE" ]; then
    TOTAL_REQUESTS=$(wc -l < "$RESULTS_FILE")
    LATENCIES=$(cut -d',' -f1 "$RESULTS_FILE" | sort -n)
    
    # Calcular estadísticas
    AVG_LATENCY=$(echo "$LATENCIES" | awk '{sum+=$1; count++} END {print sum/count}')
    MIN_LATENCY=$(echo "$LATENCIES" | head -1)
    MAX_LATENCY=$(echo "$LATENCIES" | tail -1)
    P95_LATENCY=$(echo "$LATENCIES" | awk '{print int(NR * 0.95)}' | tail -1)
    P95_VALUE=$(echo "$LATENCIES" | sed -n "${P95_LATENCY}p")
    
    SUCCESS_COUNT=$(grep ",200$" "$RESULTS_FILE" | wc -l)
    FAILURE_COUNT=$((TOTAL_REQUESTS - SUCCESS_COUNT))
    ERROR_RATE=$((FAILURE_COUNT * 100 / TOTAL_REQUESTS))
    THROUGHPUT=$(echo "scale=2; $TOTAL_REQUESTS / 30" | bc)  # Asumir 30 segundos
    
    echo "=== RESULTADOS ===" | tee -a $OUTPUT_FILE
    echo "Total Requests: $TOTAL_REQUESTS" | tee -a $OUTPUT_FILE
    echo "Exitosas: $SUCCESS_COUNT (HTTP 200)" | tee -a $OUTPUT_FILE
    echo "Fallidas: $FAILURE_COUNT" | tee -a $OUTPUT_FILE
    echo "Tasa de Error: ${ERROR_RATE}%" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    echo "=== LATENCIA (ms) ===" | tee -a $OUTPUT_FILE
    echo "Mínima: ${MIN_LATENCY}ms" | tee -a $OUTPUT_FILE
    echo "Promedio: ${AVG_LATENCY}ms" | tee -a $OUTPUT_FILE
    echo "P95: ${P95_VALUE}ms" | tee -a $OUTPUT_FILE
    echo "Máxima: ${MAX_LATENCY}ms" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    echo "=== THROUGHPUT ===" | tee -a $OUTPUT_FILE
    echo "Requests por segundo: $THROUGHPUT req/s" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    echo "=== STATUS DEL SISTEMA ===" | tee -a $OUTPUT_FILE
    curl -s "$ENDPOINT" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    
    rm -f "$RESULTS_FILE"
else
    echo "Error: No se generaron resultados" | tee -a $OUTPUT_FILE
fi

echo "" | tee -a $OUTPUT_FILE
echo "Reporte guardado en: $OUTPUT_FILE"
