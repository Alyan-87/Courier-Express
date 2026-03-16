from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models.sql_models import status_history_document
from utils.security import decode_token
from config.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/rider", tags=["Rider"])

def require_rider(token: str):
    logger.info(f"Validating rider token (first 20 chars): {token[:20]}...")
    payload = decode_token(token)
    
    if not payload:
        logger.error("Token decode returned None")
        raise HTTPException(401, "Invalid or expired token")
    
    user_role = payload.get("role")
    logger.info(f"Token decoded, user role: {user_role}")
    
    if user_role != "rider":
        logger.error(f"Access denied - user role is '{user_role}', expected 'rider'")
        raise HTTPException(403, f"Rider access required. Your role: {user_role}")
    
    return payload

@router.get("/my-parcels")
def my_parcels(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """Get all parcels assigned to the logged-in rider"""
    user = require_rider(token)

    db_user = db["users"].find_one({"email": user["sub"]})
    if not db_user:
        raise HTTPException(404, "User not found")

    assignments = list(db["delivery_assignments"].find({"rider_id": str(db_user["_id"])}))

    parcels = []
    for assignment in assignments:
        parcel = db["parcels"].find_one({"_id": assignment["parcel_id"]})
        if parcel:
            parcel["parcel_id"] = str(parcel["_id"])
            parcel.pop("_id", None)
            parcels.append(parcel)

    return parcels

@router.put("/update-status/{parcel_id}")
def update_status(parcel_id: str, new_status: str, token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    require_rider(token)

    # Validate parcel exists
    parcel = db["parcels"].find_one({"_id": ObjectId(parcel_id)})
    if not parcel:
        raise HTTPException(404, "Parcel not found")

    # Validate rider is assigned to this parcel
    user = require_rider(token)
    db_user = db["users"].find_one({"email": user["sub"]})
    assignment = db["delivery_assignments"].find_one(
        {"parcel_id": ObjectId(parcel_id), "rider_id": str(db_user["_id"])}
    )
    if not assignment:
        raise HTTPException(403, "You are not assigned to this parcel")

    # Validate status value
    valid_statuses = ["booked", "packed", "in transit", "out for delivery", "delivered"]
    if new_status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    db["parcels"].update_one({"_id": ObjectId(parcel_id)}, {"$set": {"current_status": new_status}})
    db["status_history"].insert_one(status_history_document(parcel_id=parcel_id, status=new_status))

    return {"message": f"Status updated to {new_status}"}