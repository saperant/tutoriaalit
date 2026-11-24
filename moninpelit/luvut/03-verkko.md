# Verkon todellisuus

Paikallisessa testissä kaikki toimii, koska viive on alle millisekunnin
eikä mitään katoa. Pelaajan yhteydellä on neljä ominaisuutta, jotka
pelin on kestettävä:

- **Viive** (latency). Aika, jonka paketti kulkee perille. Valon nopeus
  kuidussa on noin 200 km/ms, joten 2 000 km:n matka lisää 10 ms
  suuntaansa ennen yhtään reititintä. Peleissä puhutaan yleensä
  *kiertoviiveestä* (RTT, ping): edestakaisen matkan kestosta.
- **Värinä** (jitter). Viiveen vaihtelu paketista toiseen jonojen,
  langattoman verkon uudelleenlähetysten ja reitinvaihtojen takia.
  Värinä voi vaihtaa pakettien järjestyksen.
- **Häviö** (packet loss). Ruuhkautunut reititin pudottaa paketteja, ja
  langaton yhteys hukkaa niitä häiriöissä. Yhden prosentin häviö on
  tavallista; huonolla mobiiliyhteydellä useita prosentteja.
- **Kaistanleveys.** Lähetyskaista on usein pieni (mobiili, ADSL), ja
  sen ylittäminen kasvattaa jonoja ja siten viivettä (bufferbloat).

```{.cpp tiedosto="esimerkit/03-linkki.cpp" osa="linkit"}
```

```{.tuloste tiedosto="esimerkit/03-linkki.odotettu"}
```

Mobiiliyhteydellä viive vaihtelee 45 ja 105 ms:n välillä, ja lähes
viidennes paketeista saapuu edellistä myöhemmin lähetetyn jälkeen.
Järjestys vaihtuu aina, kun värinä on suurempi kuin lähetysväli.

## UDP vai TCP

TCP takaa, että tavut saapuvat kaikki ja järjestyksessä. Peliin se
sopii huonosti juuri tämän takuun takia. Kun yksi paketti katoaa, TCP
pidättää kaikki sen jälkeen saapuneet, kunnes kadonnut on lähetetty
uudelleen ja saapunut (head-of-line blocking). Pelin tilapäivitys on
kuitenkin vanhentunut jo silloin, kun seuraava saapuu: uusinta tilaa
ei kannata odottaa vanhan takia.

```{.cpp tiedosto="esimerkit/03-jonopaa.cpp" osa="saapuminen"}
```

```{.cpp tiedosto="esimerkit/03-jonopaa.cpp" osa="ika"}
```

```{.tuloste tiedosto="esimerkit/03-jonopaa.odotettu"}
```

Samalla 2 %:n häviöllä UDP:n tila on pahimmillaan 213 ms vanha, TCP:n
607 ms. TCP:llä peli jäätyy yli 200 ms:n ajaksi seitsemisen prosenttia
ajasta, UDP:llä tuskin koskaan. Siksi reaaliaikaiset pelit käyttävät
UDP:tä ja rakentavat sen päälle oman, valikoivan luotettavuuden (luku
*Luotettavuuskerros*). TCP (tai WebSocket) sopii vuoropohjaisiin
peleihin, kirjautumiseen, kauppaan ja chattiin, joissa järjestys on
tärkeämpi kuin tuoreus.

Uudemmat protokollat lieventävät ongelmaa: QUIC kuljettaa useita
toisistaan riippumattomia virtoja UDP:n päällä, ja WebRTC:n
datakanavalle voi valita epäluotettavan ja järjestämättömän toimituksen.
Selainpeleissä nämä ovat ainoat vaihtoehdot raa'alle UDP:lle.

## Kaistan budjetti

Paketin koko on otsakkeet (IPv4 20 tavua, UDP 8 tavua) ja hyötykuorma.
Yli MTU:n (Ethernetissä 1 500 tavua, käytännössä varmuudeksi noin
1 200 tavua) menevä paketti pilkotaan, ja yhdenkin palan katoaminen
hukkaa koko paketin. Pelin paketit pidetään siksi MTU:n alla, ja
lähetystahti valitaan kaistan mukaan: tyypillisesti 20–60 tilapäivitystä
sekunnissa ja muutamia kymmeniä kilobittejä sekunnissa pelaajaa kohti.

## Käytännössä

- **Testaa huonolla verkolla.** Kehittäjän verkko on aina liian hyvä.
  Simuloi viive, värinä ja häviö (tämän tutoriaalin `Kanava`, Linuxin
  `tc netem`, Clumsy Windowsissa) ja tee siitä osa automaattisia
  testejä.
- **Näytä pelaajalle yhteyden laatu** (ping, häviö). Se ohjaa
  pelaajia korjaamaan yhteytensä ja helpottaa vianetsintää.
- **Tilan päivitykset epäluotettavasti, tärkeät tapahtumat
  luotettavasti.** Ei koko peliä TCP:llä.
- **Pidä paketit pieninä** ja tasaisessa tahdissa; purskeet täyttävät
  jonot.
- **Hinta:** UDP vaatii oman luotettavuuskerroksen, yhteyden
  tunnistuksen ja ruuhkanhallinnan. Valmiit kirjastot (ENet,
  GameNetworkingSockets, yojimbo) tekevät tämän; käytä niitä, ellei ole
  hyvää syytä tehdä itse.

## Itsearviointi

- Osaat selittää viiveen, värinän, häviön ja kaistanleveyden vaikutuksen
  peliin.
- Osaat perustella mittauksella, miksi TCP:n jonopää-ongelma sopii
  huonosti tilapäivityksille.
- Osaat valita, mitkä pelin viestit kulkevat luotettavasti ja mitkä
  epäluotettavasti.
- Osaat arvioida paketin koon ja pelin kaistantarpeen.
