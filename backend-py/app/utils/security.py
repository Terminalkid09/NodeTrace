import secrets
from app.models.device import Device

def generate_device_token():
    return "NT-DEV-" + secrets.token_hex(16)

def verify_device_token(db, token: str):
    return db.query(Device).filter(Device.device_token == token).first()