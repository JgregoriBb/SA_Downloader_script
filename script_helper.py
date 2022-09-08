# Bb-rest-helper imports.
from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests
# Other imports
import os
import requests
from requests import HTTPError

# A class with the neccesary methods to download attempt files from
# assigments with Safeassign enabled.


class Downloader:

    # This method initializes the Donwloader class, by default handles all that is needed
    # for authentication logging and utils. No arguments are needed.
    def __init__(self):

        self.utils = Bb_Utils()
        self.utils.set_logging()
        self.quick_auth_learn = self.utils.quick_auth(
            './credentials/learn_config.json', 'Learn')
        self.learn_token = self.quick_auth_learn['token']
        self.learn_url = self.quick_auth_learn['url']
        self.reqs = Bb_Requests()

    # Gets all the courses in the target system, due to pagination this method
    # can take time to run. No arguments are needed.
    def get_courses(self):
        self.endpoint = '/learn/api/public/v3/courses'
        self.params = {
            'fields': 'id,name'
        }
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        print(f'{len(self.data)} courses found in the system')
        return self.data

    # This method gets the assessments from the course that have Safeassign enabled.This method takes the course id, if needed to work with the external id
    # pass externalId:course_id
    def get_sa_assessments(self, course_id: str):
        self.endpoint = f'/learn/api/public/v1/courses/{course_id}/contents'
        self.params = {
            'contentHandler': 'resource/x-bb-asmt-test-link',
            'fields': 'id,title,contentHandler.originalityReportingTool,contentHandler.gradeColumnId'}
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        self.sa_assessment_list = []
        for self.d in self.data:
            if (self.d['contentHandler']['originalityReportingTool']['id'] ==
                    'safeAssign' and self.d['contentHandler']['originalityReportingTool']['checkSubmission']):
                self.assesment_data = {
                    "id": self.d['id'],
                    "title": self.d['title'],
                    "columnId": self.d['contentHandler']['gradeColumnId']
                }
                self.sa_assessment_list.append(self.assesment_data)
        return self.sa_assessment_list

    # This method gets the attemps for an assigment, it takes the course Id
    # and the grade column Id as arguments
    def get_attempts(self, course_id: str, column_id: str):
        self.endpoint = f'/learn/api/public/v2/courses/{course_id}/gradebook/columns/{column_id}/attempts'
        self.params = {
            'fields': 'id,userId'
        }
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        return self.data

    # This method gets the Attempt file metadata. Takes the course Id and
    # attempt Id as arguments.
    def get_file_metadata(self, course_id: str, attempt_id: str):
        self.endpoint = f'/learn/api/public/v1/courses/{course_id}/gradebook/attempts/{attempt_id}/files'
        self.data = self.reqs.Bb_GET(
            self.learn_url, self.endpoint, self.learn_token)
        return self.data

    # This method downloads the Attempt file. It takes course Id, attempt Id,
    # attempt file ID, and file name as arguments. This method has been
    # written directly with the requests module to allow access to the binary
    # from the response.
    def download_file(
            self,
            course_id: str,
            attempt_id: str,
            attempt_file_id: str,
            file_name: str):
        self.headers = {
            'Authorization': f'Bearer {self.learn_token}',
            'Content-Type': "Application/json"
        }
        self.endpoint = f'/learn/api/public/v1/courses/{course_id}/gradebook/attempts/{attempt_id}/files/{attempt_file_id}/download'
        self.request_url = f'{self.learn_url}{self.endpoint}'
        try:
            self.data = requests.get(
                self.request_url, headers=self.headers)
            self.data.raise_for_status()
            open(file_name, 'wb').write(self.data.content)
        except requests.exceptions.HTTPError as e:
            print(repr(e))

# A class with convenience tools for folder and file management


class Tools(Exception):
    # Checks if a folder exists, if it does not, it will be created and set as
    # current working directory. Skips if folder already exists, but sets the
    # folder as cwd
    def create_folder(self, path):
        try:
            os.makedirs(path, 0o777)
            os.chdir(path)
        except FileExistsError:
            print('[Donwloader]Folder already exists.')
            os.chdir(path)
    
