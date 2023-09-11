FROM python:3.8-slim-buster AS base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  && apt-get install -y build-essential libffi-dev python3-dev \
  && apt-get install -y libcairo2-dev \
  && apt-get install -y libpango1.0-dev \
  && apt-get install -y libgdal-dev \
  && apt-get install -y git

# Requirements install
COPY ./requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["/entrypoint"]