from script_helper import Downloader
from script_helper import Tools
import os


def main():
    downloader = Downloader()
    tools = Tools()
    tools.create_folder('./sa_submissions')
    print('********************************')
    print('[Downloader] Iniciating downloader script.')
    print(
        f'[Downloader] Files and folders will be placed under >> {os.getcwd()}')
    print('[Downloader] Getting course information from the system, this may take a couple of minutes. ')
    courses = downloader.get_courses()
    print(
        f'[Downloader] {len(courses)} found in the system')

    for c in courses:
        print(f'[Downloader] Finding assessments for course {c["id"]}')
        assesments = downloader.get_sa_assessments(c['id'])
        if assesments:
            for a in assesments:
                print(
                    f'[Downloader] Finding attempts for assessment {a["id"]}')
                attempts = downloader.get_attempts(c['id'], a['columnId'])
                for at in attempts:
                    print(
                        f'[Downloader] Finding metadata for attempt {at["id"]}')
                    metadata = downloader.get_file_metadata(c["id"], at["id"])

                    if metadata:
                        tools.create_folder(
                            f'./{c["id"]}_{a["id"]}_{a["title"]}')
                        name = f'{at["userId"]}_{metadata[0]["name"]}'
                        file = downloader.download_file(
                            c['id'], at['id'], metadata[0]['id'], name)
                        os.chdir('..')


if __name__ == "__main__":
    main()
