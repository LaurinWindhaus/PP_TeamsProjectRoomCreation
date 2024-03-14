import requests


def get_file_drive_item_id(access_token, site_id, folder_path, file_name):
    response = requests.get(f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{file_name}',
                            headers={'Authorization': f'Bearer {access_token}'})
    return response.json().get('id')


def get_file_edit_url(access_token, site_id, file_path):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_path}'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        web_url = response.json().get('webUrl')
    else:
        web_url = None

    return web_url


def create_editor_tab_with_excel_file(access_token, team_id, channel_id, file_web_edit_url, tab_name):
    url = f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/tabs'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'displayName': tab_name,
        'teamsApp@odata.bind': 'https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web',
        'configuration': {
            'entityId': '',
            'contentUrl': file_web_edit_url,  # URL for editing the file in Office Online
            'websiteUrl': file_web_edit_url,  # Same URL for consistency
            'removeUrl': '',
            'websiteUrl': file_web_edit_url
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()


# import os
# from services import get_access_token

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# tenant_id = os.getenv("TENANT_ID")
# access_token = get_access_token(client_id, client_secret, tenant_id)

# group_id = "86c11c65-bdb8-4e1c-bd0e-551fd4b61b27"
# site_id = "poeppelmanngmbh.sharepoint.com,841e5a98-146e-430b-9e36-501135705179,53d0bcc8-b4ba-4b29-84d9-aa8232dd8138"
# folder_path = "General/01 Projektinitiierung und -planung"
# file_name = "Projektterminplan.xlsx"

# file_drive_id = get_file_drive_item_id(access_token, site_id, folder_path, file_name)