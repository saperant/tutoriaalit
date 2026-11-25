# Kuormantasaus

Kuormantasaaja (*load balancer*) jakaa pyynnöt usealle palvelimelle ja
piilottaa ne asiakkaalta yhden osoitteen taakse. Se tekee kolme asiaa:
valitsee palvelimen jokaiselle pyynnölle tai yhteydelle, tarkkailee
palvelinten terveyttä ja ohjaa liikenteen pois kaatuneilta. Kun
sovelluskerros on tilaton (luku 3), kuormantasaaja tekee palvelimista
vaihdettavia: niitä voi lisätä, poistaa ja päivittää yksi kerrallaan
ilman käyttökatkoa.

## Kerros 4 ja kerros 7

| Ominaisuus  | Kerros 4 (TCP/UDP)                     | Kerros 7 (HTTP)                      |
|-------------|----------------------------------------|--------------------------------------|
| näkee | osoitteet ja portit | metodin, polun, otsakkeet, evästeet |
| tasaa | yhteyksiä | pyyntöjä |
| reititys | osoitteen ja portin mukaan | polun, isännän tai otsakkeen mukaan |
| TLS | kulkee läpi | yleensä puretaan tasaajassa |
| hinta | pieni, voi olla ytimessä tai laitteessa | protokollan jäsennys |
| esimerkkejä | IPVS, Maglev, pilven verkkotasaajat | HAProxy, nginx, Envoy, pilven sovellustasaajat |

Kerros 4 on nopea ja yksinkertainen, mutta pitkäikäinen yhteys pysyy
samalla palvelimella: jos asiakas käyttää yhtä HTTP/2- tai gRPC-yhteyttä
kaikkiin pyyntöihinsä, kaikki pyynnöt päätyvät yhdelle palvelimelle.
Kerros 7 tasaa jokaisen pyynnön erikseen, osaa yrittää pyyntöä
uudelleen toisella palvelimella ja reitittää polun mukaan eri
palveluille. Suuret järjestelmät käyttävät usein molempia: kerroksen 4
tasaajat jakavat liikenteen kerroksen 7 tasaajien joukolle.

Myös asiakas voi tasata itse (*client-side load balancing*): se saa
palvelinlistan palveluhausta (DNS, Consul, Kubernetesin palvelut) ja
valitsee palvelimen itse. Väliin ei tarvita omaa hyppyä, mutta jokainen
asiakas tarvitsee saman logiikan; palveluverkko (*service mesh*)
siirtää sen sivuvaunuun (taito *Palveluarkkitehtuurit*).

## Algoritmit

Algoritmin valinta ratkaisee, kun palvelimet tai pyynnöt eivät ole
samanlaisia. Simulaatiossa on neljä palvelinta, joista yksi on puolet
hitaampi. Kuorma on 75 % yhteisestä kapasiteetista:

```{.python tiedosto="esimerkit/luku04/algoritmit.py" osa="valitsimet"}
```

```{.tuloste tiedosto="esimerkit/luku04/algoritmit.odotettu"}
```

![Sama simulaatio kuvana. Hidas palvelin ehtii käsitellä 19 %
kuormasta (katkoviiva); algoritmit, jotka antavat sille enemmän,
kasvattavat sen jonoa rajatta, ja p99 on satoja kertoja
suurempi.](kuvat/tasaus.png){width=85%}

Kierto (*round robin*) ja satunnainen valinta antavat hitaalle
palvelimelle neljänneksen pyynnöistä, eli 66 pyyntöä sekunnissa, kun se
ehtii 50. Sen jono kasvaa koko simulaation ajan, ja p99 on lähes minuutti,
vaikka järjestelmässä on kapasiteettia yli 80 pyyntöä sekunnissa
vapaana. Painotettu kierto korjaa tilanteen, jos painot tiedetään
etukäteen ja pysyvät oikeina. *Vähiten kesken* (*least connections*)
mukautuu itse: hidas palvelin kerää keskeneräisiä pyyntöjä ja saa siksi
vähemmän uusia. *Kahden satunnaisen valinta* (*power of two choices*)
pääsee lähelle sitä, vaikka se katsoo vain kahta palvelinta. Se on
tärkeää, kun tasaajia on monta eikä mikään niistä näe kaikkien
palvelinten tilaa ajantasaisesti.

Lisäksi on algoritmeja, jotka sitovat avaimen palvelimeen: lähdeosoitteen
tai evästeen tiiviste ja konsistentti hajautus (luku 5). Niitä
käytetään, kun palvelimella on avainkohtaista tilaa, kuten paikallinen
välimuisti tai WebSocket-yhteys.

## Terveystarkistukset ja kaatuminen

HAProxy tarkistaa palvelimen terveyden kutsumalla sen
terveyspäätepistettä säännöllisesti. Asetukset kertovat, kuinka nopeasti
kaatuminen huomataan ja kuinka varovasti palvelin palautetaan:

```{.text tiedosto="esimerkit/luku04/haproxy.cfg" osa="palvelu"}
```

`inter 200ms fall 2` merkitsee palvelimen alas kahden peräkkäisen
epäonnistuneen tarkistuksen jälkeen, eli noin 0,4 sekunnissa. `rise 2`
palauttaa sen vasta kahden onnistuneen jälkeen, jotta juuri käynnistyvä
tai vaihteleva palvelin ei saa liikennettä liian aikaisin. Tuotannossa
väli on tyypillisesti 1–5 sekuntia; tiheä tarkistus huomaa vian nopeasti
mutta kuormittaa palvelimia ja reagoi hetkellisiin hikkoihin.

