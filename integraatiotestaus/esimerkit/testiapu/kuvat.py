"""Testeissä käytettävät konttikuvat.

Docker Hub rajoittaa nimettömiä latauksia, joten kuvat haetaan
oletuksena Googlen peilistä mirror.gcr.io. Peilin voi vaihtaa
ympäristömuuttujalla TESTIKUVAT_PEILI (esim. yrityksen oma rekisteri).
Versiot on lukittu: päivitys on tietoinen muutos, ei sattuma.
"""

from __future__ import annotations

import os

# @alku kuvat
PEILI = os.environ.get("TESTIKUVAT_PEILI", "mirror.gcr.io/")
POSTGRES = PEILI + "library/postgres:16-alpine"
REDIS = PEILI + "library/redis:7.2-alpine"
# Testcontainersin siivoojakontti (Ryuk) poistaa kontit, jos testiajo
# kaatuu ennen kuin ne ehditään pysäyttää.
RYUK = PEILI + "testcontainers/ryuk:0.8.1"
APUKUVA = "integraatiotestaus-apukuva:1"
# @loppu kuvat
