import os
import random
import grpc
import logging
from concurrent import futures

import recommendations_pb2_grpc
from recommendations_pb2 import TaskRequest, TaskResponse

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Setup log level
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def read_secret(secret_file: str) -> bytes:
    with open(secret_file, "rb") as fp:
        return fp.read()


class RecommendationService(recommendations_pb2_grpc.RecommendationManager):
    def choose_task_for_user(self, request: TaskRequest, context):
        logging.info(f"Preparing recommendation for: {request.assignee}.")
        recommendation = random.choice(request.open_tasks)
        logging.info("Sending response to the client.")
        return TaskResponse(task=recommendation)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationManagerServicer_to_server(
        RecommendationService(), server
    )

    server_key = read_secret(secret_file="server.key")
    server_cert = read_secret(secret_file="server.pem")

    creds = grpc.ssl_server_credentials([(server_key, server_cert)])
    server.add_secure_port("[::]:50052", creds)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