```{.ajoituskaavio otsikko="Asetusten inter 200ms, fall 2 ja rise 2 vaikutus: yksi ruutu on 100 ms. Kaatumisen ja alas merkitsemisen väliin jää ikkuna, jonka aikana pyyntöjä ohjataan vielä kaatuneelle palvelimelle."}
{"signal": [
  {"name": "palvelin b", "wave": "1..0.......1....."},
  {"name": "tarkistus", "wave": "=.=.=.=.=.=.=.=.=", "data": ["ok", "ok", "virhe", "virhe", "virhe", "virhe", "ok", "ok", "ok"]},
  {"name": "tila tasaajassa", "wave": "=.....=.......=..", "data": ["ylhäällä", "alhaalla", "ylhäällä"]}
]}
```

Ennen kuin tarkistus huomaa kaatumisen, pyyntöjä menee vielä kaatuneelle
palvelimelle. Siihen auttavat `retries` ja `option redispatch`: kun
yhteyden avaus epäonnistuu, HAProxy yrittää uudelleen toisella
palvelimella:

```{.text tiedosto="esimerkit/luku04/haproxy.cfg" osa="yleiset"}
```

Esimerkki käynnistää kolme taustapalvelua ja HAProxyn, tappaa palvelimen
b varoittamatta (`SIGKILL`, kuin kone kaatuisi) ja lähettää pyyntöjä:

```{.python tiedosto="esimerkit/luku04/haproxy_vika.py" osa="kaatuminen"}
```

Lopuksi uusi b käynnistetään toiseen porttiin, ja sen osoite päivitetään
HAProxyn ajonaikaisella rajapinnalla. Palveluhaku (Consul, Kubernetesin
päätepisteet tai DNS) tekee saman automaattisesti:

```{.python tiedosto="esimerkit/luku04/haproxy_vika.py" osa="palautus"}
```

```{.tuloste tiedosto="esimerkit/luku04/haproxy_vika.odotettu"}
```

Kaikki yhdeksän kaatumisen jälkeistä pyyntöä onnistuivat, vaikka osa
niistä ohjattiin ensin kaatuneelle palvelimelle. Uudelleenyritys on
turvallinen tässä, koska yhteys ei edes auennut: pyyntö ei voinut
tapahtua. Jos yhteys aukeaa ja palvelin kaatuu kesken käsittelyn,
HAProxy ei oletuksena yritä uudelleen, koska pyyntö on voinut jo
tapahtua (esim. maksu). Uudelleenyritys on silloin sovelluksen päätös
ja vaatii idempotenssia (taito *Taustapalvelut*).

## Elävyys, valmius ja siisti sammutus

Terveystarkistus vastaa kysymykseen "saako tämä palvelin liikennettä
juuri nyt". Se on eri asia kuin "onko prosessi elossa": palvelin voi
olla elossa mutta käynnistymässä, ylikuormitettu tai ilman
tietokantayhteyttä. Kubernetes erottaa elävyyden (*liveness*, kaatuneen
uudelleenkäynnistys) ja valmiuden (*readiness*, liikenteen ohjaus);
tarkistusten määrittely ja päivitysten kulku siellä käsitellään
taidossa *Kontit ja pilvi-infrastruktuuri*.
Valmiustarkistus saa tarkistaa riippuvuudet, joita ilman pyyntöjä ei voi
palvella, mutta elävyystarkistus ei: muuten tietokannan katko käynnistää
kaikki sovelluspalvelimet uudelleen yhtä aikaa.

Päivitys ilman katkoa vaatii siistin sammutuksen: palvelin ilmoittaa
olevansa poistumassa (valmius pois), tasaaja lakkaa lähettämästä uusia
pyyntöjä, keskeneräiset pyynnöt valmistuvat ja vasta sitten prosessi
lopettaa. HAProxyssa saman tekee palvelimen tila `drain` ajonaikaisen
rajapinnan kautta.

## Käytännössä

- **Valitse algoritmi, joka mukautuu.** Vähiten kesken tai kahden
  satunnaisen valinta toimii myös, kun palvelimet ovat eri nopeuksisia
  tai pyynnöt eri raskaita. Pelkkä kierto olettaa, että kaikki on
  samanlaista.
- **Tasaa pyyntöjä, älä yhteyksiä, pitkäikäisillä yhteyksillä.**
  HTTP/2- ja gRPC-yhteydet tarvitsevat kerroksen 7 tasauksen tai
  asiakaspään tasauksen.
- **Yritä uudelleen vain, kun pyyntö ei voinut tapahtua.** Yhteysvirhe
  on turvallinen, aikakatkaisu kesken pyynnön ei, ellei pyyntö ole
  idempotentti.
- **Erota elävyys ja valmius.** Riippuvuuden katko ei saa käynnistää
  kaikkia palvelimia uudelleen.
- **Tasaaja on itsekin vikaantumispiste.** Käytä vähintään kahta
  tasaajaa (VRRP, anycast tai pilvipalvelun hallinnoima tasaaja) ja
  testaa, että niiden vaihto toimii.

## Itsearviointi

- Osaat verrata kerroksen 4 ja kerroksen 7 kuormantasausta ja kertoa,
  miksi pitkäikäiset yhteydet vaativat pyyntökohtaista tasausta.
- Osaat selittää, miksi kierto epäonnistuu erinopeuksisilla palvelimilla
  ja miten vähiten kesken ja kahden satunnaisen valinta mukautuvat.
- Osaat asettaa HAProxyn terveystarkistukset, uudelleenyritykset ja
  uudelleenohjauksen sekä vaihtaa palvelimen osoitteen ajonaikaisesti.
- Osaat erottaa elävyys- ja valmiustarkistuksen ja kuvata siistin
  sammutuksen vaiheet.
