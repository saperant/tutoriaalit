# Synkroninen viestintä

Synkronisessa viestinnässä kutsuja lähettää pyynnön ja odottaa
vastausta ennen kuin jatkaa. Se on tuttu malli, koska se muistuttaa
metodikutsua, ja juuri siinä on sen ansa. Luku näyttää etäkutsun
pienimmillään, käy läpi historian opetukset ja vertaa nykyisiä
vaihtoehtoja: REST, gRPC ja GraphQL.

## Etäproseduurikutsu

Etäproseduurikutsun (*remote procedure call*, RPC) idea on vanha:
asiakas kutsuu tavallista rajapintaa, ja kirjasto paketoi kutsun
viestiksi, lähettää sen verkon yli ja purkaa vastauksen. Esimerkin
toteutus mahtuu yhteen luokkaan. Palvelin ottaa vastaan metodin nimen
ja argumentit JSONina ja kutsuu toteutusta reflektiolla:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/rpc/Rpc.java" osa="palvelin"}
```

Asiakas on Javan dynaaminen välittäjä (*proxy*), joka toteuttaa saman
rajapinnan ja muuttaa jokaisen kutsun HTTP-pyynnöksi:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/rpc/Rpc.java" osa="asiakas"}
```

Kutsuja ei näe eroa:

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/rpc/RpcTest.java" osa="sama"}
```

## Etäkutsu ei ole paikallinen kutsu

Ero näkyy heti, kun jokin menee pieleen. Kaatunut palvelin tuottaa
poikkeuksen, jota paikallinen kutsu ei koskaan heitä. Vielä hankalampi
on aikakatkaisu: kutsuja saa virheen, mutta ei tiedä, tehtiinkö työ.

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/rpc/RpcTest.java" osa="viat"}
```

Toinen testi on palvelujen välisen viestinnän tärkein yksittäinen
opetus. Aikakatkaisun jälkeen lopputulos on *tuntematon*. Jos kutsuja
yrittää uudelleen, tilaus voi syntyä kahdesti; jos ei yritä, tilaus voi
puuttua. Ainoa kestävä ratkaisu on tehdä toiminnosta idempotentti
(taustapalveluiden idempotenssiavain) ja yrittää uudelleen.

L. Peter Deutsch ja kollegat kokosivat Sun Microsystemsillä 1990-luvulla
*hajautetun laskennan harhaluulot* (*fallacies of distributed
computing*), joihin etäkutsun paikallinen ulkoasu houkuttelee:

1. Verkko on luotettava.
2. Viive on nolla.
3. Kaistaa on rajattomasti.
4. Verkko on turvallinen.
5. Topologia ei muutu.
6. Ylläpitäjiä on yksi.
7. Siirto ei maksa mitään.
8. Verkko on yhtenäinen.

## Historian opetukset: CORBA ja SOAP

1990-luvun **CORBA** ja Javan **RMI** veivät RPC:n pisimmälle:
etäolioilla oli tila ja elinkaari, ja niitä käytettiin kuin paikallisia
olioita. Järjestelmistä tuli puheliaita (jokainen getteri oli
verkkokutsu), etäolioiden elinkaaren hallinta oli vaikeaa, ja
rajapinnan muutos vaati kaikkien osapuolten yhtäaikaisen päivityksen.

2000-luvun **SOAP** ja WS-*-standardit siirsivät kutsut XML-viesteiksi
HTTP:n yli. Ne korjasivat alustariippuvuuden, mutta standardipino
(WS-Security, WS-ReliableMessaging, WS-AtomicTransaction) kasvoi niin
raskaaksi, että yhteentoimivuus eri toteutusten välillä jäi usein
teoriaksi. Samaan aikaan *palvelukeskeinen arkkitehtuuri* (SOA)
keskitti integraatiot raskaaseen *palveluväylään* (ESB), johon kertyi
liiketoimintalogiikkaa, ja siitä tuli koko organisaation pullonkaula.

Mikropalvelujen periaatteet ovat osin vastareaktio näihin: karkeat
rajapinnat hienojakoisten sijaan, tilattomat pyynnöt etäolioiden
sijaan, älykkäät päätepisteet ja "tyhmät putket" älykkään väylän
sijaan sekä rajapintojen yhteensopiva kehitys yhtäaikaisten päivitysten
sijaan.

## Nykyiset vaihtoehdot

