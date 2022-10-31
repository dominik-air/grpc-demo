FROM python:3.10-alpine

RUN mkdir /service

COPY protobufs/ /service/protobufs/
COPY recommendation/ /service/recommendation/

COPY ca.pem /service/recommendation/
COPY ca.key /service/recommendation

WORKDIR /service/recommendation

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/recommendations.proto

RUN apk add openssl --no-cache

RUN openssl req -nodes -newkey rsa:4096 -subj /CN=recommendation \
    -keyout server.key -out server.csr
RUN --mount=type=secret,id=ca.key \
    openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key \
    -set_serial 1 -out server.pem

EXPOSE 50052
ENTRYPOINT [ "python", "main.py" ]