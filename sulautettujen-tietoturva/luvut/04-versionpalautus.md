# Versionpalautuksen esto

Allekirjoitus todistaa, että valmistaja on julkaissut kuvan. Se ei
kerro, onko kuva ajantasainen. Jos laiteohjelmiston versiossa 2 on
haavoittuvuus, joka korjataan versiossa 3, hyökkääjä voi asentaa
version 2 takaisin: sekin on aidosti allekirjoitettu.
Versionpalautuksen esto (*anti-rollback*) estää tämän.

## Turvaversio ja monotoninen laskuri

Jokaisessa kuvassa on **turvaversio** (*security version*), joka
nostetaan, kun julkaisu korjaa haavoittuvuuden. Laite muistaa suurimman
hyväksymänsä turvaversion **monotonisessa laskurissa**: arvossa, joka
voi vain kasvaa. Kuva hylätään, jos sen turvaversio on pienempi kuin
laskuri.

Turvaversio on eri asia kuin markkinointiversio. Version 4.2.7
turvaversio voi olla 5, ja korjausjulkaisu 4.2.8 voi pitää sen ennallaan,
jos se ei korjaa haavoittuvuutta. Näin laskuri ei kulu loppuun.

Laskurin vaatimukset ovat tiukat: ohjelmisto ei saa pystyä
pienentämään sitä, eikä se saa nollautua sähkökatkossa tai
flashin pyyhinnässä. Tavallinen flash ei kelpaa, koska sen voi
kirjoittaa uudelleen.

## OTP-laskuri

Mikrokontrollereissa laskuri tehdään usein OTP-muistiin. OTP-bitin
voi polttaa nollasta ykköseksi mutta ei takaisin, joten laskurin
arvoksi otetaan poltettujen bittien määrä (termometrikoodi):

```{.c tiedosto="esimerkit/04-otp-laskuri.c" osa="polta"}
```

```{.c tiedosto="esimerkit/04-otp-laskuri.c" osa="hyvaksy"}
```

```{.tuloste tiedosto="esimerkit/04-otp-laskuri.odotettu"}
```

Termometrikoodin hinta on tila: 64 bittiä riittää 64 nostoon koko
laitteen eliniäksi. Siksi laskuria nostetaan vain turvakorjauksissa.
Käynnistin lukee laskurin samalla tavalla:

```{.c tiedosto="esimerkit/laite/lahde/kaynnistin.c" osa="laskuri"}
```

QEMU-skenaariossa laskurin arvo on 2, ja kuvan versio 1 hylätään,
vaikka allekirjoitus kelpaa:

```{.tuloste tiedosto="esimerkit/laite/testit/palautus.odotettu"}
```

## Milloin laskuri nostetaan

Jos laskuri nostetaan heti, kun uusi kuva on tarkistettu, ja uusi
versio osoittautuu vialliseksi, paluu vanhaan on mahdotonta. Siksi
käynnistin nostaa laskurin vasta, kun uusi versio on **vahvistettu**
toimivaksi (luku 7). Esimerkin käynnistin vain kertoo, mihin arvoon
laskuri nostettaisiin.

## Muut laskurit

| Toteutus | Missä | Huomioitavaa |
|----------|-------|--------------|
| OTP/eFuse | mikrokontrollerit, SoC:t | rajallinen määrä nostoja |
| TPM 2.0:n NV-laskuri | PC:t, palvelimet, osa yhdyskäytävistä | ulkoinen piiri, väylä suojattava |
| eMMC:n RPMB | Linux-laitteet | todennettu muistialue, avain sidottu laitteeseen |
| Turvaelementti | IoT-laitteet | laskuri ja avaimet samassa piirissä |

## Käytännössä

- **Erota turvaversio julkaisuversiosta** ja nosta sitä vain, kun
  julkaisu korjaa haavoittuvuuden.
- **Nosta laskuri vasta vahvistuksen jälkeen**, jotta viallinen
  päivitys voidaan perua.
- **Tarkista laskuri samassa vaiheessa kuin allekirjoitus**:
  käynnistin hylkää liian vanhan kuvan eikä jätä tarkistusta
  sovellukselle.
- **Suojaa myös päivityskanava.** Laite, joka hylkää vanhan kuvan vasta
  latauksen jälkeen, kuluttaa silti akkua ja kaistaa; manifestin
  järjestysnumero (luku 7) torjuu toistetun päivityksen jo ennen
  latausta.

## Itsearviointi

- Osaat selittää, miksi allekirjoitus yksin ei estä haavoittuvan
  version palauttamista.
- Osaat toteuttaa termometrikoodatun laskurin ja arvioida sen
  rajallisuuden.
- Osaat perustella, miksi laskuri nostetaan vasta päivityksen
  vahvistamisen jälkeen.