| Ominaisuus | REST (HTTP + JSON) | gRPC | GraphQL |
|---|---|---|---|
| Malli | resurssit ja HTTP-metodit | proseduurit (`.proto`) | kysely skeemaa vastaan |
| Muoto | JSON, tekstiä | Protocol Buffers, binääriä | JSON |
| Kuljetus | HTTP/1.1 tai 2 | HTTP/2 | HTTP |
| Skeema | OpenAPI (valinnainen) | pakollinen, koodigenerointi | pakollinen |
| Suoratoisto | rajallinen | kaksisuuntainen | tilaukset (*subscriptions*) |
| Välimuistit | HTTP:n omat | ei | vaikea |
| Selain | suoraan | vaatii välityksen | suoraan |
| Vahvuus | julkiset rajapinnat, työkalut | sisäinen liikenne, tehokkuus | monta näkymää samasta datasta |

gRPC:ssä rajapinta kirjoitetaan `.proto`-tiedostoon, josta generoidaan
asiakas ja palvelin kymmenelle kielelle. Binäärimuoto on JSONia
pienempi ja nopeampi jäsentää, ja kenttien numerointi tekee
yhteensopivista muutoksista mekaanisia: uusi kenttä saa uuden numeron,
eikä vanhan numeroa käytetä uudelleen. GraphQL sopii erityisesti
taustapalveluksi monelle käyttöliittymälle (*backend for frontend*,
luku 11), koska asiakas valitsee kentät, eikä palvelimen tarvitse
arvata jokaisen näkymän tarpeita.

Kaikki kolme ovat synkronisia, ja kaikki kolme perivät tämän luvun
viat: viive, osittaiset viat ja tuntematon lopputulos. Valinta niiden
välillä vaikuttaa tehokkuuteen ja työkaluihin, ei arkkitehtuurin
perusongelmiin.

## Rajapinnan yhteensopiva kehitys

Palvelujen itsenäisyys edellyttää, että rajapintaa voi muuttaa
julkaisematta kaikkia asiakkaita samalla kertaa. Säännöt ovat samat
kaikille muodoille:

- **Lisää, älä muuta.** Uusi valinnainen kenttä on yhteensopiva;
  kentän uudelleennimeäminen tai tyypin muutos ei ole.
- **Ole suvaitsevainen lukija** (*tolerant reader*). Asiakas ohittaa
  tuntemattomat kentät eikä riipu kenttien järjestyksestä.
- **Laajenna ja supista** (*expand and contract*). Uusi kenttä lisätään
  vanhan rinnalle, asiakkaat siirretään, ja vanha poistetaan vasta, kun
  sitä ei enää käytetä.
- **Versio vain rikkovalle muutokselle**, ja silloin molemmat
  versiot rinnakkain siirtymäajan.

Luvun 11 sopimustestit tarkistavat nämä säännöt automaattisesti.

## Käytännössä

- **Karkeat rajapinnat.** Yksi kutsu hakee näkymän tarvitseman
  kokonaisuuden; hienojakoinen rajapinta tekee jokaisesta näkymästä
  kutsusarjan.
- **Jokaisella etäkutsulla on aikaraja**, ja jokainen muuttava kutsu
  on idempotentti tai varustettu idempotenssiavaimella, koska
  aikakatkaisun jälkeen lopputulos on tuntematon.
- **Älä piilota verkkoa.** Asiakaskirjaston rajapinta saa näyttää
  paikalliselta, mutta sen dokumentaation ja poikkeusten on kerrottava,
  että kutsu voi viipyä ja epäonnistua.
- **REST ulos, gRPC sisään** on yleinen ja perusteltu jako: julkiset
  rajapinnat HTTP:n ja JSONin työkaluilla, sisäinen raskas liikenne
  tehokkaasti binäärinä.
- **Hinnat:** jokainen synkroninen riippuvuus lisää viiveen ja
  pienentää saatavuutta (luku 7).

## Itsearviointi

- Osaat selittää, miten RPC-kirjasto muuttaa metodikutsun
  verkkoviestiksi, ja nimetä, mikä paikallisesta kutsusta muuttuu.
- Osaat selittää, miksi aikakatkaisun jälkeen lopputulos on tuntematon
  ja miten idempotenssi ratkaisee sen.
- Osaat luetella hajautetun laskennan harhaluuloja ja CORBA:n ja SOAPin
  opetuksia.
- Osaat verrata RESTiä, gRPC:tä ja GraphQL:ää ja valita niistä
  tilanteeseen sopivan.
- Osaat kehittää rajapintaa yhteensopivasti (lisää, älä muuta;
  suvaitsevainen lukija; laajenna ja supista).
