from fastapi import HTTPException


def raise_if_http_error(var):
    if is_http_error(var):
        raise var


def is_http_error(var):
    if isinstance(var, HTTPException):
        return True

    return False
