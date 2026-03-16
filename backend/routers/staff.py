from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models.sql_models import parcel_document, delivery_assignment_document, status_history_document
from schemas.pydantic_schemas import ParcelCreate, ParcelOut
from utils.security import decode_token
from config.database import get_db
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/staff", tags=["Staff"])

def require_staff(token: str):
    logger.info(f"Validating staff token (first 20 chars): {token[:20]}...")
    payload = decode_token(token)
    
    if not payload:
        logger.error("Token decode returned None")
        raise HTTPException(401, "Invalid or expired token")
    
    user_role = payload.get("role")
    logger.info(f"Token decoded, user role: {user_role}")
    
    if user_role != "staff":
        logger.error(f"Access denied - user role is '{user_role}', expected 'staff'")
        raise HTTPException(403, f"Staff access required. Your role: {user_role}")
    
    return payload

@router.get("/parcels")
def get_all_parcels(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    require_staff(token)
    parcels = list(db["parcels"].find())
    for p in parcels:
        p["parcel_id"] = str(p["_id"])
        p.pop("_id", None)
    return parcels

@router.get("/parcel/{parcel_id}")
def get_parcel_by_id(parcel_id: str, token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    require_staff(token)
    parcel = db["parcels"].find_one({"_id": ObjectId(parcel_id)})
    if not parcel:
        raise HTTPException(404, "Parcel not found")
    parcel["parcel_id"] = str(parcel["_id"])
    parcel.pop("_id", None)
    return parcel

@router.get("/riders")
def get_all_riders(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """Get list of all riders for assignment"""
    require_staff(token)
    riders = list(db["users"].find({"role": "rider"}))
    return [{"user_id": str(r["_id"]), "name": r["name"], "email": r["email"], "phone": r.get("phone")} for r in riders]

@router.post("/assign-rider")
def assign_rider(parcel_id: str, rider_id: str, token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    require_staff(token)

    # Validate parcel exists
    parcel = db["parcels"].find_one({"_id": ObjectId(parcel_id)})
    if not parcel:
        raise HTTPException(404, "Parcel not found")

    # Validate rider exists and is a rider
    rider = db["users"].find_one({"_id": ObjectId(rider_id), "role": "rider"})
    if not rider:
        raise HTTPException(404, "Rider not found")

    # Check if already assigned
    existing = db["delivery_assignments"].find_one({"parcel_id": ObjectId(parcel_id)})
    if existing:
        raise HTTPException(400, "Parcel already assigned to a rider")

    assignment = delivery_assignment_document(parcel_id=ObjectId(parcel_id), rider_id=str(rider["_id"]))
    db["delivery_assignments"].insert_one(assignment)

    return {"message": "Rider assigned successfully!"}

@router.post("/parcel/create", response_model=ParcelOut)
def create_parcel_as_staff(
    parcel: ParcelCreate,
    customer_email: str,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db)
):
    """Staff can create parcels on behalf of customers"""
    require_staff(token)

    # Find the customer by email
    customer = db["users"].find_one({"email": customer_email, "role": "customer"})
    if not customer:
        raise HTTPException(404, f"Customer with email '{customer_email}' not found")

    # Validate weight
    if parcel.weight_kg <= 0:
        raise HTTPException(400, "Weight must be greater than 0")

    # Validate receiver details
    if not parcel.receiver_name or not parcel.receiver_name.strip():
        raise HTTPException(400, "Receiver name is required")
    if not parcel.receiver_phone or not parcel.receiver_phone.strip():
        raise HTTPException(400, "Receiver phone is required")
    if not parcel.receiver_address or not parcel.receiver_address.strip():
        raise HTTPException(400, "Receiver address is required")

    charges = parcel.weight_kg * 50  # Rs.50 per kg
    tracking_number = f"TRK{datetime.now().strftime('%Y%m%d%H%M%S')}"

    new_parcel = parcel_document(
        tracking_number=tracking_number,
        sender_id=str(customer["_id"]),
        receiver_name=parcel.receiver_name,
        receiver_phone=parcel.receiver_phone,
        receiver_address=parcel.receiver_address,
        weight_kg=parcel.weight_kg,
        charges=charges,
        current_status="booked"
    )

    result = db["parcels"].insert_one(new_parcel)
    db["status_history"].insert_one(status_history_document(parcel_id=str(result.inserted_id), status="booked"))
    new_parcel["parcel_id"] = str(result.inserted_id)
    return new_parcel

@router.put("/parcel/{parcel_id}", response_model=ParcelOut)
def update_parcel(
    parcel_id: str,
    parcel: ParcelCreate,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db)
):
    """Staff can update/edit parcel details"""
    require_staff(token)

    # Find the parcel
    db_parcel = db["parcels"].find_one({"_id": ObjectId(parcel_id)})
    if not db_parcel:
        raise HTTPException(404, "Parcel not found")

    # Validate weight
    if parcel.weight_kg <= 0:
        raise HTTPException(400, "Weight must be greater than 0")

    # Validate receiver details
    if not parcel.receiver_name or not parcel.receiver_name.strip():
        raise HTTPException(400, "Receiver name is required")
    if not parcel.receiver_phone or not parcel.receiver_phone.strip():
        raise HTTPException(400, "Receiver phone is required")
    if not parcel.receiver_address or not parcel.receiver_address.strip():
        raise HTTPException(400, "Receiver address is required")

    db["parcels"].update_one(
        {"_id": ObjectId(parcel_id)},
        {
            "$set": {
                "receiver_name": parcel.receiver_name,
                "receiver_phone": parcel.receiver_phone,
                "receiver_address": parcel.receiver_address,
                "weight_kg": parcel.weight_kg,
                "charges": parcel.weight_kg * 50,
            }
        },
    )

    # Add status history for the update
    db["status_history"].insert_one(
        status_history_document(parcel_id=parcel_id, status=db_parcel.get("current_status", "booked"))
    )
    updated_parcel = db["parcels"].find_one({"_id": ObjectId(parcel_id)})
    updated_parcel["parcel_id"] = str(updated_parcel["_id"])
    updated_parcel.pop("_id", None)
    return updated_parcel