import json
import os

class TokenService:
    FILE = "token.json"

    def save(self, token, device_id):
        with open(self.FILE, "w") as f:
            json.dump({"token": token, "device_id": device_id}, f)

    def load(self):
        if not os.path.exists(self.FILE):
            return None, None
        with open(self.FILE, "r") as f:
            data = json.load(f)
            return data.get("token"), data.get("device_id")