FROM python:3.6-alpine
RUN apk add gcc musl-dev && pip install pipenv

COPY Pipfile /opt
WORKDIR /opt
RUN pipenv lock --requirements > requirements.txt && \
    pip install -r /opt/requirements.txt && \
    pip install gunicorn

ADD constable/ /opt/constable

ENV FLASK_APP=/opt/constable/constable.py
ENV PORT=5000
WORKDIR /opt/constable
CMD exec gunicorn -b :$PORT constable:app
