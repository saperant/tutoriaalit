# Rinnakkaisuus {.runko-rinnakkaisuus}

Pythonissa on kolme rinnakkaisuuden mallia: säikeet, prosessit ja
`asyncio`. Oikea valinta riippuu siitä, odottaako ohjelma (I/O) vai
laskeeko se (CPU), ja ratkaisevana tekijänä on CPythonin globaali
tulkkilukko. Rinnakkaisuuden yleiset käsitteet, kuten kilpatilanteet,
lukot ja lukkiutumat, ovat taidossa *Rinnakkaisohjelmointi*; tämä luku
keskittyy Pythonin välineisiin ja niiden hintoihin.

## Globaali tulkkilukko

CPythonin *GIL* (*global interpreter lock*) sallii vain yhden säikeen
suorittaa Python-tavukoodia kerrallaan. Lukko yksinkertaistaa tulkin
toteutusta ja viitelaskentaa, ja se tekee yksisäikeisestä koodista
nopeaa. Seuraukset:

- **Säikeet eivät nopeuta Python-laskentaa.** Neljä säiettä laskemassa
  alkulukuja on yhtä hidas kuin yksi, usein hitaampi.
- **Säikeet sopivat odottamiseen.** GIL vapautuu I/O-kutsun ajaksi
  (verkko, tiedostot, `time.sleep`) ja monissa C-kirjastoissa (NumPy,
  hashlib, zlib) raskaan laskennan ajaksi.
- **GIL ei tee koodista säieturvallista.** Säikeiden vaihto voi tapahtua
  minkä tahansa tavukoodikäskyn välissä, joten `laskuri += 1` (luku,
  lisäys, tallennus) voi hukata päivityksiä. Jaettu tila suojataan
  lukolla kuten muissakin kielissä.

Python 3.13 toi kokeellisen *GIL-vapaan* version (`python3.13t`, PEP 703),
ja 3.14:ssä se on virallisesti tuettu mutta ei vielä oletus. Siinä
säikeet suorittavat Python-koodia aidosti rinnakkain, mutta
yksisäikeinen koodi on hieman hitaampaa ja kaikki C-laajennukset eivät
vielä tue sitä. Tämän luvun ohjeet pätevät molemmissa; GIL-vapaassa
versiossa lukkojen tarve vain korostuu.

## Säikeet I/O-työhön

`concurrent.futures.ThreadPoolExecutor` on korkean tason rajapinta
säiejoukkoon. `map` jakaa tehtävät säikeille ja palauttaa tulokset
syötteen järjestyksessä:

```{.python tiedosto="esimerkit/12-saikeet.py" osa="saikeet"}
```

Kahdeksan 0,2 sekunnin odotusta valmistuu yhteensä noin 0,2 sekunnissa,
koska säikeet odottavat yhtä aikaa. Esimerkki tulostaa vain vertailun
tuloksen, jotta tuloste on toistettava. `with`-lause odottaa kaikkien
tehtävien valmistumista ja sulkee joukon. `submit` palauttaa
`Future`-olion, ja `as_completed` antaa tulokset valmistumisjärjestyksessä.
Tehtävässä noussut poikkeus nousee uudelleen, kun tulosta pyydetään.

Jaettu muuttuva tila suojataan lukolla, ja lukko otetaan
`with`-lauseella, jolloin se vapautuu myös poikkeuksessa:

```{.python tiedosto="esimerkit/12-saikeet.py" osa="lukko"}
```

```{.tuloste tiedosto="esimerkit/12-saikeet.odotettu"}
```

Lukkoa parempi ratkaisu on usein olla jakamatta tilaa: säikeet
palauttavat tuloksensa, ja pääsäie yhdistää ne. Säikeiden välinen
viestintä tehdään `queue.Queue`-jonolla, joka on valmiiksi
säieturvallinen.

## Prosessit laskentaan

`ProcessPoolExecutor` ajaa tehtävät erillisissä prosesseissa, joilla
kullakin on oma tulkkinsa ja oma GIL. Laskenta skaalautuu ytimien
määrän mukaan:

```{.python tiedosto="esimerkit/12-prosessit.py" osa="prosessit"}
```

```{.tuloste tiedosto="esimerkit/12-prosessit.odotettu"}
```

- Argumentit ja tulokset siirretään prosessien välillä sarjallistettuina
  (`pickle`). Funktion on oltava moduulitason funktio, ja siirrettävän
  datan on oltava pientä suhteessa laskentaan. Työ jaetaan siksi
  isoihin paloihin; tässä neljä väliä alkioiden sijaan.
- `if __name__ == "__main__":` on pakollinen. Käynnistystavasta riippuen
  (`spawn` macOS:ssä ja Windowsissa, Linuxissa 3.14:stä alkaen
  `forkserver`) lapsiprosessi tuo pääohjelman moduulin, ja ilman
  vartijaa se käynnistäisi uuden joukon.
- Prosessin käynnistys maksaa kymmeniä millisekunteja, joten joukko
  luodaan kerran ja sitä käytetään uudelleen.

Kun laskenta on numeerista, NumPy tai muu C-kirjasto on usein parempi
ratkaisu kuin prosessit: vektoroitu operaatio on yksiprosessisenakin
moninkertaisesti nopeampi kuin Python-silmukka.

## asyncio

