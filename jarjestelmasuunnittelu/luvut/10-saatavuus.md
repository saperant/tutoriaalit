# Saatavuus ja luotettavuus

Saatavuus (*availability*) on osuus ajasta tai pyynnöistä, jolloin
palvelu toimii. Se ilmoitetaan "ysiluokkina": 99,9 % on kolme ysiä ja
sallii noin 43 minuuttia katkoa kuukaudessa, 99,99 % neljä minuuttia.
Jokainen lisäysi maksaa moninkertaisesti, koska se vaatii kahdennuksen
jokaiseen kerrokseen, automaattisen vaihdon ja käyttöönotot ilman
katkoa. Siksi tavoite valitaan sen mukaan, mitä katko maksaa, eikä
mahdollisimman suureksi. SLI-, SLO- ja SLA-käsitteet ja
virhebudjettihälytysten perusteet ovat taidossa *Palvelinympäristöt*.
Tässä lasketaan, miten osien saatavuus muodostaa kokonaisuuden.

## Sarjaan ja rinnan

Kun pyyntö tarvitsee kaikki osat (tasaaja, sovelluspalvelin, välimuisti,
tietokanta), saatavuudet kerrotaan: kokonaisuus on huonompi kuin heikoin
osa. Kun riittää, että yksi kopioista toimii, kerrotaan
epäsaatavuudet:

```{.dot otsikko="Esimerkin neljäs kokoonpano. Sarjassa pyyntö tarvitsee jokaisen osan, rinnan riittää yksi kopioista. Välimuisti on ketjun ainoa yhden kappaleen osa tasaajan lisäksi."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.45;
  pyynto [label="pyyntö", shape=plaintext];
  tasaaja; muisti [label="välimuisti"];
  subgraph cluster_api {
    label="rinnan"; fontsize=9; color="#B8C4C8";
    api1 [label="api"]; api2 [label="api"]; api3 [label="api"];
  }
  subgraph cluster_kanta {
    label="rinnan"; fontsize=9; color="#B8C4C8";
    kanta; replika;
  }
  pyynto -> tasaaja;
  tasaaja -> api1; tasaaja -> api2; tasaaja -> api3;
  api1 -> muisti; api2 -> muisti; api3 -> muisti;
  muisti -> kanta; muisti -> replika;
}
```

```{.python tiedosto="esimerkit/luku10/saatavuus.py" osa="kaavat"}
```

```{.python tiedosto="esimerkit/luku10/saatavuus.py" osa="kokoonpanot"}
```

```{.tuloste tiedosto="esimerkit/luku10/saatavuus.odotettu" asti="2 vyöhykettä"}
```

Neljä osaa sarjassa, joista mikään ei ole alle 99,9 %, tuottaa 99,7 %:n
palvelun, eli yli kaksi tuntia katkoa kuukaudessa. Kolme sovelluspalvelinta
rinnan poistaa sovelluskerroksen lähes kokonaan laskusta, ja kannan
replika parantaa lisää. Silti tulos on vain 99,85 %, koska välimuisti on
yhä sarjassa yhtenä kappaleena. Kun välimuisti tehdään
ohitettavaksi (palvelu toimii ilman sitä, luku 9), se poistuu ketjusta,
ja saatavuus nousee 99,95 %:iin.

Laskun tärkein opetus on kaksi viimeistä riviä. Kolmen kopion kaava
olettaa, että kopiot vikaantuvat toisistaan riippumatta. Kun ne ovat
samassa saatavuusvyöhykkeessä, vyöhykkeen katko kaataa ne kaikki, ja
saatavuus on vyöhykkeen saatavuus. Todelliset viat ovat usein
yhteisiä: konesalin sähkö tai verkko, sama virheellinen asetus kaikilla
palvelimilla, sama ohjelmistoversio, joka kaatuu samaan syötteeseen,
tai yhteinen riippuvuus kuten DNS tai todennuspalvelu. Kahdennus
auttaa vain siltä osin kuin viat ovat riippumattomia.

## Vikaantumisalueet

Hajautus vikaantumisalueittain on vastaus yhteisiin vikoihin:

- **Palvelin ja teline.** Kopiot eri koneissa ja eri telineissä.
- **Saatavuusvyöhyke.** Erillinen konesali samalla alueella, viive
  1–2 ms. Synkroninen replikointi vyöhykkeiden välillä on mahdollinen.
- **Alue.** Eri kaupunki tai maa, viive kymmeniä millisekunteja.
  Replikointi on yleensä asynkronista (luku 7), joten alueen
  menetyksessä voi kadota viimeisimmät kirjoitukset.

