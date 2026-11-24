# Ohjelmistoradio

Tiivis suomenkielinen tutoriaali ohjelmistoradion vastaanotinketjuista:
IQ-näytteet ja tallennusmuodot (cu8, ci16, cf32, SigMF), laitteen
epäideaalisuuksien korjaus (tasakomponentti, IQ-epätasapaino, AGC,
kiteen virhe), NCO ja kanavan valinta monivaiheisella desimoinnilla ja
polyfaasipankilla, FM-stereovastaanotin pilotin vaihelukolla ja
RDS-tyyppisellä datalla, GFSK-pakettivastaanotin sekä lohkoittainen
reaaliaikakäsittely C++:lla. Lopuksi esitellään GNU Radio, laitteet,
herkkyyslaskelmat ja radiolupasäännöt. Kaikki tallenteet ovat
synteettisiä ja toistettavia. Valmiit dokumentit:
[sdr.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sdr.pdf)
ja pikaopas
[sdr-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sdr-pikaopas.pdf).

## Sisältö

1. Johdanto – SDR:n rakenne, synteettiset tallenteet, kaistan spektri
2. IQ-näytteet ja tallennusmuodot – cu8, ci16, cf32, SigMF, ADC:n
   dynamiikka ja ylikuormitus
3. Radion epäideaalisuudet – DC-piikki, IQ-epätasapaino, AGC, ppm
4. NCO, sekoitus ja kanavan valinta – vaiheakkumulaattori,
   monivaiheinen desimointi, polyfaasisuodinpankki
5. FM-demodulointi – ilmaisimet, kynnysilmiö, jälkikorostus, WAV
6. Stereo ja RDS – MPX, pilotin PLL, stereodekooderi, RDS-lohkot
7. Digitaalinen pakettivastaanotin – GFSK, haku, taajuusvirhe, CRC
8. Reaaliaikainen lohkokäsittely C++:lla – tila, itsetesti, putki,
   vertailu Python-viitteeseen
9. GNU Radio – lohkokaaviot, lohkon sopimus, testattava logiikka
10. Laitteet ja radiolupasäännöt – RTL-SDR, HackRF, Pluto,
    herkkyys, väylä, Traficom
11. Lopuksi – nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, C++ (GCC, Clang,
              # sanitoijat), esimerkkien ajot ja pytest
make pdf      # sdr.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
make -C esimerkit mittaa   # C++-ketjun läpäisy (ei testi)
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla (NumPy, SciPy) sekä
C++23-kääntäjällä (GCC 14 tai Clang 20). Tarkistukseen tarvitaan ruff,
mypy, scipy-stubs ja pytest (kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.
