# Lyhytosoitepalvelun konttikuva. Rakennetaan esimerkit-hakemistosta:
#   docker build -f luku12/Dockerfile -t lyhyt:1.0.0 .
FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir "psycopg[binary]==3.3.9"

WORKDIR /palvelu
COPY jarjestelma/ ./jarjestelma/
USER 10001
EXPOSE 8000
ENTRYPOINT ["python3", "-m", "jarjestelma.lyhyt"]
