import os
import logging
from pprint import pformat
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import grpc
from vault_pb2 import VaultRequest, KeyValuePair, VaultResponse
from vault_pb2_grpc import VaultManagerStub

import recommendations_pb2
from recommendations_pb2 import Priority, TaskRequest, TaskResponse
from recommendations_pb2 import Task as gRPC_Task
from recommendations_pb2_grpc import RecommendationManagerStub

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")

# Setup log level
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    name: str


class Task(BaseModel):
    name: str
    description: str
    priority: int
    assignee: None | str


PRIORITY_MAP = {
    recommendations_pb2.LOW: Priority.LOW,
    recommendations_pb2.MEDIUM: Priority.MEDIUM,
    recommendations_pb2.HIGH: Priority.HIGH,
}


def get_tasks_from_document_db() -> list[Task]:
    doc_tasks = MongoClient(MONGODB_URI).jira.tasks
    return [create_task_from_document(doc) for doc in doc_tasks.find()]


def create_task_from_document(document: dict[str, str]) -> Task:
    return Task(
        name=document["name"],
        description=document["description"],
        priority=PRIORITY_MAP[document["priority"]],
        assignee=document["assignee"],
    )


def update_task_assignee_in_db(task: Task) -> None:
    MongoClient(MONGODB_URI).jira.tasks.update_one(
        {"name": task.name}, {"$set": {"assignee": task.assignee}}
    )


def find_task_by_name(tasks: list[Task], task_name: str) -> Task:
    for task in tasks:
        if task_name == task.name:
            return task


def create_grpc_task(task: Task) -> gRPC_Task:
    return gRPC_Task(
        name=task.name, description=task.description, priority=task.priority
    )


def is_assignee_a_valid_name(assignee: str) -> None:
    if not assignee:
        raise HTTPException(
            status_code=418, detail="The assignee's name is an empty string."
        )


def is_assignee_free(tasks: list[Task], assignee: str) -> None:
    if assignee in {task.assignee for task in tasks}:
        raise HTTPException(
            status_code=418, detail=f"{assignee} already has a task to work on."
        )


def find_open_tasks(tasks: list[Task]) -> list[Task]:
    open_tasks = [task for task in tasks if task.assignee is None]
    if not open_tasks:
        raise HTTPException(status_code=418, detail="We ran out of tasks!")
    return open_tasks


def assign_task(open_tasks: list[Task], assignee: str) -> Task:
    # prepare the remote procedure call
    request = TaskRequest(
        assignee=assignee, open_tasks=[create_grpc_task(task) for task in open_tasks]
    )
    # create a channel and grpc client for the recommendation service
    ca_cert = read_secret(secret_file="ca.pem")
    creds = grpc.ssl_channel_credentials(ca_cert)
    channel = grpc.secure_channel("recommendation:50052", creds)
    grpc_client = RecommendationManagerStub(channel)
    # get response from vault grpc server
    logging.info("Sending a TaskRequest.")
    response: TaskResponse = grpc_client.choose_task_for_user(request)
    logging.info("A TaskResponse was received.")
    task = find_task_by_name(open_tasks, response.task.name)
    task.assignee = assignee
    return task


def read_secret(secret_file: str) -> bytes:
    with open(secret_file, "rb") as fp:
        return fp.read()


def pretty_format_secrets(secrets: list[KeyValuePair]) -> str:
    pretty_format = ""
    for secret in secrets:
        pretty_format += f"key={secret.key} : value={secret.value}\n"
    return pretty_format


@app.on_event("startup")
def example_vault_call():
    token = os.getenv("VAULT_TOKEN")
    request = VaultRequest(vault_token=token, requested_secret="sbx/devops")
    # create a channel and grpc client for vault
    ca_cert = read_secret(secret_file="ca.pem")
    creds = grpc.ssl_channel_credentials(ca_cert)
    channel = grpc.secure_channel("vault:50051", creds)
    grpc_client = VaultManagerStub(channel)
    # get response from vault grpc server
    logging.info("Sending a VaultRequest.")
    response: VaultResponse = grpc_client.get_secret(request)
    logging.info(f"Received secrets:")
    logging.info(pretty_format_secrets(response.secrets))


@app.post("/task")
def assign_task_to_user(user: User):
    logging.debug("Entered task endpoint")
    tasks = get_tasks_from_document_db()
    logging.debug("Got tasks from db")
    for task in tasks:
        logging.debug(pformat(task))
    logging.debug("Header guards")
    is_assignee_a_valid_name(assignee=user.name)
    is_assignee_free(tasks, assignee=user.name)
    open_tasks = find_open_tasks(tasks)
    logging.debug("Found open tasks")
    task = assign_task(open_tasks, assignee=user.name)
    logging.debug("Task assigned")
    update_task_assignee_in_db(task)
    logging.debug("Updated db")
    return task
