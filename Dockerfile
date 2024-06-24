FROM python:3.11.6-slim

RUN mkdir -p /mad_test
WORKDIR /mad_test

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .
COPY . .