#!/bin/sh
set -e

echo "⏳ Waiting for PostgreSQL to be ready at $DATABASE_URL ..."
until pg_isready -h db -p 5432 -U postgres > /dev/null 2> /dev/null; do
  echo "Database is not ready yet, waiting..."
  sleep 2
done

echo "✅ Database is ready! Starting API..."
exec "$@"
