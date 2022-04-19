from shutil import copyfileobj
from os import stat, path, remove

from fastapi import UploadFile


def is_file_size_more_that(file: UploadFile, size: int) -> bool:
    ''' size in Kilobytes'''
    return (len(file.file.read()) / 1024 > size)


def is_file_image(file: UploadFile) -> bool:
    return check_file_type(file, "image/png")


def check_file_type(file: UploadFile, type: str):
    if file.content_type != type:
        return False

    return True


def save_file(file: UploadFile, directory: str, filename: str):
    with open(directory + "/" + filename, "wb") as new_file:
        copyfileobj(file.file, new_file)
        file.file.close()


def delete_file(directory: str, filename: str) -> bool:
    remove(directory + "/" + filename)


def is_file_exists(directory: str, filename: str) -> bool:
    if path.exists(directory + "/" + filename):
        return True
    return False
