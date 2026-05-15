#!/usr/bin/env bash
HOST=${1:-https://10.255.28.248}

TOKEN=$(curl -sk -X POST "$HOST/auth/realms/aion/protocol/openid-connect/token" \
  -d "client_id=aion-frontend&grant_type=password&username=tests&password=test" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -sk -H "Authorization: Bearer $TOKEN" "$HOST/data-ingestion/nef/subscriptions" \
  | strings | grep -o 'perf-[a-f0-9]*' | while read nid; do
    code=$(curl -sk -o /dev/null -w "%{http_code}" -X DELETE \
      -H "Authorization: Bearer $TOKEN" \
      "$HOST/data-ingestion/nef/subscriptions/$nid")
    echo "$code $nid"
done
