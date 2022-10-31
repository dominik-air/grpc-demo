import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import grpc
from vault_pb2 import VaultRequest, KeyValuePair, VaultResponse
from vault_pb2_grpc import VaultManagerStub

from recommendations_pb2 import Priority, TaskRequest, TaskResponse
from recommendations_pb2 import Task as gRPC_Task
from recommendations_pb2_grpc import RecommendationManagerStub

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


tasks = [
    Task(
        name="DOPT-2137",
        description="easy task",
        priority=Priority.MEDIUM,
        assignee=None,
    ),
    Task(
        name="DOPT-3777",
        description="hard task",
        priority=Priority.HIGH,
        assignee=None,
    ),
    Task(
        name="DOPT-6527",
        description="somewhat easy task",
        priority=Priority.LOW,
        assignee=None,
    ),
]


def find_task_by_name(task_name: str) -> Task:
    for task in tasks:
        if task_name == task.name:
            return task


def create_grpc_task(task: Task) -> gRPC_Task:
    return gRPC_Task(
        name=task.name, description=task.description, priority=task.priority
    )


def assign_task(assignee: str) -> Task:
    if not assignee:
        raise HTTPException(
            status_code=418, detail="The assignee's name is an empty string."
        )
    if assignee in {task.assignee for task in tasks}:
        raise HTTPException(
            status_code=418, detail=f"{assignee} already has a task to work on."
        )
    open_tasks = [task for task in tasks if task.assignee is None]
    if not open_tasks:
        raise HTTPException(status_code=418, detail="We ran out of tasks!")

    # prepare the remote procedure call
    request = TaskRequest(
        assignee=assignee, open_tasks=[create_grpc_task(task) for task in open_tasks]
    )
    # create a channel and grpc client for the recommendation service
    with open("ca.pem", "rb") as fp:
        ca_cert = fp.read()
    creds = grpc.ssl_channel_credentials(ca_cert)
    channel = grpc.secure_channel("recommendation:50052", creds)
    grpc_client = RecommendationManagerStub(channel)
    # get response from vault grpc server
    print("Sending a TaskRequest.")
    response: TaskResponse = grpc_client.choose_task_for_user(request)
    print("A TaskResponse was received.")

    task = find_task_by_name(response.task.name)
    task.assignee = assignee
    return task


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
    with open("ca.pem", "rb") as fp:
        ca_cert = fp.read()
    creds = grpc.ssl_channel_credentials(ca_cert)
    channel = grpc.secure_channel("vault:50052", creds)
    grpc_client = VaultManagerStub(channel)
    # get response from vault grpc server
    print("Sending a VaultRequest.")
    response: VaultResponse = grpc_client.get_secret(request)
    print(f"Received secrets:")
    print(pretty_format_secrets(response.secrets))


@app.post("/task")
def assign_task_to_user(user: User):
    return assign_task(user.name)
