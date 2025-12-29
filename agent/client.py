import requests

class GhostClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def get_state(self):
        try:
            response = requests.get(f"{self.base_url}/state")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_command(self, cmd):
        payload = {"command": cmd}
        try:
            response = requests.post(f"{self.base_url}/dispatch", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
