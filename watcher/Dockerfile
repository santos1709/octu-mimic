FROM python:3.6-stretch
WORKDIR /usr/src/app
ARG CALLCOUNT

COPY . .
ENV CALLCOUNT 0
RUN export CALLCOUNT=0

CMD [ "python", "watcher.py" ]
