from alive_progress import alive_it
from script_helper import Downloader
from script_helper import Tools
import os
import csv


def main():
    downloader = Downloader()
    tools = Tools()
    original_courses = tools.read_from_csv(
        'original', './input_files/original.csv')
    ultra_courses = tools.read_from_csv(
        'ultra', './input_files/ultra_course_id.csv')

    tools.create_folder('./sa_submissions')

    print('[DOWNLOADER] Starting script')
    print('[DOWNLOADER] Processing Original courses.')
    print(
        f'[DOWNLOADER] {len(original_courses)} Original courses found in the system.')
    for c in alive_it(original_courses):
        print(
            f'[Downloader] Searching assessments for course {c["external_id"]}')
        downloader.authenticate()
        content_areas = downloader.get_top_content_original(c['id'])
        if content_areas:
            print(
                f'->[DOWNLOADER] Searching content areas for course: {c["external_id"]}')
            for ca in content_areas:
                downloader.authenticate()
                assessments = downloader.get_sa_assessments_original(
                    c['id'], ca['id'])
                if assessments:
                    print(
                        f'-->[DOWNLOADER] Searching asessments for course: {c["external_id"]}')
                    for a in assessments:
                        print(f'--->[DOWNLOADER] Assessment {a["id"]} found')
                        downloader.authenticate()
                        attempts = downloader.get_attempts(
                            c['id'], a['columnId'])
                        if attempts:
                            print(
                                f'---->[DOWNLOADER] Searching attempts for assessment {a["id"]}')
                            for at in attempts:
                                print(
                                    f'----->[DOWNLOADER] Attempt {at["id"]} found ')
                                downloader.authenticate()
                                metadata = downloader.get_file_metadata(
                                    c['id'], at['id'])
                                if metadata:
                                    print(
                                        '------>[DOWNLOADER] Searching file metadata and downloading file.')
                                    tools.create_folder(
                                        f'{c["id"]}_{c["ultraStatus"]}_{c["external_id"]}')
                                    tools.create_folder(
                                        f'./Assessment_{c["id"]}_{c["external_id"]}_{a["id"]}')
                                    name = f'{at["userId"]}_{metadata[0]["name"]}'
                                    file = downloader.download_file(
                                        c['id'], at['id'], metadata[0]['id'], name)
                                    os.chdir('../..')
    print('[DOWNLOADER] safeAssign assignments download complete for original courses')
    print('[DOWNLOADER] Processing Ultra courses.')
    print(
        f'[DOWNLOADER] {len(ultra_courses)} Ultra courses found in the system.')
    for c in alive_it(ultra_courses):
        print(
            f'-->[DOWNLOADER] Searching asessments for course: {c["external_id"]}')
        assesments = downloader.get_sa_assessments_ultra(c['id'])
        if assesments:
            print(
                f'-->[DOWNLOADER] Searching asessments for course: {c["external_id"]}')
            for a in assesments:
                print(f'--->[DOWNLOADER] Assessment {a["id"]} found')
                attempts = downloader.get_attempts(c['id'], a['columnId'])
                if attempts:
                    print(
                        f'---->[DOWNLOADER] Searching attempts for assessment {a["id"]}')
                    for at in attempts:
                        print(f'----->[DOWNLOADER] Attempt {at["id"]} found ')
                        metadata = downloader.get_file_metadata(
                            c["id"], at["id"])
                        if metadata:
                            print('------>[DOWNLOADER] Searching file metadata and downloading file.')
                            tools.create_folder(f'{c["id"]}_{c["ultraStatus"]}_{c["external_id"]}')
                            tools.create_folder(f'./Assessment_{c["id"]}_{c["external_id"]}_{a["id"]}')
                            name = f'{at["userId"]}_{metadata[0]["name"]}'
                            file = downloader.download_file(c['id'], at['id'], metadata[0]['id'], name)
                            os.chdir('../..')

        print('[DOWNLOADER] safeAssign assignments download complete for ultra courses')


if __name__ == "__main__":
    main()
