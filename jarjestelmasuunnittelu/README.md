# Skaalautuvien järjestelmien suunnittelu

Suurten palvelujärjestelmien arkkitehtuuri arvioista toteutukseen:
selkäpuolen laskut, latenssi ja kapasiteetti, kuormantasaus,
konsistentti hajautus ja osiointi, välimuistit, tietokannan
replikointi, viestijonot, ylikuorma ja uudelleenyritysmyrskyt,
saatavuus sekä havaittavuus. Lopuksi lyhytosoitepalvelu suunnitellaan
ja ajetaan HAProxyn, Redisin ja PostgreSQLin kanssa. Valmis dokumentti:
[jarjestelmasuunnittelu.pdf](https://saperant.github.io/tutoriaalit/materiaalit/jarjestelmasuunnittelu.pdf),
pikaopas:
[jarjestelmasuunnittelu-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/jarjestelmasuunnittelu-pikaopas.pdf).

Esitiedot: taidot *Hajautetut järjestelmät* ja *SQL ja
relaatiotietokannat*.

## Sisältö

1. Johdanto – menetelmä, esimerkkijärjestelmät, mitä testataan
2. Vaatimukset ja arviot – selkäpuolen laskut, mittaluokat
3. Suorituskyky ja skaalautuvuus – persentiilit, häntälatenssi,
   Littlen laki, Erlangin C, pysty- ja vaakaskaalaus
4. Kuormantasaus – L4 ja L7, algoritmit, HAProxy ja palvelimen
   kaatuminen, elävyys ja valmius
5. Konsistentti hajautus ja osiointi – rengas, rendezvous, avainalueet
   ja tiiviste, kuumat avaimet
6. Välimuistit – strategiat, invalidointi ja vuokrat, ryntäys,
   häätöpolitiikat
7. Tietokantojen skaalaus ja replikointi – lukureplikat, lue omat
   kirjoituksesi, synkroninen replikointi, yhteysaltaat
8. Viestijonot ja asynkroninen käsittely – kuorman tasaus, Redis
   Streams, idempotentti kuluttaja, vastapaine
9. Ylikuorma ja vikojen leviäminen – token bucket, uudelleenyritys-
   myrsky, kuorman pudotus, laipiot
10. Saatavuus ja luotettavuus – sarjaan ja rinnan, vikaantumisalueet,
    RTO ja RPO, virhebudjetti
11. Monitorointi ja havaittavuus – RED ja USE, histogrammit,
    Prometheus, jäljitys, hälytykset
12. Suunnitteluharjoitus: lyhytosoitepalvelu
13. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/`:

- `jarjestelma/` – yhteinen koodi: palvelujen käynnistys prosesseina,
  Redis-asiakas, hajautus, rajoitin, histogrammi, välimuisti ja
  esimerkkipalvelut (myös lyhytosoitepalvelu)
- `luku02/` … `luku12/` – lukujen laskelmat, simulaatiot ja kokeet
  sekä niiden odotetut tulosteet
- `luku12/compose.yaml`, `luku12/Dockerfile` – sama palvelu kontteina
- `testit/` – yksikkötestit

```text
make -C esimerkit                  # tarkistukset ja kaikki esimerkit
make -C esimerkit luku04/haproxy_vika
```

Esimerkit tarvitsevat ohjelmat `redis-server`, `haproxy` ja
PostgreSQL 16:n sekä Python-paketin psycopg. Ne käynnistetään
väliaikaishakemistoihin ja vapaisiin portteihin, kuuntelevat vain
osoitetta 127.0.0.1 ja pysäytetään lopuksi. Kehityskontissa
(`.devcontainer/jarjestelmasuunnittelu`) kaikki on valmiina.

Lisenssi: CC BY-SA 4.0.
