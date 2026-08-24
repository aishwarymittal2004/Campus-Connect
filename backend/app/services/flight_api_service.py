import httpx
import uuid
from typing import Any
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class FlightAPIService:
    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY_FLIGHT
        self.host = "sky-scanner3.p.rapidapi.com"
        self.base_url = f"https://{self.host}/flights/search-oneway"

    def _resolve_airport_code(self, name: str) -> str:
        name = name.lower()
        if "bikaner" in name: return "BKB"
        if "jais" in name or "rgipt" in name or "rajiv gandhi" in name or "petroleum" in name or "amethi" in name: return "LKO" # Lucknow is closest
        if "gwalior" in name or "mits" in name: return "GWL"
        if "kanpur" in name: return "KNU"
        if "delhi" in name: return "DEL"
        return name[:3].upper()

    async def get_flight_schedules(self, origin_name: str, dest_name: str) -> list[dict]:
        src_code = self._resolve_airport_code(origin_name)
        dst_code = self._resolve_airport_code(dest_name)
        
        # MOCK FOR BIKANER -> RGIPT
        if src_code == "BKB" and dst_code == "LKO":
            return [
                {
                    "id": str(uuid.uuid4()),
                    "total_duration": "4h 15m",
                    "price_estimate": "?5200",
                    "legs": [
                        {
                            "flight_number": "AI-412",
                            "airline": "Air India",
                            "departure_airport": "Bikaner (BKB)",
                            "arrival_airport": "New Delhi (DEL)",
                            "departure_time": "11:30 AM",
                            "arrival_time": "12:45 PM",
                            "duration": "1h 15m"
                        },
                        {
                            "flight_number": "6E-2041",
                            "airline": "IndiGo",
                            "departure_airport": "New Delhi (DEL)",
                            "arrival_airport": "Lucknow (LKO)",
                            "departure_time": "02:45 PM",
                            "arrival_time": "03:45 PM",
                            "duration": "1h 00m"
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "total_duration": "6h 30m",
                    "price_estimate": "?4800",
                    "legs": [
                        {
                            "flight_number": "AI-412",
                            "airline": "Air India",
                            "departure_airport": "Bikaner (BKB)",
                            "arrival_airport": "New Delhi (DEL)",
                            "departure_time": "11:30 AM",
                            "arrival_time": "12:45 PM",
                            "duration": "1h 15m"
                        },
                        {
                            "flight_number": "SG-8273",
                            "airline": "SpiceJet",
                            "departure_airport": "New Delhi (DEL)",
                            "arrival_airport": "Lucknow (LKO)",
                            "departure_time": "05:00 PM",
                            "arrival_time": "06:00 PM",
                            "duration": "1h 00m"
                        }
                    ]
                }
            ]
            
        return []
