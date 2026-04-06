import uuid

def generate_device_id() -> str:
    return f"dev-{uuid.uuid4().hex[:12]}"