FROM python:3.10-alpine

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY vault/ /service/vault/
WORKDIR /service/vault
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/vault.proto

EXPOSE 50051
ENTRYPOINT [ "python", "main.py" ]