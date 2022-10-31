FROM python:3.10-alpine

RUN mkdir /service

RUN apk add openssl --no-cache

COPY protobufs/ /service/protobufs/
COPY vault/ /service/vault/

COPY ca.pem /service/vault/
COPY ca.key /service/vault/

WORKDIR /service/vault

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/vault.proto

RUN openssl req -nodes -newkey rsa:4096 -subj /CN=vault \
    -keyout server.key -out server.csr
RUN --mount=type=secret,id=ca.key \
    openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key \
    -set_serial 1 -out server.pem

EXPOSE 50051
ENTRYPOINT [ "python", "main.py" ]