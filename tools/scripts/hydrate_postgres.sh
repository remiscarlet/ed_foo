#!/usr/bin/env bash

if ! psql $DATABASE_URL -c "SELECT 1 FROM core.systems LIMIT 1;" >/dev/null 2>&1; then
    echo "Hydrating..."
    make run-pipeline
else
    echo "Database already hydrated."
fi