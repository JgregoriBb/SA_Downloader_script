# Bb-rest-helper imports.
from Bb_rest_helper import Bb_Utils
from Bb_rest_helper import Get_Config
from Bb_rest_helper import Auth_Helper
from Bb_rest_helper import Bb_Requests
# Other imports
import os
import requests
from requests import HTTPError
from alive_progress import alive_bar


# A class with the neccesary methods to download attempt files from
# assigments with Safeassign enabled. Works for Original and Ultra courses
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

    # This method returns a list with all the Ultra courses in the target system, due to pagination this method
    # can take time to run. No arguments are needed.
    def get_courses_ultra(self):
        self.endpoint = '/learn/api/public/v3/courses'
        self.params = {
            'fields': 'id,name,ultraStatus',
            'organization': False
        }
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        self.ultra_course_list = []
        self.original_course_list = []
        for self.d in (self.data):
            if self.d['ultraStatus'] == "Ultra":
                self.ultra_course_list.append(self.d)
        return self.ultra_course_list

    # This method returns a list with all the Original courses in the target system, due to pagination this method
    # can take time to run. No arguments are needed.
    def get_courses_original(self):
        self.endpoint = '/learn/api/public/v3/courses'
        self.params = {
            'fields': 'id,name,ultraStatus',
            'organization': False
        }
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        self.ultra_course_list = []
        self.original_course_list = []
        for self.d in self.data:
            if self.d['ultraStatus'] == "Classic":
                self.original_course_list.append(self.d)
        return self.original_course_list

    # This method returns a list with the assessments from Ultra courses that
    # have safeAssign enabled.This method takes the course id as an argument.
    def get_sa_assessments_ultra(self, course_id: str):
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
                    "course_id": course_id,
                    "id": self.d['id'],
                    "title": self.d['title'],
                    "columnId": self.d['contentHandler']['gradeColumnId']
                }
                self.sa_assessment_list.append(self.assesment_data)
        return self.sa_assessment_list

    # This method returns a list with the id of content areas for original courses, where assessments
    # will be located.
    def get_top_content_original(self, course_id: str):
        self.content_area_list = []
        self.endpoint = f'/learn/api/public/v1/courses/{course_id}/contents'
        self.params = {
            'fields': 'id'
        }
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        for self.d in self.data:
            if self.d['id']:
                self.content_area_data = {
                    'id': self.d['id']
                }
                self.content_area_list.append(self.content_area_data)
        return self.content_area_list

    # This method returns a list with the assessments from Original courses
    # that have safeAssign enabled.This method takes the course id and the
    # parent content area as an argument.
    def get_sa_assessments_original(
            self,
            course_id: str,
            content_area_id: str):
        self.sa_assessment_list = []
        self.endpoint = f'/learn/api/public/v1/courses/{course_id}/contents/{content_area_id}/children'
        self.params = {
            'contentHandler': 'resource/x-bb-assignment',
            'fields': 'id,title,contentHandler.originalityReportingTool,contentHandler.gradeColumnId'}
        self.data = self.reqs.Bb_GET(
            self.learn_url,
            self.endpoint,
            self.learn_token,
            self.params)
        for self.d in self.data:
            try:
                if (self.d['contentHandler']['originalityReportingTool']['id'] ==
                        'safeAssign' and self.d['contentHandler']['originalityReportingTool']['checkSubmission']):
                    self.assesment_data = {
                        "course_id": course_id,
                        "id": self.d['id'],
                        "title": self.d['title'],
                        "columnId": self.d['contentHandler']['gradeColumnId']
                    }
                    self.sa_assessment_list.append(self.assesment_data)

            except BaseException:
                pass

        return self.sa_assessment_list

    # This method returns a list with the attemps for any assigment, it takes the course Id
    # and the grade column Id as arguments.
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

    # This method returns a list with the attempt file metadata. It takes the course Id and
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
            print('[DOWNLOADER]File could not be found, try manual download.')


# A class with convenience tools for folder management.
class Tools(Exception):
    # Checks if a folder exists, if it does not, it will be created and set as
    # current working directory. Skips if folder already exists, but sets the
    # folder as cwd
    def create_folder(self, path):
        try:
            os.makedirs(path, 0o777)
            os.chdir(path)
        except FileExistsError:
            os.chdir(path)
