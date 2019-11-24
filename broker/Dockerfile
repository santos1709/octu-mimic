FROM python:3.7
WORKDIR /usr/src/app-data

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY broker.py .

CMD [ "python", "broker.py" ]
