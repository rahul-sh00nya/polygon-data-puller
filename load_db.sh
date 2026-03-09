#!/usr/bin/env bash
set -euo pipefail

# ── Usage ──────────────────────────────────────────────────────────────
# ./load_db.sh -h <host> -p <port> -U <user> [-d <dbname>] [-W]
#
# Defaults: host=localhost, port=5432, user=test, dbname=stock_data
# Pass -W to be prompted for a password.
# ───────────────────────────────────────────────────────────────────────

DB_HOST="localhost"
DB_PORT="5432"
DB_USER="test"
DB_NAME="stock_data"
PW_FLAG=""

while getopts "h:p:U:d:W" opt; do
  case $opt in
    h) DB_HOST="$OPTARG" ;;
    p) DB_PORT="$OPTARG" ;;
    U) DB_USER="$OPTARG" ;;
    d) DB_NAME="$OPTARG" ;;
    W) PW_FLAG="-W" ;;
    *) echo "Usage: $0 [-h host] [-p port] [-U user] [-d dbname] [-W]" >&2; exit 1 ;;
  esac
done

PSQL="psql -h $DB_HOST -p $DB_PORT -U $DB_USER $PW_FLAG"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Connecting to PostgreSQL at $DB_HOST:$DB_PORT as $DB_USER"

# ── Create database if it does not exist ───────────────────────────────
if $PSQL -lqt | cut -d\| -f1 | grep -qw "$DB_NAME"; then
  echo "==> Database '$DB_NAME' already exists"
else
  echo "==> Creating database '$DB_NAME'"
  $PSQL -d postgres -c "CREATE DATABASE $DB_NAME;"
fi

PSQL_DB="$PSQL -d $DB_NAME"

# ── Drop all tables in the public schema ───────────────────────────────
echo "==> Dropping all tables in '$DB_NAME'"
TABLES=$($PSQL_DB -t -A -c \
  "SELECT string_agg(tablename, ', ') FROM pg_tables WHERE schemaname = 'public';")

if [ -n "$TABLES" ]; then
  $PSQL_DB -c "DROP TABLE IF EXISTS $TABLES CASCADE;"
  echo "    Dropped: $TABLES"
else
  echo "    No tables to drop"
fi

# ── Run every .sql file in the script's directory ──────────────────────
echo "==> Loading SQL files from $SCRIPT_DIR"
LOADED=0
TOTAL_ROWS=0

for sql_file in "$SCRIPT_DIR"/*.sql; do
  [ -f "$sql_file" ] || continue
  fname="$(basename "$sql_file")"
  output=$($PSQL_DB -f "$sql_file" 2>&1)
  # Extract row count from COPY output (e.g. "COPY 591070")
  rows=$(echo "$output" | sed -n 's/^COPY \([0-9]*\)$/\1/p')
  rows=${rows:-0}
  echo "    $fname — $rows rows"
  LOADED=$((LOADED + 1))
  TOTAL_ROWS=$((TOTAL_ROWS + rows))
done

echo "==> Done: $LOADED files loaded, $TOTAL_ROWS total rows"
