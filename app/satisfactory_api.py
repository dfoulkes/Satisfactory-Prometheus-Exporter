import requests
import os
from dataclasses import dataclass
# from dotenv import load_dotenv

login_headers = {
"Content-Type": "application/json",
}


# Load environment variables from .env file
# load_dotenv()

# url = "https://192.168.50.20:7777/api/v1"

def get_password():
    return os.getenv("SATISFACTORY_PASSWORD")

def get_server_url():
    domain = os.getenv("SATISFACTORY_URL")
    if domain is None:
        raise ValueError("Environment variable 'SATISFACTORY_URL' is not set.")
    url = "https://"+domain+":"+get_server_port()+"/api/v1"
    return url

def get_server_port():
    port = os.getenv("SATISFACTORY_PORT")
    if port is None:
        return "7777"
    return str(port)

def get_api_token() -> str:
    data = {
        "function": "PasswordLogin",
        "data": {
            "MinimumPrivilegeLevel": "Administrator",
            "Password": get_password()
        }
    }
    #response = requests.post(f"{url}/login", headers=login_headers, json=data, verify=False)
    response = requests.post(f"{get_server_url()}", headers=login_headers, json=data, verify=False)
    if "errorCode" in response.content.decode('utf-8'):
        raise Exception("Something went wrong with the login process.")

    if response.status_code == 200:
       response_data = response.json()
       return response_data["data"]["authenticationToken"]
    else:
       raise Exception("Did not receive a 200 status code in back from the API.")

# Now get Server Stats

def get_server_stats(token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "function": "QueryServerState",
        "data": {}
    }
    response = requests.post(f"{get_server_url()}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return covert_json_to_class(response.json()["data"]["serverGameState"])
    else:
        raise Exception("Failed to retrieve server stats.")

def covert_json_to_class(json):
    return SatisfactoryGameStatus(
        activeSessionName=json["activeSessionName"],
        numConnectedPlayers=json["numConnectedPlayers"],
        playerLimit=json["playerLimit"],
        techTier=json["techTier"],
        isGameRunning=json["isGameRunning"],
        totalGameDuration=json["totalGameDuration"],
        isGamePaused=json["isGamePaused"],
        averageTickRate=json["averageTickRate"],
        autoLoadSessionName=json["autoLoadSessionName"]
    )

@dataclass
class SatisfactoryGameStatus:
    activeSessionName: str
    numConnectedPlayers: int
    playerLimit: int
    techTier: int
    isGameRunning: bool
    totalGameDuration: int
    isGamePaused: bool
    averageTickRate: float
    autoLoadSessionName: str
