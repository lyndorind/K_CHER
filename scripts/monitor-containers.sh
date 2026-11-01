#!/usr/bin/env bash
# Моніторинг ресурсів контейнерів: кожні N секунд записує в CSV
# використання CPU та пам'яті всіх запущених контейнерів (docker stats).
#
# Використання: bash scripts/monitor-containers.sh [файл.csv] [інтервал_секунд]
# Зупинка: Ctrl+C або kill.
set -euo pipefail

OUT="${1:-docker-stats.csv}"
INTERVAL="${2:-2}"

echo "timestamp,container,cpu_percent,mem_usage,mem_percent" > "$OUT"

while true; do
  now="$(date -u +%H:%M:%S)"
  docker stats --no-stream \
    --format '{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}' \
    | while IFS= read -r line; do
        echo "${now},${line}" >> "$OUT"
      done
  sleep "$INTERVAL"
done
