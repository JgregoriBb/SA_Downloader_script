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
import json
import logging
import time
import datetime
import csv


# A class with the neccesary methods to download attempt files from
# assigments with Safeassign enabled. Works for Original and Ultra courses
class Downloader:

    # This method initializes the Donwloader class, by default handles all that is needed
    # for authentication logging and utils. No arguments are needed.
    def __init__(self):
        # remove logging for pruduction
        #self.utils = Bb_Utils()
        #self.utils.set_logging()
        self.conf = Get_Config('./credentials/learn_config.json')
        self.learn_url = self.conf.get_url()
        self.learn_token = None
        self.reqs = Bb_Requests()

    # Method that returns True when the token expires.

    def token_is_expired(self, expiration_datetime):
        time_left = (expiration_datetime -
                     datetime.datetime.now()).total_seconds()
        if time_left < 1:
            time.sleep(1)
            return True
        else:
            return False

    # Using this method instead of default for Bb-rest-helper auth to better handle
    # token expiration, this will be updated in the library so this method is not needed.
    def authenticate(self):
        self.endpoint = "/learn/api/public/v1/oauth2/token"
        self.params = {"grant_type": "client_credentials"}
        self.headers = {
            'Content-Type': "application/x-www-form-urlencoded"}

        try:
            if self.learn_token == None:
                
                r = requests.request(
                    "POST",
                    self.learn_url +
                    self.endpoint,
                    headers=self.headers,
                    params=self.params,
                    auth=(
                        self.conf.get_key(),
                        self.conf.get_secret()))
                r.raise_for_status()
                self.data = json.loads(r.text)
                self.learn_token = self.data["access_token"]
                self.expires = self.data["expires_in"]
                m, s = divmod(self.expires, 60)
                self.now = datetime.datetime.now()
                self.expires_at = self.now + \
                    datetime.timedelta(seconds=s, minutes=m)
                logging.info("Learn Authentication successful")
                logging.info("Token expires at: " + str(self.expires_at))
                # return self.learn_token

            elif self.token_is_expired(self.expires_at):
                print('refresh token')
                r = requests.request(
                    "POST",
                    self.learn_url +
                    self.endpoint,
                    headers=self.headers,
                    params=self.params,
                    auth=(
                        self.conf.get_key(),
                        self.conf.get_secret()))
                r.raise_for_status()
                self.data = json.loads(r.text)
                self.learn_token = self.data["access_token"]
                self.expires = self.data["expires_in"]
                m, s = divmod(self.expires, 60)
                self.now = datetime.datetime.now()
                self.expires_at = self.now + \
                    datetime.timedelta(seconds=s, minutes=m)
                logging.info("Learn Authentication successful")
                logging.info("Token expires at: " + str(self.expires_at))

        except requests.exceptions.HTTPError as e:
            data = json.loads(r.text)
            logging.error(data["error_description"])

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
            'recursive': True,
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
            'recursive': True,
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

    def read_from_csv(self, course_exp: str, path: str):
        self.path = path
        self.course_exp = course_exp
        self.original_courses = []
        self.ultra_courses = []
        if self.course_exp == "original":
            try:
                with open(self.path,'r', newline='') as csvfile:
                    self.reader = csv.DictReader(csvfile)
                    for self.row in self.reader:
                        self.data_to_append = {
                            "id":self.row["course_id"],
                            "ultraStatus":self.row["ultraStatus"],
                            "name":self.row["course_name"]     
                                }
                        self.original_courses.append(self.data_to_append)
                    return self.original_courses
            except FileNotFoundError:
                print('[DOWNLOADER] file not found!')
        elif self.course_exp == "ultra":
            try:
                with open(path,'r', newline='') as csvfile:
                    self.reader = csv.DictReader(csvfile)
                    for self.row in self.reader:
                        self.data_to_append = {
                            "id":self.row["course_id"],
                            "ultraStatus":self.row["ultraStatus"],
                            "name":self.row["course_name"]     
                                }
                        self.ultra_courses.append(self.data_to_append)
                    return self.ultra_courses
            except FileNotFoundError:
                print('[DOWNLOADER] file not found!')
        else:
            print('[DOWNLOADER] Invalid value, use "original" or "ultra"')
