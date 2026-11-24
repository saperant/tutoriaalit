# Testien apupalvelut: hintapalvelun väärennös ja vikaproxy.
# Pohjakuva haetaan Docker Hubin Google-peilistä (ks. luku 10).
FROM mirror.gcr.io/library/python:3.12-alpine
WORKDIR /app
COPY hintapalvelu.py vikaproxy.py ./
USER nobody
EXPOSE 8080 8474 8666
CMD ["python3", "-u", "hintapalvelu.py"]
