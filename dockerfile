FROM python:3.7.4-alpine

WORKDIR /server

COPY ./server /server

RUN pip install -r /server/requirements.txt

EXPOSE 8080

CMD [ "python", "/server/main.py"]