import json

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

BASE_DIR = settings.BASE_DIR


def get_user_subjects(grade, letter, group):
    grades_subjects_url = staticfiles_storage.url("grades_subjects.json")
    subjects_url = staticfiles_storage.url("subjects.json")
    with open(
        str(BASE_DIR) + grades_subjects_url,
        encoding="utf-8",
    ) as data:
        json_data = json.loads(data.read())
        user_subjects = json_data[str(grade)][letter]["subject_codes"]
        with open(
            str(BASE_DIR) + subjects_url,
            encoding="utf-8",
        ) as subjects_data:
            json_subject_data = json.loads(subjects_data.read())
            response = []
            for i in user_subjects:
                if i in ["eng1", "eng2", "ger1", "ger2", "ikt1", "ikt2"]:
                    i_group = int(i[-1:])
                    if i_group != group:
                        continue
                    if isinstance(json_subject_data[i], list):
                        response.append(json_subject_data[i][0])
                    else:
                        response.append(json_subject_data[i])
                else:
                    if isinstance(json_subject_data[i], list):
                        response.append(json_subject_data[i][0])
                    else:
                        response.append(json_subject_data[i])
    return response


def get_user_subjects_abbreviation(grade, letter):
    grades_subjects_url = staticfiles_storage.url("grades_subjects.json")
    with open(str(BASE_DIR) + grades_subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        return json_data[str(grade)][letter]["subject_codes"]


def get_abbreviation_from_name(name):
    subjects_url = staticfiles_storage.url("subjects.json")
    with open(str(BASE_DIR) + subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        for i in json_data:
            if isinstance(json_data[i], list):
                for j in range(len(json_data[i])):
                    if json_data[i][j].lower() == name.lower():
                        return i
            elif json_data[i].lower() == name.lower():
                return i
    return "ERROR"


def get_name_from_abbreviation(abbreviation):
    subjects_url = staticfiles_storage.url("subjects.json")
    with open(str(BASE_DIR) + subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        response_object = json_data[abbreviation]
        if isinstance(response_object, list):
            return response_object[0]
        return response_object