Monialueinen arkkitehtuuri on joko *aktiivinen–passiivinen* (yksi alue
palvelee, toinen on valmiina ja saa replikoidun datan) tai
*aktiivinen–aktiivinen* (molemmat palvelevat, ja kirjoitukset on
ratkaistava: kotialue käyttäjää kohden, konfliktien ratkaisu tai
maailmanlaajuinen konsensus). Aktiivinen–aktiivinen on moninkertaisesti
monimutkaisempi, ja se kannattaa vain, kun alueen katko on
liiketoiminnalle kestämätön tai käyttäjät ovat ympäri maailmaa.

## RTO ja RPO

Katastrofista palautuminen mitoitetaan kahdella luvulla:

- **RTO** (*recovery time objective*): kuinka kauan palautuminen saa
  kestää. Määrää, tarvitaanko valmiina odottava ympäristö vai riittääkö
  rakentaminen varmuuskopiosta.
- **RPO** (*recovery point objective*): kuinka paljon dataa saa kadota.
  Asynkroninen replika antaa RPO:n sekunneissa, öinen varmuuskopio
  vuorokauden.

Molemmat ovat lupauksia vain, jos palautuminen on harjoiteltu.
Varmuuskopio, jota ei ole koskaan palautettu, on toive
(taito *Palvelinympäristöt*).

## Virhebudjetti

SLO määrittää virhebudjetin: 99,9 %:n tavoite sallii 0,1 % epäonnistumisia
jaksossa. Budjetti on työkalu päätöksiin: kun sitä on jäljellä,
julkaistaan rohkeasti; kun se on lopussa, keskitytään luotettavuuteen.
Hälytykset perustuvat budjetin *kulumisnopeuteen* (*burn rate*):
nopeus 1 kuluttaa budjetin tasan jakson lopussa, nopeus 14,4 kahdessa
vuorokaudessa.

```{.python tiedosto="esimerkit/luku10/saatavuus.py" osa="budjetti"}
```

```{.tuloste tiedosto="esimerkit/luku10/saatavuus.odotettu" alkaen="virhebudjetti 30"}
```

Taulukko kertoo, mikä virhesuhde laukaisee nopean hälytyksen kullakin
tavoitteella. Neljän ysin tavoitteella 0,14 % virheitä tunnin ajan on
jo hälytyksen arvoinen; kahden ysin tavoitteella vasta 14 %. Luvussa 11
sama sääntö kirjoitetaan Prometheuksen hälytykseksi.

## Käyttöönotot

Suurin osa katkoista johtuu muutoksista: uusi versio, asetus tai
infrastruktuurin muutos. Saatavuus siis riippuu siitä, miten muutokset
otetaan käyttöön:

- **Vähittäinen käyttöönotto**: uusi versio ensin pienelle osalle
  palvelimista tai liikenteestä (*canary*), sitten laajemmin, jos
  virhesuhde ja latenssi pysyvät tavoitteessa.
- **Nopea paluu**: edellinen versio on valmiina, ja paluu on yksi
  komento tai automaattinen.
- **Yhteensopivat muutokset**: tietokannan skeemamuutos tehdään
  vaiheittain (lisää sarake, kirjoita molempiin, siirrä lukijat, poista
  vanha), jotta vanha ja uusi versio toimivat yhtä aikaa.
- **Ominaisuusliput** erottavat käyttöönoton julkaisusta: koodi on
  tuotannossa, mutta toiminto kytketään päälle erikseen.

Julkaisustrategiat, toimitusputki ja tietokantamuutokset ilman katkoa
käsitellään kokonaisuutena taidossa *Jatkuva integraatio ja toimitus*.

## Käytännössä

- **Laske saatavuus ketjusta.** Jokainen sarjassa oleva osa heikentää
  kokonaisuutta. Etsi yhden kappaleen osat ja tee niistä kahdennettuja
  tai ohitettavia.
- **Hajauta vikaantumisalueittain.** Kopiot samassa paikassa eivät suojaa
  paikan violta.
- **Varo yhteisiä vikoja.** Sama asetus, versio ja riippuvuus kaikilla
  kopioilla kumoaa kahdennuksen. Ota muutokset käyttöön vähitellen.
- **Valitse SLO katkon hinnan mukaan.** Jokainen ysi maksaa enemmän kuin
  edellinen.
- **Harjoittele palautuminen.** RTO ja RPO ovat totta vasta, kun
  palautus on tehty.

## Itsearviointi

- Osaat laskea sarjaan ja rinnan kytkettyjen osien saatavuuden ja
  muuntaa sen katkoaikaan.
- Osaat selittää, miksi yhteiset viat kumoavat kahdennuksen, ja hajauttaa
  järjestelmän vikaantumisalueittain.
- Osaat määritellä RTO:n ja RPO:n ja kertoa, mitä ne vaativat
  arkkitehtuurilta.
- Osaat laskea virhebudjetin ja kulumisnopeuden hälytysrajat.
