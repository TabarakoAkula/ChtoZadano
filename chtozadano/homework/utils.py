import json

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

BASE_DIR = settings.BASE_DIR


def get_user_subjects(grade, letter):
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
            return [json_subject_data[i] for i in user_subjects]


def get_user_subjects_abbreviation(grade, letter):
    grades_subjects_url = staticfiles_storage.url("grades_subjects.json")
    with open(str(BASE_DIR) + grades_subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        return json_data[str(grade)][letter]["subject_codes"]


def get_abbreviation_from_name(abbreviation):
    subjects_url = staticfiles_storage.url("subjects.json")
    with open(str(BASE_DIR) + subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        for i in json_data:
            if json_data[i].lower() == abbreviation.lower():
                return i
    return "ERROR"
