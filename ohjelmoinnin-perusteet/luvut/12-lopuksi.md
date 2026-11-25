# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

**Nimet ja rakenne**

- Nimi kertoo merkityksen ja tarvittaessa yksikön: `hinta_snt`,
  `kesto_s`. Vakiot isoilla kirjaimilla, ei taikanumeroita.
- Funktio tekee yhden asian, palauttaa tuloksen eikä tulosta sitä.
- Pääohjelma funktioon `main` ja `if __name__ == "__main__":`.
- Yksi moduli, yksi aihe.

**Data**

- Valitse kokoelma käytön mukaan: haku avaimella sanakirja, jäsenyys
  joukko, jono lista, kiinteä ryhmä dataluokka.
- Raha kokonaislukuina sentteinä tai `Decimal`-tyyppinä.
- Muutettava kokoelma on jaettu kaikkien siihen viittaavien kesken.

**Syöte ja virheet**

- Syöte on tekstiä, ja se tarkistetaan ja jäsennetään reunalla.
- Tiedostot `with open(..., encoding="utf-8")`, CSV `csv`-modulilla.
- Nosta poikkeus kuvaavalla viestillä; sieppaa vain poikkeukset, jotka
  osaat käsitellä. Älä niele virheitä.

**Työtapa**

- Esimerkit ja testit ennen koodia tai sen rinnalla.
- Pienet askeleet: aja ruff, mypy ja testit jokaisen muutoksen
  jälkeen.
- Ensin toimiva, sitten siisti.

## Jatkotaidot

Ohjelmoinnin perusteista avautuvat muun muassa:

- *Python*: idiomaattinen Python ohjelmoinnin osaavalle:
  iteraattorit, tyypitys, kontekstinhallinta, rinnakkaisuus ja hinnat.
- *Tietorakenteet* ja *Algoritmit*: miten tehokkaat ohjelmat
  rakennetaan ja miten niiden suoritusaika arvioidaan.
- *Komentorivi ja Linux* ja *Versionhallinta (Git)*: jokaisen
  ohjelmoijan päivittäiset työkalut.
- *SQL ja relaatiotietokannat*: tiedon tallentaminen ja kyselyt.
- *C-kieli*: miten tietokone toimii lähempänä laitteistoa.
- *Funktionaalinen ohjelmointi (Racket)*: toinen tapa ajatella
  ohjelmia.

## Lähteet ja jatkolukeminen

Pythonin virallinen dokumentaatio on lisensoitu PSF:n lisenssillä.
Muut lähteet ovat linkkejä; niiden sisältöä ei ole kopioitu tähän
teokseen.

- *The Python Tutorial*. Python Software Foundation.
  <https://docs.python.org/3/tutorial/>
- *The Python Standard Library*. Python Software Foundation.
  <https://docs.python.org/3/library/>
- *PEP 8 – Style Guide for Python Code*.
  <https://peps.python.org/pep-0008/>
- Ohjelmoinnin MOOC (Python). Helsingin yliopisto. Suomenkielinen
  kurssi tehtävineen ja automaattisine tarkistuksineen.
  <https://www.mooc.fi/>
- Allen B. Downey: *Think Python*, 3. painos. O'Reilly, 2024. Vapaasti
  luettavissa: <https://allendowney.github.io/ThinkPython/>
- Al Sweigart: *Automate the Boring Stuff with Python*. No Starch
  Press. Käytännön automaatiotehtäviä. Vapaasti luettavissa:
  <https://automatetheboringstuff.com/>
- *pytest documentation*. <https://docs.pytest.org/>
- *Ruff* ja *mypy*: <https://docs.astral.sh/ruff/>,
  <https://mypy.readthedocs.io/>

### Työkalut

| Tarkoitus | Työkalu |
|-----------|---------|
| Editori | Visual Studio Code ja Python-laajennus, PyCharm, Thonny (aloittelijoille) |
| Tarkistus | `ruff check`, `mypy` |
| Testaus | `pytest` |
| Virheiden etsintä | `breakpoint()`, editorin debuggeri |
| Kokeilut | `python3` (REPL) |
