"""Komentoinjektio käytännössä: sama syöte komentotulkin kautta."""

import subprocess

syote = "Aino; echo HYOKKAAJAN KOMENTO AJETTIIN"

# @alku hyokkays
# VIRHE: komentotulkki tulkitsee puolipisteen komentojen erottimeksi.
tulos = subprocess.run(f"echo Hei {syote}", shell=True,  # noqa: S602
                       capture_output=True, text=True, check=True)
print(tulos.stdout, end="")
# @loppu hyokkays
