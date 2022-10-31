import os
import logging
from pprint import pformat
from pymongo import MongoClient

MONGODB_URI = "mongodb://localhost:27017/"
if os.getenv("MONGODB_URI"):
    MONGODB_URI = os.getenv("MONGODB_URI")

# Setup log level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

TASKS = [
    {
        "name": "DOPT-2137",
        "description": "high complexity but not so time consuming task",
        "priority": 1,
        "assignee": None,
    },
    {
        "name": "DOPT-3777",
        "description": "really time consuming task with low complexity",
        "priority": 2,
        "assignee": None,
    },
    {
        "name": "DOPT-6527",
        "description": "somewhat easy task",
        "priority": 0,
        "assignee": None,
    },
]


def populate_db():
    logging.info("Inserting sample data...")
    MongoClient(MONGODB_URI).jira.tasks.insert_many(TASKS)


def show_db_contents():
    logging.info("Data check...")
    for task in MongoClient(MONGODB_URI).jira.tasks.find():
        logging.info(pformat(task))


if __name__ == "__main__":
    logging.info("Setting MongoDB up...")
    populate_db()
    show_db_contents()
    logging.info("Job has finished successfully.")
