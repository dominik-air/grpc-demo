FROM python:3.10-alpine

RUN apk --no-cache add build-base
WORKDIR /app
COPY ./web-client /app
EXPOSE 9000

CMD ["python3", "-u", "-m", "http.server", "--bind", "0.0.0.0", "9000"]