FROM python:3.10-alpine

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY recommendation/ /service/recommendation/
WORKDIR /service/recommendation
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
    --grpc_python_out=. ../protobufs/recommendations.proto

EXPOSE 50052
ENTRYPOINT [ "python", "main.py" ]