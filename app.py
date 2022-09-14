from alive_progress import alive_it
from script_helper import Downloader
from script_helper import Tools
import os


def main():
    downloader = Downloader()
    tools = Tools()
    tools.create_folder('./sa_submissions')
    print('[DOWNLOADER] Processing Original courses.')
    original_courses = downloader.get_courses_original()
    print(
        f'[DOWNLOADER] {len(original_courses)} Original courses found in the system.')
    for c in alive_it(original_courses):
        content_areas = downloader.get_top_content_original(c['id'])
        if content_areas:
            print('[DOWNLOADER] Retrieving content areas.')
            for ca in content_areas:
                assessments = downloader.get_sa_assessments_original(
                    c['id'], ca['id'])
                if assessments:
                    print('[DOWNLOADER] Retrieving asessments.')
                    for a in assessments:
                        attempts = downloader.get_attempts(
                            c['id'], a['columnId'])
                        if attempts:
                            print('[DOWNLOADER] Retrieving attempts.')
                            for at in attempts:
                                metadata = downloader.get_file_metadata(
                                    c['id'], at['id'])
                                if metadata:
                                    print(
                                        '[DOWNLOADER] Retrieving file metadata and downloading file.')
                                    tools.create_folder(
                                        f'{c["id"]}_{c["ultraStatus"]}_{c["name"]}')
                                    tools.create_folder(
                                        f'./{c["id"]}_{a["id"]}__{a["title"]}')
                                    name = f'{at["userId"]}_{metadata[0]["name"]}'
                                    file = downloader.download_file(
                                        c['id'], at['id'], metadata[0]['id'], name)
                                    os.chdir('../..')
    print('[DOWNLOADER] safeAssign assignments download complete for original courses')
    ultra_courses = downloader.get_courses_ultra()
    for c in alive_it(ultra_courses):
        print(f'[Downloader] Finding assessments for course {c["id"]}')
        assesments = downloader.get_sa_assessments(c['id'])
        if assesments:
            for a in assesments:
                print(
                    f'[Downloader] Finding attempts for assessment {a["id"]}')
                attempts = downloader.get_attempts(c['id'], a['columnId'])
                if attempts:
                    for at in attempts:
                        print(
                            f'[Downloader] Finding metadata for attempt {at["id"]}')
                        metadata = downloader.get_file_metadata(
                            c["id"], at["id"])
                        if metadata:
                            print(
                                '[DOWNLOADER] Retrieving file metadata and downloading file.')
                            tools.create_folder(
                                f'{c["id"]}_{c["ultraStatus"]}_{c["name"]}')
                            tools.create_folder(
                                f'./{c["id"]}_{a["id"]}__{a["title"]}')
                            name = f'{at["userId"]}_{metadata[0]["name"]}'
                            file = downloader.download_file(
                                c['id'], at['id'], metadata[0]['id'], name)
                            os.chdir('../..')
    print(
        f'[DOWNLOADER] {len(original_courses)} Ultra courses found in the system.')
    ultra(ultra_courses)


if __name__ == "__main__":
    main()
