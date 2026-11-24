# Käyntilaskurin kuva. Vaiheet: perus -> testit, perus -> ajo.
#   docker build --target testit sovellus     ajaa yksikkötestit
#   docker build --target ajo -t kaynnit sovellus

# @alku perus
# Peruskuva kiinnitetään tagilla ja digestillä: tagi kertoo lukijalle
# version, digest takaa, että kuva on tavu tavulta sama joka kerta.
# Digest on pitkä, joten rivi jatkuu kenoviivalla.
FROM docker.io/library/python:3.12-slim@sha256:\
37fc60d303cb9294d3718b5b48998a0210bb1c73611c1399ef5eb7964c0536e5 \
    AS perus
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
# @loppu perus

# @alku testit
FROM perus AS testit
COPY . .
RUN python -m unittest -q
# @loppu testit

# @alku ajo
FROM perus AS ajo
ARG VERSIO=kehitys
LABEL org.opencontainers.image.title="kaynnit" \
      org.opencontainers.image.version="${VERSIO}" \
      org.opencontainers.image.licenses="CC-BY-SA-4.0"
# Ajossa ei tarvita testejä: kopioidaan vain sovelluksen tiedostot.
COPY yhteinen.py api.py laskuri.py terveys.py ./
# Oma käyttäjä ilman kotihakemistoa ja kuorta; ei root-oikeuksia.
# Datahakemisto kuuluu käyttäjälle: uusi nimetty volyymi saa
# omistajansa ja oikeutensa kuvan hakemistosta.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin \
        palvelu \
    && mkdir /data \
    && chown 10001:10001 /data
USER 10001
ENV VERSIO=${VERSIO} \
    PORTTI=8080
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \
    CMD ["python", "terveys.py"]
# Exec-muoto: Python on PID 1 ja saa SIGTERMin suoraan.
ENTRYPOINT ["python"]
CMD ["api.py"]
# @loppu ajo
