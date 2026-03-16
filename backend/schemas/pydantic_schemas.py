from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None

class UserOut(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ParcelCreate(BaseModel):
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    weight_kg: float

class AssignRiderRequest(BaseModel):
    parcel_id: str
    rider_id: str

class UpdateStatusRequest(BaseModel):
    new_status: str

class ParcelOut(BaseModel):
    parcel_id: str
    tracking_number: str
    sender_id: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    weight_kg: float
    current_status: str
    charges: float
    booked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }