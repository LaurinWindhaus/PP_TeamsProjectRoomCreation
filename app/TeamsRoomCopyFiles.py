import requests
import time

def get_drive_id_from_group_id(access_token, group_id):
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/drive"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json().get('id')


def get_site_id_from_group_id(access_token, group_id):
    url = f"https://graph.microsoft.com/v1.0//groups/{group_id}/sites/root"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json().get('id')


def find_general_folder_id(access_token, site_id):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    folders = [item for item in response.json().get('value', []) if item.get('folder')]

    for folder in folders:
        if folder.get('name').lower() == 'general':
            return folder.get('id')
    return None


def ensure_general_folder_exists(access_token, site_id):
    general_folder_id = find_general_folder_id(access_token, site_id)
    if general_folder_id is None:
        general_folder_id = create_folder(access_token, site_id, '', 'General')
        if general_folder_id:
            return general_folder_id
        else:
            return "Failed to create General folder."
    return general_folder_id


def list_files_in_team(access_token, site_id, item_id=None):
    if item_id:
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{item_id}/children"
    else:
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json().get('value', [])


def download_file(file_metadata):
    download_url = file_metadata['@microsoft.graph.downloadUrl']
    response = requests.get(download_url)
    return response.content


def upload_file(access_token, site_id, parent_item_id, file_name, file_content):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{parent_item_id}:/{file_name}:/content"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(url, headers=headers, data=file_content)
    return response.json()


def create_folder(access_token, site_id, parent_folder_id, folder_name):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{parent_folder_id}/children' if parent_folder_id else f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    body = {
        'name': folder_name,
        'folder': {},
        '@microsoft.graph.conflictBehavior': 'rename'
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 201:
        return response.json().get('id')
    else:
        print(f"Error creating folder: {response.json()}")
        return None
    

def copy_items(access_token, source_site_id, dest_site_id, parent_item_id, items, source_group_id, new_group_id):
    for item in items:
        if is_onenote_notebook(item):
            copy_notebook(access_token, source_group_id, "ProjektOneNote", new_group_id, get_site_id_from_group_id(access_token, new_group_id))
        else:
            if 'folder' in item:
                new_folder_id = create_folder(access_token, dest_site_id, parent_item_id, item['name'])
                sub_items = list_files_in_team(access_token, source_site_id, item['id'])
                copy_items(access_token, source_site_id, dest_site_id, new_folder_id, sub_items, source_group_id, new_group_id)
            else:
                file_content = download_file(item)
                upload_file(access_token, dest_site_id, parent_item_id, item['name'], file_content)
    return "Done"


def copy_notebook(access_token, source_group_id, source_notebook_name, new_group_id, new_site_id):
    source_notebooks = list_notebooks(access_token, source_group_id)
    source_notebook = next((nb for nb in source_notebooks if nb['displayName'].lower() == source_notebook_name.lower()), None)
    
    if not source_notebook:
        print(f"Notebook with name '{source_notebook_name}' not found.")
        return
    
    general_folder_id = None
    for i in list_files_in_team(access_token, new_site_id):
        if i["name"] == "General":
            copy_onenote_notebook(access_token, source_group_id, source_notebook["id"], new_group_id)
            general_folder_id = i["id"]
            time.sleep(20)
            for j in list_files_in_team(access_token, new_site_id):
                if j["name"] == "Notebooks":
                    for k in list_files_in_team(access_token, new_site_id, j["id"]):
                        if k["name"] == source_notebook_name:
                            new_notebook_id = k["id"]
    if move_notebook_to_specific_folder(access_token, new_group_id, new_notebook_id, general_folder_id) == 200:
        return(f"Successfully copied notebook '{source_notebook_name}' to the destination team.")


def copy_onenote_notebook(access_token, source_group_id, notebook_id, destination_group_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"https://graph.microsoft.com/v1.0/groups/{source_group_id}/onenote/notebooks/{notebook_id}/copyNotebook"
    payload = {
        "groupId": destination_group_id
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def is_onenote_notebook(item):
    return item["createdBy"]["application"]["displayName"] == "OneNote"


def list_notebooks(access_token, group_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/onenote/notebooks"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['value']


def move_notebook_to_specific_folder(access_token, new_group_id, notebook_id, new_folder_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',  # Ensure responses are in JSON
        'Content-Type': 'application/json'  # Correctly specify for JSON payload
    }
    move_url = f"https://graph.microsoft.com/v1.0/groups/{new_group_id}/drive/items/{notebook_id}"
    move_payload = {
        "parentReference": {
            "id": new_folder_id
        },
    }
    move_response = requests.patch(move_url, headers=headers, json=move_payload)
    if move_response.status_code == 200:
        return move_response.status_code
    else:
        return None



# import os
# from services import get_access_token, find_group_id_by_name

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# tenant_id = os.getenv("TENANT_ID")
# access_token = get_access_token(client_id, client_secret, tenant_id)

# try:
#     template_team_name = 'Projekttemplate'
#     template_group_id = find_group_id_by_name(access_token, template_team_name)

#     new_team_name = 'Testraum'
#     new_group_id = find_group_id_by_name(access_token, new_team_name)

#     template_site_id = get_site_id_from_group_id(access_token, template_group_id)
#     new_site_id = get_site_id_from_group_id(access_token, new_group_id)

#     template_root_folder_id = find_general_folder_id(access_token, template_site_id)
#     new_root_folder_id = ensure_general_folder_exists(access_token, new_site_id)

#     files_and_folders = list_files_in_team(access_token, template_site_id, template_root_folder_id)
#     copy_items(access_token, template_site_id, new_site_id, new_root_folder_id, files_and_folders, template_group_id, new_group_id)
# except Exception as e:
#     print(e)
#     print("An error occurred while copying files")
#     raise e