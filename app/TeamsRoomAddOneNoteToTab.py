import requests


def get_existing_onenote_tab(access_token, group_id, channel_id):
    url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/tabs'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def remove_existing_onenote_tab(access_token, group_id, channel_id, tab_id):
    url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/tabs/{tab_id}'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code


def get_notebook_id(access_token, site_id):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/onenote/notebooks'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        notebooks = response.json().get('value', [])
        if notebooks:
            return notebooks[0]['id']
    return None


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


def create_onenote_tab(access_token, group_id, channel_id, tab_name, file_edit_url):
    url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/tabs'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'displayName': tab_name,
        'teamsApp@odata.bind': 'https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web',
        'configuration': {
            'entityId': '',
            'contentUrl': file_edit_url,  # URL for editing the file in Office Online
            'removeUrl': '',
            'websiteUrl': file_edit_url
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()


def list_notebooks(access_token, group_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/onenote/notebooks"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['value']



# from dotenv import load_dotenv
# import os
# from services import *
# new_group_id = "55013860-f801-4c72-bb1c-3ed02b6fd488"
# template_group_id = "28244f9e-46a7-4e4f-9bd9-bcd8063f451d"

# new_site_id = "poeppelmanngmbh.sharepoint.com,63e91bd8-7aa8-4246-8d0e-7545255a06f3,096668f4-0a90-4146-a93a-40b23ba6eeaa"

# load_dotenv()
# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# tenant_id = os.getenv("TENANT_ID")
# access_token = get_access_token(client_id, client_secret, tenant_id)

# new_channel_id = get_channel_id_by_name(access_token, new_group_id, 'General')
# existing_onenote_tab = get_existing_onenote_tab(access_token, new_group_id, new_channel_id)
# if len(existing_onenote_tab) > 0:
#     tab_id = existing_onenote_tab['value'][0]['id']
#     remove_existing_onenote_tab_result = remove_existing_onenote_tab(access_token, new_group_id, new_channel_id, tab_id)
# notebook_id = get_notebook_id(access_token, new_site_id)
# file_edit_url = get_file_edit_url(access_token, new_site_id, "General/ProjektOneNote")
# create_onenote_tab_result = create_onenote_tab(access_token, new_group_id, new_channel_id, "Notizbuch", file_edit_url)
# print(create_onenote_tab_result)