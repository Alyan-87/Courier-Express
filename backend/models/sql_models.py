from datetime import datetime

def user_document(name, email, phone, password_hash, role):
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }


def parcel_document(
    tracking_number,
    sender_id,
    receiver_name,
    receiver_phone,
    receiver_address,
    weight_kg,
    charges=0.0,
    current_status="booked",
):
    return {
        "tracking_number": tracking_number,
        "sender_id": sender_id,
        "receiver_name": receiver_name,
        "receiver_phone": receiver_phone,
        "receiver_address": receiver_address,
        "weight_kg": weight_kg,
        "charges": charges,
        "current_status": current_status,
        "booked_at": datetime.utcnow(),
    }


def delivery_assignment_document(parcel_id, rider_id, status="assigned"):
    return {
        "parcel_id": parcel_id,
        "rider_id": rider_id,
        "status": status,
    }


def status_history_document(parcel_id, status, changed_at=None):
    return {
        "parcel_id": parcel_id,
        "status": status,
        "changed_at": changed_at or datetime.utcnow(),
    }