
from ploy_app.ploy_app.allot import validate_files_space_limit, validate_db_space_limit

def daily():
    validate_files_space_limit()
    validate_db_space_limit()