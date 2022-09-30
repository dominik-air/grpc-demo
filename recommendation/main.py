from concurrent import futures
import random
import grpc
import logging

from recommendations_pb2 import (
    TaskRequest,
    TaskResponse
)
import recommendations_pb2_grpc

# Setup log level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class RecommendationService(recommendations_pb2_grpc.RecommendationManager):
    def choose_task_for_user(self, request: TaskRequest, context):
        logging.info(f'Preparing recommendation for: {request.assignee}.')
        recommendation = random.choice(request.open_tasks)
        logging.info('Sending response to the client.')
        return TaskResponse(task=recommendation)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationManagerServicer_to_server(
        RecommendationService(), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()