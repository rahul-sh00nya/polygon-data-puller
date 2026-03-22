#!/usr/bin/env bash
set -euo pipefail

# ── Usage ──────────────────────────────────────────────────────────────
# ./load_db.sh [-c <connection_uri>]
#
# Default: connects to Neon remote PostgreSQL (stock_data database).
# Override with -c to use a different connection URI.
# ───────────────────────────────────────────────────────────────────────

DATABASE_URL='postgresql://username:password@hostname/database_name?sslmode=require&channel_binding=require'

while getopts "c:" opt; do
  case $opt in
    c) DATABASE_URL="$OPTARG" ;;
    *) echo "Usage: $0 [-c connection_uri]" >&2; exit 1 ;;
  esac
done

PSQL="psql"
PSQL_DB="$PSQL $DATABASE_URL"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Connecting to remote PostgreSQL"

# ── Drop all tables in the public schema ───────────────────────────────
echo "==> Dropping all tables"
TABLES=$($PSQL_DB -t -A -c \
  "SELECT string_agg(tablename, ', ') FROM pg_tables WHERE schemaname = 'public';")

if [ -n "$TABLES" ]; then
  $PSQL_DB -c "DROP TABLE IF EXISTS $TABLES CASCADE;"
  echo "    Dropped: $TABLES"
else
  echo "    No tables to drop"
fi

# ── Run every .sql file in the script's directory ──────────────────────
# cd so that relative CSV paths in \COPY commands resolve correctly
cd "$SCRIPT_DIR"
echo "==> Loading SQL files from $SCRIPT_DIR"
LOADED=0
FAILED=0
TOTAL_ROWS=0

for sql_file in "$SCRIPT_DIR"/*.sql; do
  [ -f "$sql_file" ] || continue
  fname="$(basename "$sql_file")"
  if output=$($PSQL_DB -f "$sql_file" 2>&1); then
    rows=$(echo "$output" | sed -n 's/^COPY \([0-9]*\)$/\1/p')
    rows=${rows:-0}
    echo "    $fname — $rows rows"
    LOADED=$((LOADED + 1))
    TOTAL_ROWS=$((TOTAL_ROWS + rows))
  else
    echo "    $fname — FAILED"
    echo "$output" | sed 's/^/      /'
    FAILED=$((FAILED + 1))
  fi
done

echo "==> Done: $LOADED files loaded, $FAILED failed, $TOTAL_ROWS total rows"
if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
