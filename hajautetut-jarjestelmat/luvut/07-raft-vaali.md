# Raft: johtajavaali

Konsensus tarkoittaa, että joukko solmuja sopii yhdestä arvosta niin,
että sopimus säilyy, vaikka osa solmuista kaatuu ja viestit viivästyvät.
Käytännön järjestelmät tarvitsevat konsensusta harvoin yksittäiseen
arvoon. Ne tarvitsevat sitä *replikoituun tilakoneeseen*: kaikki solmut
suorittavat samat komennot samassa järjestyksessä, joten niiden tila
pysyy samana. Komennot kirjataan lokiin, ja konsensus koskee sitä, mikä
komento on lokin kussakin kohdassa.

Raft (Ongaro ja Ousterhout 2014) suunniteltiin ymmärrettäväksi
vaihtoehdoksi Lamportin Paxokselle. Se jakaa ongelman kolmeen osaan:
johtajan valintaan, lokin replikointiin ja turvallisuuteen. Raftia
käyttävät muun muassa etcd (ja sen kautta Kubernetes), Consul,
CockroachDB, TiKV ja Kafkan KRaft-tila. Tämä luku käsittelee
vaalin, seuraava lokin.

## Termit ja roolit

Raft-solmu on aina yhdessä kolmesta roolista: *seuraaja*, *ehdokas* tai
*johtaja*. Aika on jaettu *termeihin*, jotka on numeroitu kasvavasti.
Jokainen termi alkaa vaalilla, ja termillä on enintään yksi johtaja.
Termi toimii loogisena kellona: jokainen viesti kantaa lähettäjänsä
termiä, ja jos solmu näkee suuremman termin, se siirtyy siihen ja
palaa seuraajaksi. Vanhentunut johtaja huomaa näin, että maailma on
mennyt eteenpäin, ja sen viestit hylätään vanhan termin vuoksi.

Raft tallentaa pysyvästi vain kolme asiaa: nykyisen termin, kenelle
solmu äänesti tällä termillä ja lokin. Kaikki muu (rooli, sitoutettu
kohta, seuraajien edistyminen) rakennetaan uudelleen käynnistyksessä.

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="tyypit"}
```

Simulaattorissa `RaftLevy` on solmun levy, joten kaatuminen säilyttää
termin, äänen ja lokin ja hävittää muun. Muutokset kirjoitetaan
levylle ennen vastausviestin lähettämistä, kuten Raft vaatii: jos solmu
äänestäisi ja unohtaisi äänensä kaatuessaan, se voisi äänestää samalla
termillä toista ehdokasta ja tuottaa kaksi johtajaa.

## Vaali

Seuraaja odottaa johtajalta sykettä. Jos sitä ei kuulu *vaaliaikarajan*
sisällä, seuraaja kasvattaa termiään, äänestää itseään ja pyytää ääniä
muilta. Ehdokkaasta tulee johtaja, kun se saa äänet enemmistöltä. Solmu
antaa termillä vain yhden äänen, ja vain ehdokkaalle, jonka loki on
vähintään yhtä tuore kuin oma; tämän ehdon merkitys selviää
seuraavassa luvussa.

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="vaali"}
```

Enemmistö takaa *vaaliturvallisuuden*: kahdella termin ehdokkaalla ei voi
olla kumpaakin enemmistö, koska kaksi enemmistöä leikkaavat ja
leikkauksen solmu äänesti vain toista. Viiden solmun klusteri sietää
kahden solmun kaatumisen, kolmen solmun klusteri yhden. Parillinen määrä
ei auta: neljä solmua sietää yhden kaatumisen kuten kolme, mutta vaatii
kolmen äänet.

Uusi johtaja lisää lokiin tyhjän merkinnän omalla termillään ja alkaa
lähettää sykkeitä. Tyhjän merkinnän tarkoitus selviää seuraavassa
luvussa.

## Ensimmäinen vaali

Kokoonpano rakentaa viiden solmun klusterin. Apufunktio etsii johtajan,
jonka termi on suurin, koska vanha johtaja voi verkon jakautuessa
luulla yhä olevansa johtaja:

```{.cpp tiedosto="esimerkit/07-vaali.cpp" osa="kokoonpano"}
```

Ensimmäinen koe tulostaa solmujen lokin: vaali, johtajan kaatuminen ja
uusi vaali.

```{.cpp tiedosto="esimerkit/07-vaali.cpp" osa="jalki"}
```

```{.tuloste tiedosto="esimerkit/07-vaali.odotettu"}
```

Solmun 4 aikaraja umpeutui ensin, ja se voitti vaalin 12 ms:ssa.
Johtajan kaaduttua solmut 3 ja 1 aloittivat vaalin termillä 2 lähes
samaan aikaan, ja äänet jakautuivat: kumpikaan ei saanut kolmea ääntä.
Kumpikin odotti uuden satunnaisen aikarajan, ja solmu 1 voitti termillä 3.
Termi 2 jäi ilman johtajaa, mikä on sallittua.

