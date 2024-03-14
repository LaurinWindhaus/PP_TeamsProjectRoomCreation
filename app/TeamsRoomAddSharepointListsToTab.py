import requests

def get_sharepoint_site_url(access_token, team_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        f'https://graph.microsoft.com/v1.0/groups/{team_id}/sites/root',
        headers=headers
    )
    if response.status_code == 200:
        site_url = response.json().get('webUrl')
        return site_url
    else:
        raise Exception(f"Error retrieving site URL: {response.json()}")

def add_sharepoint_list_to_teams_tab(access_token, team_id, channel_id, list_name):
    new_list_name = ""
    if list_name == "Entscheidung":
        new_list_name = "Entscheidungen"
    elif list_name == "Projektstatus Liste":
        new_list_name = "Projektstatus"
    print(new_list_name)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        site_url = get_sharepoint_site_url(access_token, team_id)
        list_url = f"{site_url}/Lists/{new_list_name}/AllItems.aspx"
    except Exception as e:
        return str(e)

    payload = {
        "displayName": f"{new_list_name}",
        "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web",
        "configuration": {
            "entityId": "",
            "contentUrl": list_url,
            "websiteUrl": list_url,
            "removeUrl": list_url,
            "customSettings": ""
        }
    }

    response = requests.post(
        f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/tabs',
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        return "Tab successfully added."
    else:
        return f"Error adding tab: {response.json()}"