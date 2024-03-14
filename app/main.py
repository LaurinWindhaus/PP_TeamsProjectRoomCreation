from TeamsRoomCreation import *
from TeamsRoomDeletion import *
from TeamsRoomCopyFiles import *
from TeamsRoomAddOneNoteToTab import *
from TeamsRoomAddPlanner import *
from TeamsRoomAddExcelToTab import *
from TeamsRoomCreateSharepointList import *
from TeamsRoomAddSharepointListsToTab import *
from TeamsRoomAddSapLinkToTab import *
from ListSharepointProjectList import *
from JiraTicketCreation import *

from services import *

from dotenv import load_dotenv
import logging, time
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

load_dotenv()

def remove_quotes_if_present(s):
    # Check if the first character is a double quote
    if s.startswith('"'):
        s = s[1:]
    # Check if the last character is a double quote
    if s.endswith('"'):
        s = s[:-1]
    return s

client_id = remove_quotes_if_present(os.getenv("CLIENT_ID"))
client_secret = remove_quotes_if_present(os.getenv("CLIENT_SECRET"))
tenant_id = remove_quotes_if_present(os.getenv("TENANT_ID"))

jira_username = remove_quotes_if_present(os.getenv("JIRA_USERNAME"))
jira_password = remove_quotes_if_present(os.getenv("JIRA_PASSWORD"))

pp_projekt_site_id = "poeppelmanngmbh.sharepoint.com,48d1194c-58e6-4d9f-b117-6b48c53f7560,d9c5cee9-39a7-4858-b884-f9e84d529f3e"
pp_projekt_list_id = "fb0ecd46-a62c-4583-92c5-49f0068a1963"

# class Team(BaseModel):
#     name: str = Field(..., example="LaurinTestrojektraum")
#     owner: str = Field(..., example="laurinwindhaus@poeppelmann.com")

# @app.post("/create_team")
# def create_team(team: Team):
#     new_team_name = team.name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
#     owner_email = team.owner
#     logger = init_logger(owner_email, new_team_name)
#     tc = TeamCreation(new_team_name, owner_email, logger, access_token)
#     result = tc.create_team()
#     if result == None:
#         return {"status_code": 500, "message": "Error creating team"}
#     elif result.get("status_code") == 201:
#         return result
#     else:
#         return {"status_code": 500, "message": "Error creating team"}


def run_team_creation():
    access_token = get_access_token(client_id, client_secret, tenant_id)

    list_of_projects_to_create = get_projects_from_sharepoint_list(access_token, pp_projekt_site_id, pp_projekt_list_id)
    for list_element in list_of_projects_to_create:
        list_element_title = "PRJ-"+list_element.get('fields').get('Title')
        list_element_owner = list_element.get('fields').get('Email_x0020_Projektleiter')
        logger = init_logger(list_element_owner, list_element_title)
        logger.info(f"List element: {list_element}")
        list_element_created_at = list_element.get('fields').get('Created')
        tc = TeamCreation(list_element_title, list_element_owner, logger, access_token)
        result = tc.create_team()
        logger.info(f"Result: {result}")
        if result != None:
            update_fields = {
                "Teamraum_x0020_Link": result.get("team_room_link"),
                "ProjektstatusLink": result.get('project_status_link'),
                "TeamID": result.get('group_id'),
                "lastProjektReport": list_element_created_at,
                "ChannelID": result.get('channel_id')
            }
            logger.info(f"Update fields: {update_fields}")
            update_element_result = update_sharepoint_list_entry(access_token, pp_projekt_site_id, pp_projekt_list_id, list_element.get('id'), {"TeamID": result.get("group_id")})
            logger.info(f"Update element result: {update_element_result}")
        else:
            update_fields = {
                "TeamID": "null",
            }
            logger.info(f"Update fields: {update_fields}")
            update_element_result = update_sharepoint_list_entry(access_token, pp_projekt_site_id, pp_projekt_list_id, list_element.get('id'), {"TeamID": result.get("group_id")})
            logger.info(f"Update element result: {update_element_result}")


def init_logger(owner_email, new_team_name):
    log_directory = "./logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{log_directory}/log_{current_time}_{owner_email}_{new_team_name}.log"
    
    # absolute_log_path = os.path.abspath(log_filename)
    # print(f"Log file: {absolute_log_path}")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

