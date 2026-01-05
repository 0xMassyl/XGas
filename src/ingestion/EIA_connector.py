
import requests
import os
from pathlib import Path
from dotenv import load_dotenv


class EIAClient:
    """Client for EIA API v2 (HTTP + auth only)."""

    def __init__(self):
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        self.api_key = os.getenv("EIA_API_KEY")

        if not self.api_key:
            raise ValueError("EIA_API_KEY missing")

    def get(self, url: str, params: dict) -> list[dict]:
        params = dict(params)
        params["api_key"] = self.api_key

        r = requests.get(url, params=params)
        r.raise_for_status()


        data = r.json().get("response", {}).get("data", [])
        if not data:
            raise RuntimeError("No data returned by EIA")

        return data
