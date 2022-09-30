FROM python:3.10-alpine

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY main-server/ /service/main-server/
WORKDIR /service/main-server

RUN python -m pip install --upgrade pip --no-cache-dir
RUN python -m pip install -r requirements.txt --no-cache-dir

RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/recommendations.proto
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/vault.proto

ENV VAULT_TOKEN VaultToken
EXPOSE 12345

CMD ["python3", "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12345"]