## Satunnaistettu aikaraja

Raftin tapa välttää jakautuneet vaalit on yksinkertainen: jokainen solmu
arpoo aikarajansa uudelleen joka kerta. Silloin yksi solmu herää yleensä
selvästi ennen muita, ehtii pyytää äänet ja voittaa. Tulosteen
taulukko on tilastokokeesta, joka ajaa sata klusteria kolmella
aikarajavälillä, kaataa johtajan sekunnin kohdalla ja mittaa uuden
vaalin. Välillä 150–300 ms ensimmäinen vaali kesti
keskimäärin 186 ms ja tarvitsi lähes aina yhden termin, ja uusi johtaja
löytyi alle 200 ms:ssa kaatumisen jälkeen. Kun väli kapenee 10 ms:iin,
termejä tarvitaan kaksi ja vaali kestää kaksinkertaisesti. Kiinteällä
aikarajalla johtajaa ei löytynyt yhdessäkään ajossa: kaikki solmut
käynnistyvät samalla hetkellä, heräävät samaan aikaan, äänestävät
itseään ja aloittavat seuraavan termin taas yhtä aikaa. Kyse on
etenemisen menetyksestä, ei turvallisuuden: tarkkailija ei löytänyt
yhtään termiä, jolla olisi ollut kaksi johtajaa.

Raft-artikkeli suosittelee, että sykeväli on selvästi lyhyempi kuin
vaaliaikaraja ja vaaliaikaraja selvästi pidempi kuin verkon tyypillinen
kiertoaika. etcd:n oletukset ovat 100 ms ja 1000 ms; konesalien välillä
arvot ovat suurempia.

## Häiritsevä solmu

Vaalisäännöissä on hienovarainen etenemisongelma. Solmu, joka on
verkosta erillään, ei kuule johtajaa ja aloittaa vaalin toisensa jälkeen
kasvattaen termiään. Kun yhteys palaa, sen suuri termi pakottaa toimivan
johtajan seuraajaksi, ja klusteri joutuu turhaan vaaliin. Luvun 11
jäljessä tämä näkyy: erillään olevat solmut ehtivät termille 4, vaikka
muulla klusterilla on koko ajan toimiva johtaja termillä 1.

Korjaus on *esiäänestys* (*Pre-Vote*, Ongaron väitöskirja): ennen termin
kasvattamista ehdokas kysyy, antaisivatko muut sille äänen. Solmut, jotka
kuulevat johtajaa, vastaavat kieltävästi, joten erillinen solmu ei kasvata
termiään. etcd ja useimmat tuotantototeutukset käyttävät esiäänestystä.
Tämän tutoriaalin toteutus jättää sen pois selkeyden vuoksi.

## Käytännössä

- **Käytä valmista toteutusta.** Raftin perusajatus mahtuu muutamaan
  sivuun, mutta tuotantokelpoinen toteutus (esiäänestys, kokoonpanon
  muutokset, tilannevedokset, johtajan siirto) on vuosien työ.
  etcd:n raft-kirjasto, hashicorp/raft ja openraft ovat hyviä
  lähtökohtia.
- **Pariton määrä solmuja.** Kolme solmua sietää yhden ja viisi kahden
  kaatumisen. Useampi solmu hidastaa jokaista kirjoitusta.
- **Kirjoita levylle ennen vastausta.** Termi ja ääni on tallennettava
  ennen ääniviestiä ja lokimerkinnät ennen kuittausta, muuten
  kaatuminen voi tuottaa kaksi johtajaa.
- **Mitoita aikarajat verkon mukaan.** Liian lyhyt vaaliaikaraja aiheuttaa
  turhia vaaleja ruuhkassa, liian pitkä pidentää katkosta johtajan
  kaatuessa.
- **Seuraa termien kasvua.** Nopeasti kasvava termi kertoo toistuvista
  vaaleista, yleensä ylikuormitetusta johtajasta tai epävakaasta verkosta.

## Itsearviointi

- Osaat selittää replikoidun tilakoneen ajatuksen ja sen, mitä
  konsensusta tarvitaan lokin rakentamiseen.
- Osaat kuvata Raftin roolit ja termit ja sen, mitä solmu tekee nähdessään
  suuremman termin.
- Osaat perustella enemmistöön perustuvan vaaliturvallisuuden ja sen,
  miksi pysyvä tila on tallennettava ennen vastausta.
- Osaat selittää jakautuneen vaalin ja satunnaistetun aikarajan
  merkityksen ja mitata sen simulaattorissa.
- Osaat kuvata häiritsevän solmun ongelman ja esiäänestyksen.
