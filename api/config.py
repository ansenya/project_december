import logging
import os

DATABASE_URL = os.environ.get('DATABASE_URL')


def check():
    if not DATABASE_URL:
        logging.error('Database URL not defined')
        return False
    return True