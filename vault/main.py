from concurrent import futures
import grpc
import logging

from vault_pb2 import VaultRequest, VaultResponse, KeyValuePair
import vault_pb2_grpc

# Setup log level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class VaultService(vault_pb2_grpc.VaultManagerServicer):
    def get_secret(self, request: VaultRequest, context):
        logging.info(f"Provided token: '{request.vault_token}' is correct.")
        logging.info(f"Getting secrets from Vault...")
        username = KeyValuePair(key="username", value="admin")
        password = KeyValuePair(key="password", value="admin123")
        hostname = KeyValuePair(key="host", value="AWS")
        logging.info("Sending response to the client.")
        return VaultResponse(secrets=[username, password, hostname])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_VaultManagerServicer_to_server(VaultService(), server)

    with open("server.key", "rb") as fp:
        server_key = fp.read()
    with open("server.pem", "rb") as fp:
        server_cert = fp.read()

    creds = grpc.ssl_server_credentials([(server_key, server_cert)])
    server.add_secure_port("[::]:50051", creds)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
