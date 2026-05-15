"""
NWDAF Platform Performance Tests — all through nginx (https://localhost)

Usage:
    locust -f locustfile.py --host https://localhost
    locust -f locustfile.py --host https://localhost --headless -u 50 -r 5 --run-time 2m
"""
from ingestion import IngestionUser
from data_storage import StorageQueryUser
from ml import MLUser

__all__ = ["IngestionUser", "StorageQueryUser", "MLUser"]
