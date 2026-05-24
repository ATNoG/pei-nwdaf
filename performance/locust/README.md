# Run

Get token first (replace IP if needed):
```bash
export AION_TOKEN=$(curl -sk -X POST https://<address>/auth/realms/aion/protocol/openid-connect/token \
  -d "client_id=aion-frontend&grant_type=password&username=<username>&password=<password>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

For ML inference test, create and train a model first via the frontend, then run:
```bash
export ML_MODEL_ID=<model-id-from-frontend>
```

Then run:
```bash
uv run --with locust locust -f ingestion.py --host <host> --web-port 8089
uv run --with locust locust -f data_storage.py --host <host> --web-port 8090
uv run --with locust locust -f ml.py --host <host> --web-port 8091
```
