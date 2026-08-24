from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.deps import get_travel_service
from app.services.travel_service import TravelService

router = APIRouter(prefix="/travel", tags=["Travel (RapidAPI)"])

TravelSvc = Annotated[TravelService, Depends(get_travel_service)]

@router.get("/train-status", response_model=dict[str, Any])
async def get_train_status(
    travel_service: TravelSvc,
    train_number: str = Query(..., description="Train number to check status for"),
):
    """
    Fetch live train status using a RapidAPI provider.
    Requires RAPIDAPI_KEY_TRAIN to be set in the environment.
    """
    result = await travel_service.get_train_status(train_number)
    if result is None:
        raise HTTPException(status_code=502, detail="Failed to fetch train status from external API.")
    return result

@router.get("/flight-prices", response_model=dict[str, Any])
async def get_flight_prices(
    travel_service: TravelSvc,
    source: str = Query(..., description="Source airport code (e.g., DEL)"),
    destination: str = Query(..., description="Destination airport code (e.g., BOM)"),
    date: str = Query(..., description="Date of travel (YYYY-MM-DD)"),
):
    """
    Fetch flight prices using a RapidAPI provider.
    Requires RAPIDAPI_KEY_FLIGHT to be set in the environment.
    """
    result = await travel_service.get_flight_prices(source, destination, date)
    if result is None:
        raise HTTPException(status_code=502, detail="Failed to fetch flight prices from external API.")
    return result
