#!/bin/bash
# Test and run Flask + FastAPI. Run from project root: ./scripts/test_and_run_servers.sh
# Or: bash scripts/test_and_run_servers.sh

set -e
cd "$(dirname "$0")/.."
echo "=== Freeing ports 8081 and 8000 ==="
lsof -ti :8081 | xargs kill -9 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sleep 2

echo "=== Starting Flask on 8081 ==="
python3 app_global.py &
FLASK_PID=$!

echo "=== Starting FastAPI on 8000 ==="
python3 -m uvicorn api.main_api:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

echo "=== Waiting for servers (up to 20s) ==="
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  sleep 1
  F=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:8081/ 2>/dev/null || echo "000")
  A=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:8000/health 2>/dev/null || echo "000")
  if [ "$F" = "200" ] && [ "$A" = "200" ]; then
    echo "  Both responded after ${i}s."
    break
  fi
  [ $i -eq 20 ] && echo "  Timeout waiting for one or both servers."
done

echo "=== Testing endpoints ==="
FLASK_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8081/ || echo "000")
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/health || echo "000")

echo "Flask  http://127.0.0.1:8081  → HTTP $FLASK_CODE"
echo "FastAPI http://127.0.0.1:8000/health → HTTP $API_CODE"

if [ "$FLASK_CODE" = "200" ] && [ "$API_CODE" = "200" ]; then
  echo ""
  echo "✅ TEST PASSED – Both servers are running. Open http://127.0.0.1:8081 in your browser."
  echo "   Press Ctrl+C in this window to stop both servers."
  wait $FLASK_PID $UVICORN_PID 2>/dev/null || true
else
  echo ""
  echo "❌ TEST FAILED – Flask got $FLASK_CODE, FastAPI got $API_CODE. Check the output above."
  kill $FLASK_PID $UVICORN_PID 2>/dev/null || true
  exit 1
fi
