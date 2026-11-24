# Tyypillisiä virheitä: hadolint löytää ne ennen kuin kuva rakennetaan.
FROM python:latest
RUN apt-get update
RUN apt-get install -y curl
ADD . /app
WORKDIR /app
RUN pip install requests
CMD python api.py
