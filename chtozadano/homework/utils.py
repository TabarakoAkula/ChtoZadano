import json

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage

import homework.models

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


def save_files(request_files_list):
    files_list_for_model = []
    for r_file in request_files_list:
        file_extension = r_file.name.split(".")[-1]
        if file_extension.lower() in ["png", "jpeg", "webp", "gif", "jpg"]:
            file_name = default_storage.save(
                f"homework/img/{r_file.name}",
                r_file,
            )
            files_list_for_model.append((file_name, "img"))
        elif file_extension.lower() in [
            "pdf",
            "ppt",
            "pptx",
            "doc",
            "docx",
            "zip",
        ]:
            file_name = default_storage.save(
                f"homework/files/{r_file.name}",
                r_file,
            )
            files_list_for_model.append((file_name, "file"))
        elif file_extension.lower() in ["mp3", "ogg", "acc", "wav"]:
            file_name = default_storage.save(
                f"homework/music/{r_file.name}",
                r_file,
            )
            files_list_for_model.append((file_name, "music"))
        else:
            return "Error", file_extension
    return "Ok", files_list_for_model


def get_user_from_grade(grade, letter):
    return homework.models.Homework.objects.filter(
        grade=grade,
        letter=letter,
    ).all()
