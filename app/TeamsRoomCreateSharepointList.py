import requests


def create_sharepoint_list(access_token, site_id, list_name, columns):
    new_list_name = ""
    if list_name == "Entscheidung":
        new_list_name = "Entscheidungen"
    elif list_name == "Projektstatus Liste":
        new_list_name = "Projektstatus"
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    list_data = {
        "displayName": new_list_name,
        "columns": columns,
        "list": {
            "template": "genericList"
        }
    }
    response = requests.post(url, headers=headers, json=list_data)
    return response


def get_all_lists(access_token, site_id):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        all_lists = response.json().get('value', [])
        visible_lists = [list_info for list_info in all_lists if not list_info.get('hidden', False)]
        return visible_lists
    else:
        raise Exception("Error retrieving lists: " + str(response.json()))


def get_list_columns(access_token, site_id, list_id):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/columns'
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        columns = response.json().get('value', [])

        transformed_columns = []
        for column in columns:
            if column.get('readOnly') == False and column.get('columnGroup') == "Benutzerdefinierte Spalten" and column.get('name') != "Title" and column.get('displayName') != "Anlagen":
                new_column = {
                    "id": column.get('id'),
                    "displayName": column.get('displayName'),
                    "name": column.get('name'),
                    "hidden": column.get('hidden')
                }
                if 'description' in column:
                    new_column['description'] = column['description']
                if 'text' in column:
                    new_column['text'] = {"allowMultipleLines": True}
                elif 'personOrGroup' in column:
                    new_column['personOrGroup'] = {}
                elif 'dateTime' in column:
                    new_column['dateTime'] = {"format": "dateOnly"}
                elif 'choice' in column:
                    new_column['choice'] = {
                        "choices": column['choice']['choices']  # Include the choices from the original column
                    }
                else:
                    continue

                transformed_columns.append(new_column)
        return transformed_columns
    else:
        raise Exception(f"Error retrieving columns: {response.json()}")
    

def rename_sharepoint_column(access_token, site_id, list_id, old_column_name, new_column_name):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    fields_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/columns'
    response = requests.get(fields_url, headers=headers)
    fields = response.json()

    # Find the field that needs to be renamed
    field_to_update = next((field for field in fields['value'] if field['name'] == old_column_name), None)
    if field_to_update:
        update_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/columns/{field_to_update["id"]}'
        
        update_data = {
            'displayName': new_column_name
        }
        update_response = requests.patch(update_url, json=update_data, headers=headers)

        if update_response.status_code in [200, 204]:
            return update_response.json(), update_response.status_code
        else:
            return "Error rename Sharepoint list column", update_response.status_code
    else:
        return "Error no column find to rename", 404
    

# from TeamsRoomAddSharepointListsToTab import add_sharepoint_list_to_teams_tab
# from services import get_access_token, get_channel_id_by_name
# import os

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# tenant_id = os.getenv("TENANT_ID")
# access_token = get_access_token(client_id, client_secret, tenant_id)

# new_group_id = "bb22bb4c-95c5-408f-9809-124d2294f018"
# template_site_id = "poeppelmanngmbh.sharepoint.com,0ba4f450-67cb-4d65-842c-7bf764e21da6,f0e7aa66-011c-4c9c-aade-c5d431094b0b"
# new_site_id = "poeppelmanngmbh.sharepoint.com,ce74e121-77ab-460e-8b84-f568d6e5285b,b95d2906-d7d9-4e00-9afa-15693eef6644"

# try:
#     for sp_list in get_all_lists(access_token, template_site_id):
#         if sp_list.get("id") in ["1b328181-bf17-46bc-8887-1b1e651b8f36", "bf921424-c901-4473-a808-852b92d6aaf5"]:
#             columns = get_list_columns(access_token, template_site_id, sp_list.get("id"))
#             result = create_sharepoint_list(access_token, new_site_id, sp_list.get("displayName"), columns)
#             if result.json().get("name") == "Entscheidungen":
#                 new_column_name = "Titel der Entscheidung"
#             elif result.json().get("name") == "Projektstatus":
#                 new_column_name = "Reportingtag"
#             else:
#                 new_column_name = "Title"
#             rename_sharepoint_column(access_token, new_site_id, result.json().get("id"), "Title", new_column_name)

#             general_channel_id = get_channel_id_by_name(access_token, new_group_id, "General")
#             add_sharepoint_list_to_teams_tab_result = add_sharepoint_list_to_teams_tab(access_token, new_group_id, get_channel_id_by_name(access_token, new_group_id, "General"), sp_list.get("displayName"))
# except Exception as e:
#     print(e)