class TeamCreation():
    def __init__(self, name, owner_email, logger, access_token):
        self.new_team_name = name
        self.team_description = "Projektraum"
        self.owner_email = owner_email
        self.logger = logger

        self.access_token = access_token

        self.template_team_name = os.getenv("TEMPLATE_TEAM_NAME").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace('"', '')
        logger.info(f"Template team name: {self.template_team_name}")

        logger.info(f"Owner email: {self.owner_email}")
        logger.info(f"New team name: {self.new_team_name}")
        logger.info(f"Team description: {self.team_description}")
        logger.info(f"Datetime: {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")

    def delete_team(self):
        time.sleep(10)
        self.logger.info(f"--------------------Deleting team--------------------")
        summary = f'Raumerstellung "{self.new_team_name}" fehlgeschlagen'
        description_text = f'Bitte den Projektraum mit dem Namen "{self.new_team_name}" des Owners "{self.owner_email}" per PowerShell aus den Deleted Sites im SharePoint Admin Center löschen und anschließend manuell anlegen.'
        group_id = find_group_id_by_name(self.access_token, self.new_team_name)
        self.logger.info(f"Group id: {group_id}")
        if group_id is None:
            self.logger.info(f"Group {self.new_team_name} not found")
            # create_ticket_result = create_jira_ticket(jira_username, jira_password, summary, description_text)
            # self.logger.info(f"Create ticket result: {create_ticket_result}")
            return None
        result = soft_delete_group(self.access_token, group_id)
        self.logger.info(f"Soft delete result: {result}")
        is_group_soft_deleted = check_if_group_is_soft_deleted(self.access_token, group_id)
        self.logger.info(f"Is group soft deleted: {is_group_soft_deleted}")
        if is_group_soft_deleted:
            self.logger.info(f"Group is soft deleted")
            # create_ticket_result = create_jira_ticket(jira_username, jira_password, summary, description_text)
            # self.logger.info(f"Create ticket result: {create_ticket_result}")
            return 1

    def create_team(self):
        # Teamroom creation
        self.logger.info(f"--------------------Creating team--------------------")
        try:
            owner_user_id = get_user_id_from_email(self.owner_email, self.access_token)
            self.logger.info(f"Owner user id: {owner_user_id}")
            owner_username = get_username_from_email(self.owner_email, self.access_token)
            self.logger.info(f"Owner username: {owner_username}")
            does_team_exist = check_if_team_exist(self.access_token, self.new_team_name)
            self.logger.info(f"Does team exist: {does_team_exist}")

            if does_team_exist:
                self.logger.info(f"Team already exists")
                return None

            result = create_teams_room(self.access_token, self.new_team_name, self.team_description, owner_user_id)
            if result.status_code == 202 or result.status_code == 201:
                self.logger.info(f"Create team result: {result.status_code}, {result.text}")
            else:
                self.logger.error(f"Error creating team: {result.status_code}, {result.text}")
                return None
            new_group_id = find_group_id_by_name(self.access_token, self.new_team_name)
            self.logger.info(f"New group id: {new_group_id}")
            get_team_room_info_result = get_team_room_info(self.access_token, new_group_id)
            self.logger.info(f"Get team room info result: {get_team_room_info_result}")
        except Exception as e:
            self.logger.error(f"Error creating team: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None

        # Teamroom copy items
        time.sleep(360)
        self.logger.info(f"--------------------Copying items--------------------")
        try:
            template_group_id = find_group_id_by_name(self.access_token, self.template_team_name)
            self.logger.info(f"Template team id: {template_group_id}")
            new_group_id = find_group_id_by_name(self.access_token, self.new_team_name)
            self.logger.info(f"New group id: {new_group_id}")

            template_site_id = get_site_id_from_group_id(self.access_token, template_group_id)
            self.logger.info(f"Template site id: {template_site_id}")
            new_site_id = get_site_id_from_group_id(self.access_token, new_group_id)
            self.logger.info(f"New site id: {new_site_id}")

            template_root_folder_id = find_general_folder_id(self.access_token, template_site_id)
            self.logger.info(f"Template root folder id: {template_root_folder_id}")
            new_root_folder_id = ensure_general_folder_exists(self.access_token, new_site_id)
            self.logger.info(f"New root folder id: {new_root_folder_id}")

            template_files_and_folders = list_files_in_team(self.access_token, template_site_id, template_root_folder_id)
            self.logger.info(f"Template files and folders: {template_files_and_folders}")

            result_copy_items = copy_items(self.access_token, template_site_id, new_site_id, new_root_folder_id, template_files_and_folders, template_group_id, new_group_id)
            self.logger.info(f"Copy items result: {result_copy_items}")
            # return None
        except Exception as e:
            self.logger.error(f"Error copying items: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None
        

        # Teamroom add OneNote to tab
        time.sleep(20)
        self.logger.info(f"--------------------Adding OneNote--------------------")
        try:
            new_channel_id = get_channel_id_by_name(self.access_token, new_group_id, 'General')
            self.logger.info(f"New channel id: {new_channel_id}")
            existing_onenote_tab = get_existing_onenote_tab(self.access_token, new_group_id, new_channel_id)
            self.logger.info(f"Existing OneNote tab: {existing_onenote_tab}")
            if len(existing_onenote_tab) > 0:
                tab_id = existing_onenote_tab['value'][0]['id']
                self.logger.info(f"Tab id: {tab_id}")
                remove_existing_onenote_tab_result = remove_existing_onenote_tab(self.access_token, new_group_id, new_channel_id, tab_id)
                self.logger.info(f"Remove existing OneNote tab result: {remove_existing_onenote_tab_result}")
            notebook_id = get_notebook_id(self.access_token, new_site_id)
            self.logger.info(f"Notebook id: {notebook_id}")
            file_edit_url = get_file_edit_url(self.access_token, new_site_id, "General/ProjektOneNote")
            self.logger.info(f"File edit url: {file_edit_url}")
            create_onenote_tab_result = create_onenote_tab(self.access_token, new_group_id, new_channel_id, "Notizbuch", file_edit_url)
            self.logger.info(f"Create OneNote tab result: {create_onenote_tab_result}")
        except Exception as e:
            self.logger.error(f"Error adding OneNote to tab: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None
        

        # Teamroom add planner
        time.sleep(60)
        self.logger.info(f"--------------------Adding planner--------------------")
        try:
            template_planner_id = get_planner_ids_for_group(self.access_token, template_group_id)[0]
            self.logger.info(f"Template planner id: {template_planner_id}")
            new_planner_id = create_planner_in_existing_team(self.access_token, new_group_id)
            self.logger.info(f"New planner id: {new_planner_id}")

            tasks, buckets = get_tasks_and_buckets_from_template_planner(self.access_token, template_planner_id)
            self.logger.info(f"Tasks: {tasks}")
            self.logger.info(f"Buckets: {buckets}")

            if not is_planner_already_added_as_tab(self.access_token, new_group_id, new_planner_id):
                add_planner_as_tab_in_default_channel(self.access_token, new_group_id, new_planner_id, self.owner_email)
                self.logger.info(f"Planner added as tab in default channel")

            reverse_buckets = []
            if buckets:
                for i in buckets:
                    reverse_buckets.insert(0, i)
                self.logger.info(f"Reverse buckets: {reverse_buckets}")
            else:
                self.logger.info(f"No buckets found")
                raise Exception("No buckets found")

            for bucket in reverse_buckets:
                new_bucket = create_bucket_in_planner(self.access_token, new_planner_id, bucket['name'])
                self.logger.info(f"New bucket: {new_bucket}")
                for i in range(len(tasks)):
                    if tasks[i]['bucketId'] == bucket['id']:
                        create_task_in_planner(self.access_token, new_planner_id, new_bucket, tasks[i]['title'])
                        self.logger.info(f"Task created: {tasks[i]['title']}")
            self.logger.info(f"Tasks and buckets added to planner")
        except Exception as e:
            self.logger.error(f"Error creating and adding planner: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None


        # Teamroom add excel to tab
        time.sleep(60)
        self.logger.info(f"--------------------Adding excel to tab--------------------")
        try:
            new_channel_id = get_channel_id_by_name(self.access_token, new_group_id, 'General')
            self.logger.info(f"New channel id: {new_channel_id}")
            folder_path = 'General/01 Projektinitiierung und -planung'
            file_name = 'Projektterminplan.xlsx'
            self.logger.info(f"Folder path: {folder_path}")
            self.logger.info(f"File name: {file_name}")

            web_edit_url = get_file_edit_url(self.access_token, new_site_id, folder_path+'/'+file_name)
            self.logger.info(f"Web edit url: {web_edit_url}")
            tab_creation_response = create_editor_tab_with_excel_file(self.access_token, new_group_id, new_channel_id, web_edit_url, "Projektterminplan")
            self.logger.info(f"Tab creation response: {tab_creation_response}")
        except Exception as e:
            self.logger.error(f"Error adding excel to tab: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None
        

        # Teamroom rename Notes column
        time.sleep(10)
        self.logger.info(f"--------------------Renaming notes tab--------------------")
        try:
            note_rename_tab_result = rename_notes_tab_to_notizbuch(self.access_token, new_group_id, new_channel_id)
            self.logger.info(f"Rename notes tab result: {note_rename_tab_result}")
        except Exception as e:
            self.logger.error(f"Error renaming notes tab: {e}")



        # Teamroom create sharepoint lists  
        time.sleep(10)
        self.logger.info(f"--------------------Creating sharepoint lists--------------------")
        try:
            for sp_list in get_all_lists(self.access_token, template_site_id):
                self.logger.info(f"Sharepoint list: {sp_list.get('displayName')}, {sp_list.get('id')}")
                if sp_list.get("id") in ["1b328181-bf17-46bc-8887-1b1e651b8f36", "bf921424-c901-4473-a808-852b92d6aaf5"]:
                    self.logger.info(f"Sharepoint list {sp_list.get('displayName')}")
                    columns = get_list_columns(self.access_token, template_site_id, sp_list.get("id"))
                    self.logger.info(f"Columns: {columns}")
                    result = create_sharepoint_list(self.access_token, new_site_id, sp_list.get("displayName"), columns)
                    self.logger.info(f"Result create Sharepoint list: {result}")
                    if result.json().get("name") == "Entscheidungen":
                        new_column_name = "Titel der Entscheidung"
                        self.logger.info(f"New column name: {new_column_name}")
                    elif result.json().get("name") == "Projektstatus":
                        new_column_name = "Reportingtag"
                        self.logger.info(f"New column name: {new_column_name}")
                    else:
                        new_column_name = "Title"
                    rename_sharepoint_column(self.access_token, new_site_id, result.json().get("id"), "Title", new_column_name)
                    self.logger.info(f"Column renamed")


                    # Teamroom add sharepoint lists to tab
                    time.sleep(60)
                    general_channel_id = get_channel_id_by_name(self.access_token, new_group_id, "General")
                    self.logger.info(f"General channel id: {general_channel_id}")

                    add_sharepoint_list_to_teams_tab_result = add_sharepoint_list_to_teams_tab(self.access_token, new_group_id, get_channel_id_by_name(self.access_token, new_group_id, "General"), sp_list.get("displayName"))
                    self.logger.info(f"Add Sharepoint list to teams tab result: {add_sharepoint_list_to_teams_tab_result}")
        except Exception as e:
            self.logger.error(f"Error creating sharepoint lists: {e}")
            delete_team_result = self.delete_team()
            if delete_team_result == 1:
                self.logger.info(f"Team deleted")
            return None    
            

        # Teamroom add sap link to tab
        # time.sleep(10)
        # try:
        #     tab_creation_response = create_tab(self.access_token, new_group_id, new_channel_id)
        #     self.logger.info(f"SAP-Tab creation response: {tab_creation_response}")
        # except Exception as e:
        #     self.logger.error(f"Error creating sap link tab: {e}")
        #     delete_team_result = self.delete_team()
        #     if delete_team_result == 1:
        #         self.logger.info(f"Team deleted")
        #     return None
        
        self.logger.info(f"Teamroom creation successful")
        # post_message_in_channel_result = post_message_in_channel(self.access_token, new_group_id, new_channel_id, owner_username)
        # self.logger.info(f"Post message in channel result: {post_message_in_channel_result}")
        return {"status_code": 201, "message": "Teamroom creation successful", "group_id": new_group_id, "channel_id": new_channel_id, "project_status_link": f"{get_sharepoint_site_url(self.access_token, new_group_id)}/Lists/Projektstatus/AllItems.aspx", "team_room_link": get_team_room_info_result.get("webUrl")}
    

import schedule
import time

schedule.every().hour.do(run_team_creation)

while True:
    schedule.run_pending()
    time.sleep(1)
# run_team_creation()