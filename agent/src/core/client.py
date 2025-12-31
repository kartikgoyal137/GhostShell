import requests_unixsocket
import requests

class GhostClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.socket_path = "/tmp/ghostshell.sock".replace("/", "%2F")
        self.base_url = f"http+unix://{self.socket_path}"
        self.session = requests_unixsocket.Session()

    def get_state(self):
        try:
            response = self.session.get(f"{self.base_url}/state")
            result = response.json()

            if response.status_code != 200:
                 return {
                 "error": result.get("message", "Unknown error"),
                 "shell_output": result.get("output", "")
                 }
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def send_command(self, cmd):
        payload = {"command": cmd}
        try:
            response = self.session.post(f"{self.base_url}/dispatch", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
