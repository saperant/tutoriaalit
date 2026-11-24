"""Miksi komento annetaan listana eikä merkkijonona: tiedostonimi,
jossa on välilyönti tai komentotulkin erikoismerkkejä."""

import shlex
import subprocess

# @alku lainaus
nimi = "raportti; echo HYÖKKÄYS"        # esim. käyttäjän syöttämä nimi

# Väärin: merkkijono komentotulkille. ';' aloittaa uuden komennon.
vaarin = subprocess.run(f"printf '%s\\n' {nimi}", shell=True,
                        capture_output=True, text=True, check=False)
print("shell=True:", vaarin.stdout.splitlines())

# Oikein: lista, ei komentotulkkia. Argumentti välittyy sellaisenaan.
oikein = subprocess.run(["printf", "%s\\n", nimi],
                        capture_output=True, text=True, check=True)
print("lista:     ", oikein.stdout.splitlines())

# Jos komentotulkkia on pakko käyttää (putket), lainaa jokainen arvo.
turvallinen = f"printf '%s\\n' {shlex.quote(nimi)} | tr a-z A-Z"
putki = subprocess.run(turvallinen, shell=True, capture_output=True,
                       text=True, check=True)
print("quote:     ", putki.stdout.splitlines())
print("lokiin:    ", shlex.join(["sim", "--testi", nimi]))
# @loppu lainaus
