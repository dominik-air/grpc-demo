FROM python:3.10-alpine

COPY init-db/ /job/
WORKDIR /job/

RUN python -m pip install --upgrade pip --no-cache-dir
RUN python -m pip install -r requirements.txt --no-cache-dir

CMD [ "python", "main.py"]