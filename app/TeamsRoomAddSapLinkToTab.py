import os
import requests
from services import get_access_token, find_group_id_by_name, get_channel_id_by_name
    

def create_tab(access_token, team_id, channel_id):
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/tabs"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "displayName": "SAP Stunden buchen",
        "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web",
        "configuration": {
            "entityId": "",
            "contentUrl": "https://ppsapfe1.sap.poeppelmann.com/sap/bc/ui2/flp#Z_CAT2-manage",
            "websiteUrl": "https://ppsapfe1.sap.poeppelmann.com/sap/bc/ui2/flp#Z_CAT2-manage",
            "removeUrl": "",
            "customProperty": ""
        }
    }
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 201:
        raise Exception(f"Failed to add planner as a tab in Teams channel. Status Code: {response.status_code}, Response: {response.text}")

    return response.json()