from script_helper import Downloader
from script_helper import Tools
import csv
import os


class Csv_Gen():

    def __init__(self):
        self.downloader = Downloader()
        self.downloader.authenticate()

    def generate_file_original(self):
        self.original_courses = self.downloader.get_courses_original()
        try:
            with open('./input_files/original.csv', 'w', newline='') as csvfile:
                self.fieldnames = [
                    'course_id',
                    'external_id',
                    'ultraStatus',
                    'course_name']
                self.writer = csv.DictWriter(csvfile, self.fieldnames)
                self.writer.writeheader()
                for self.c in self.original_courses:
                    self.writer.writerow(
                        {
                            'course_id': self.c["id"],
                            'external_id': self.c["externalId"],
                            'ultraStatus': self.c["ultraStatus"],
                            'course_name': self.c["name"]})
        except FileExistsError:
            print('[DOWNLOADER][CSV_GEN] File already exists')

    def generate_file_ultra(self):
        self.ultra_courses = self.downloader.get_courses_ultra()
        try:
            with open('./input_files/ultra.csv', 'w', newline='') as csvfile:
                self.fieldnames = [
                    'course_id',
                    'external_id',
                    'ultraStatus',
                    'course_name']
                self.writer = csv.DictWriter(csvfile, self.fieldnames)
                self.writer.writeheader()
                for self.c in self.ultra_courses:
                    self.writer.writerow(
                        {
                            'course_id': self.c["id"],
                            'external_id': self.c["externalId"],
                            'ultraStatus': self.c["ultraStatus"],
                            'course_name': self.c["name"]})
        except FileExistsError:
            print('[DOWNLOADER][CSV_GEN] File already exists')


if __name__ == "__main__":
    file_gen = Csv_Gen()
    tools = Tools()
    tools.create_folder('./input_files')
    os.chdir('../')
    file_gen.generate_file_ultra()
    file_gen.generate_file_original()
    os.chdir('../')
