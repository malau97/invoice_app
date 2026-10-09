import os

APP_FOLDER = os.path.dirname(__file__)

DATA_FOLDER = os.path.join(APP_FOLDER, "data")

REPORT_FOLDER = os.path.join(DATA_FOLDER, "reports")

DATABASE = os.path.join(DATA_FOLDER, "invoice.db")

os.makedirs(DATA_FOLDER, exist_ok=True)

os.makedirs(REPORT_FOLDER, exist_ok=True)