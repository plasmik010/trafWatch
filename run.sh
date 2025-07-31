#!/bin/bash
set -e
max_retries=15
count=0

echo "[cron $(date)] Running trafWatch with args: -d $1 -t $2 $3"

cd /app
while (( count < max_retries )); do
    /usr/local/bin/python3 /app/main.py -d "$1" -t "$2" "$3"
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        if [ $count -gt 0 ]; then
            echo "[cron $(date)] Success [$1] after $((count+1)) attempt(s)"
        fi
        exit 0
    else
        echo "[cron $(date)] Failed [$1] with code $exit_code (attempt $((count+1)))"
        ((count++))
        sleep 40  # Wait before retrying
    fi
done

echo "[cron $(date)] Failed [$1] after $max_retries attempts"
exit 1
