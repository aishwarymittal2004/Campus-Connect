import httpx
from typing import Any

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class TravelService:
    def __init__(self):
        self.train_api_key = settings.RAPIDAPI_KEY_TRAIN
        self.flight_api_key = settings.RAPIDAPI_KEY_FLIGHT

    async def get_train_status(self, train_number: str) -> dict[str, Any] | None:
        """
        Placeholder for fetching live train status via a RapidAPI provider.
        You must replace `RAPIDAPI_HOST` and `RAPIDAPI_URL` with the specific provider you subscribe to.
        """
        if not self.train_api_key:
            logger.warning("Train status called but no RAPIDAPI_KEY_TRAIN is set")
            return None

        # TODO: Replace with the actual URL and host from your RapidAPI subscription
        url = "https://your-rapidapi-train-provider.p.rapidapi.com/status"
        headers = {
            "X-RapidAPI-Key": self.train_api_key,
            "X-RapidAPI-Host": "your-rapidapi-train-provider.p.rapidapi.com"
        }
        params = {"train_number": train_number}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("rapidapi_train_status_failed", error=str(exc))
            return None

    async def get_flight_prices(self, source: str, destination: str, date: str) -> dict[str, Any] | None:
        """
        Placeholder for fetching flight prices via a RapidAPI provider (e.g., Skyscanner).
        You must replace `RAPIDAPI_HOST` and `RAPIDAPI_URL` with the specific provider you subscribe to.
        """
        if not self.flight_api_key:
            logger.warning("Flight prices called but no RAPIDAPI_KEY_FLIGHT is set")
            return None

        # TODO: Replace with the actual URL and host from your RapidAPI subscription
        url = "https://your-rapidapi-flight-provider.p.rapidapi.com/flights"
        headers = {
            "X-RapidAPI-Key": self.flight_api_key,
            "X-RapidAPI-Host": "your-rapidapi-flight-provider.p.rapidapi.com"
        }
        params = {
            "source": source,
            "destination": destination,
            "date": date
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("rapidapi_flight_prices_failed", error=str(exc))
            return None
