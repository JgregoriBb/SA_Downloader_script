# Submission downloader script for Blackboard Learn

This script runs through Blackboard Learn Courses and downloads student sumbissions for assessesments that have the Safeassign anti-plagiarisim tool enabled. A folder is created for each assignment and the user Id is included in the file name for further processing.

We have upddated the script to run from a csv file instead of running through all the courses. This allow to have more control over the courses that are included and also allow to run the script in batches.

Now we also offer a functionality to generate the csv files for original and ultra courses.

This script has not been tested for windows computers.

> :warning: This script now supports Original (Classic) and Ultra courses, however, it does consume more API calls, when using in production, make sure to contact Blackboard Support and request the API call rate to be raised (default for dev apps is 10k)

## Setup

This script was created in Python 3, make sure python3 is installed and working in your system. Here are the steps to make it work.

1. Download or clone the repository.
2. Create a virtual environment and activate it.

```Python
#env creation
python3 -m venv env

#env activation
source env/bin/activate
```

3.Install dependencies, either from 'requirements.txt' or manually.

```Python
#dependencies from requeriments.txt
pip3 install -r requeriments.txt

#dependencies manually
pip3 install Bb-rest-helper
pip3 install alive_progress
````

5.In the developer portal, register a new application and retrieve the KEY and SECRET values. Configure this application in Learn with an user with sufficient priviledges to

* Read course information.
* Read assessment information.
* Read attempt information

>:warning: Do NOT use an admin user to register your application!

>:warning: Make sure to log a ticket to raise the API rate

More information can be found in Anthology´s [developer 
documentation page](https://docs.anthology.com/rest-apis/learn/getting-started/registry)

4.Within root, create a folder called **credentials** inside of that folder, create a file named **learn.config.json** and fill it with the following template with the KEY and SECRET values.

```json
{
    "url":"Learn Server url",
    "key":"KEY from dev portal",
    "secret":"SECRET from dev portal"
}
```

## Usage

### csv file generation

csv files for original and ultra courses can be automatically generated. to do so, run the following command

```Python
Python3 csv_gen.py
```

This will call the courses API, create a folder under the root of the application called **input_files** with two files inside, **original.csv** and **ultra.csv**.The structure is simple.

```csv
course_id,ultraStatus,course_name
```

Feel free to add/remove courses, or to split in different files for batch processing. As long as you don't alter file name of file strucure the application will run from the content of the files.

>:warning: if you choose NOT to use **csv_gen.py** and generate the files in a different way, you need to create the **input_files** folder manually.

### Running the main script.

Once setup is complete, the script can be run from a terminal.

1. Open a terminal and navegate to the root directory

2. Run the script with Python3

```Python
Python3 app.py
```

## Script results

By default, the script will create a folder called 'sa_submissions' in the root folder of the application.

After that, the script will create a folder for each of the courses where there are safeAssign enabled assessments with files to download, the folder name follows the following convention.

```csv
course_id_ultraStatus_course_name
```

Whithin this folder, one folder will be created for each one of the assessments with the following naming convention.

```csv
course_id_assessment_id_assesment_name
 ```

Whitin this folder, the files will be downloaded with the following naming convention.

```csv
user_id_file_name_extension 
```