`asyncio` on yksisäikeinen tapahtumasilmukka. `async def` määrittelee
*korutiinin*, ja `await` luovuttaa suorituksen silmukalle, kunnes
odotettava asia on valmis. Koska vuoron vaihto tapahtuu vain
`await`-kohdissa, jaettua tilaa ei tarvitse lukita niiden välissä.
Yksi säie hallitsee tuhansia samanaikaisia yhteyksiä, kun säikeitä
tarvittaisiin yksi yhteyttä kohden.

```{.python tiedosto="esimerkit/12-asyncio.py" osa="asyncio"}
```

```{.tuloste tiedosto="esimerkit/12-asyncio.odotettu"}
```

- `asyncio.run` käynnistää tapahtumasilmukan ja ajaa pääkorutiinin.
- `gather` ajaa korutiinit samanaikaisesti. `return_exceptions=True`
  palauttaa poikkeukset tulosten joukossa, jolloin yksi epäonnistuminen
  ei peruuta muita.
- `Semaphore` rajaa samanaikaisuuden: 100 pyyntöä, enintään 10
  kerrallaan. Ilman rajaa palvelin tai oma yhteysjoukko ylikuormittuu.
- `asyncio.timeout` (3.11) peruuttaa lohkon, jos se ei valmistu ajassa.

`asyncio.TaskGroup` (3.11) on *rakenteellisen samanaikaisuuden* väline:
`async with asyncio.TaskGroup() as tg:` -lohkossa luodut tehtävät
odotetaan lohkon lopussa, ja jos yksi epäonnistuu, muut peruutetaan ja
virheet nostetaan `ExceptionGroup`-ryhmänä (luku 10). Se on oletus, kun
kaikkien tehtävien on onnistuttava; `gather` palautuksineen, kun
osittainen tulos kelpaa.

Asynkroninen koodi vaatii asynkroniset kirjastot (`httpx`, `asyncpg`,
`aiofiles`). Tavallinen estävä kutsu kuten `time.sleep` tai
`requests.get` korutiinissa pysäyttää koko tapahtumasilmukan.
Välttämätön estävä kutsu siirretään säikeeseen
`await asyncio.to_thread(funktio, ...)`-kutsulla.

## Mallin valinta

| Työ | Malli | Perustelu |
|-----|-------|-----------|
| Kymmeniä I/O-tehtäviä, estävät kirjastot | `ThreadPoolExecutor` | yksinkertainen, toimii olemassa olevan koodin kanssa |
| Tuhansia yhteyksiä, verkkopalvelu | `asyncio` | pieni hinta per tehtävä, ei lukkoja |
| Python-laskenta | `ProcessPoolExecutor` | ohittaa GIL:n |
| Numeerinen laskenta | NumPy, Numba, C-laajennus | vektorointi vapauttaa GIL:n |
| Taustatyöt palvelussa | työjono (Celery, RQ) | erillinen prosessi, uudelleenyritys |

## Käytännössä

- **Valitse malli työn mukaan:** odotus säikeillä tai `asyncio`-
  silmukalla, laskenta prosesseilla tai C-kirjastolla. Säikeet
  laskentaan on Pythonin yleisin rinnakkaisuusvirhe.
- **Korkean tason rajapinnat.** `concurrent.futures` ja `asyncio`
  hoitavat joukot, tulokset ja poikkeukset. `threading.Thread` ja
  `multiprocessing.Process` suoraan vain erikoistapauksissa.
- **Älä jaa muuttuvaa tilaa.** Tehtävät palauttavat tuloksia, ja
  viestintä kulkee jonojen kautta. Jos tila on jaettava, se kapseloidaan
  luokkaan, joka omistaa lukon (kuten `Laskuri`).
- **Rajaa samanaikaisuus** säiejoukon koolla tai semaforilla, ja anna
  jokaiselle ulkoiselle kutsulle aikaraja.
- **Rakenteellinen samanaikaisuus:** `TaskGroup` ja `with`-lohkot
  varmistavat, ettei tehtäviä jää orvoiksi.
- **Hinta:** säikeen luonti ja vaihto ovat kohtuullisia, mutta GIL:n
  kilpailu voi hidastaa laskentaa säikeissä. Prosessin käynnistys ja
  `pickle`-sarjallistus maksavat; korutiini on kevein, noin kilotavu
  muistia.
- **Sudenkuopat:** estävä kutsu korutiinissa, puuttuva
  `__main__`-vartija prosessien kanssa, lambda tai sisäfunktio
  `ProcessPoolExecutor`-tehtävänä (ei sarjallistu) ja tehtävän
  poikkeus, jota ei koskaan noudeta `Future`-oliosta.

## Itsearviointi

- Osaat selittää, mitä GIL estää ja mitä se ei estä, ja mitä
  GIL-vapaa Python muuttaa.
- Osaat ajaa I/O-tehtäviä rinnakkain `ThreadPoolExecutor`-joukolla ja
  suojata jaetun tilan lukolla.
- Osaat jakaa laskennan prosesseille `ProcessPoolExecutor`-joukolla ja
  tiedät, miksi `__main__`-vartija ja isot työpalat tarvitaan.
- Osaat kirjoittaa `asyncio`-ohjelman, joka rajaa samanaikaisuuden
  semaforilla ja käsittelee virheet ja aikarajat.
- Osaat valita mallin työn luonteen perusteella ja perustella valinnan.
