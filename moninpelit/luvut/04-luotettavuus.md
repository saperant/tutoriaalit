# Luotettavuuskerros

UDP:n päälle rakennetaan kerros, joka tekee kolme asiaa: tunnistaa
paketit sekvenssinumerolla, kertoo vastapuolelle mitkä paketit saapuivat
ja lähettää uudelleen vain sen, mikä on menetettävä. Tilapäivityksiä ei
lähetetä uudelleen, koska seuraava päivitys korvaa ne. Tapahtumat, kuten
esineen poimiminen tai chat-viesti, on saatava perille täsmälleen kerran.

## Sekvenssinumerot

Jokainen paketti saa juoksevan numeron. 16-bittinen numero riittää, jos
vertailu sietää kierron: 60 paketin sekuntivauhdilla 65 536 kuluu
reilussa 18 minuutissa, ja sen jälkeen numerot alkavat alusta.

```{.cpp tiedosto="esimerkit/04-sekvenssit.cpp" osa="uudempi"}
```

```{.tuloste tiedosto="esimerkit/04-sekvenssit.odotettu"}
```

Etumerkillinen erotus tulkitsee luvun uudemmaksi, jos se on enintään
puoli kierrosta edellä. Naiivi `a > b` erehtyy heti kierron jälkeen, ja
virhe näkyy vasta pitkässä pelissä: vastaanottaja alkaa hylätä kaikki
uudet paketit "vanhoina". 40 000 on 100:aa yli puoli kierrosta edellä,
joten se tulkitaan vanhemmaksi; käytännössä niin vanha paketti on joka
tapauksessa hylättävä.

## Kuittauskenttä

TCP kuittaa jokaisen segmentin erikseen. Pelipaketissa kuittaukset
kulkevat vastakkaiseen suuntaan menevien pakettien mukana ilmaiseksi:
jokaisessa paketissa on uusin vastaanotettu numero ja 32 bitin kenttä,
jossa bitti *i* kertoo, saapuiko paketti *uusin − 1 − i*. Yksi paketti
kuittaa siis 33 viimeisintä, ja yksittäinen kadonnut kuittaus korvautuu
seuraavalla.

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="paketti"}
```

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="vastaanotto"}
```

Lähettäjä muistaa, mitkä tapahtumat kukin paketti kuljetti. Kun paketti
kuitataan, sen tapahtumat poistuvat jonosta. Kuittaamaton tapahtuma
lisätään uudelleen pakettiin, kun edellisestä lähetyksestä on kulunut
yli kiertoviiveen verran:

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="lahetys"}
```

```{.tuloste tiedosto="esimerkit/04-kuittaukset.odotettu"}
```

15 %:n häviöllä kaikki 50 tapahtumaa käsiteltiin, ja yhdeksän niistä
tarvitsi uudelleenlähetyksen. Uudelleenlähetys voi johtaa
kaksoiskappaleeseen, jos alkuperäinen paketti saapui mutta sen kuittaus
katosi. Vastaanottaja tunnistaa kaksoiskappaleen tapahtuman tunnisteesta
ja käsittelee sen vain kerran: lopputulos on *täsmälleen kerran*,
vaikka verkko toimittaa *vähintään kerran*.

## Järjestys ja kanavat

Kaikki luotettavat viestit eivät tarvitse järjestystä. Chat-viestien
järjestyksellä on väliä, mutta kahden pelaajan esinepoiminnat ovat
toisistaan riippumattomia. Kerroksessa on siksi usein useita
*kanavia*: epäluotettava (tila), luotettava järjestämätön (tapahtumat)
ja luotettava järjestetty (chat, kauppa). Järjestetty kanava pidättää
vain omat viestinsä, ei koko yhteyttä.

## Käytännössä

- **Kuittaukset kulkevat vastakkaisen liikenteen mukana.** Erillistä
  kuittauspakettia ei tarvita, koska peli lähettää kumpaankin suuntaan
  jatkuvasti.
- **Sekvenssinumeroiden vertailu aina kierron sietävällä funktiolla.**
  Testaa kierto erikseen: aloita testi numerosta 65 500.
- **Tunnisteet tapahtumille, ei paketeille.** Sama tapahtuma voi kulkea
  useassa paketissa; vastaanottaja tunnistaa sen tunnisteesta.
- **Kiertoviiveen arvio kuittauksista.** Lähetysajan ja kuittauksen
  välinen aika antaa RTT:n ilman erillisiä pingejä; tasoita se
  liukuvalla keskiarvolla.
- **Hinta:** luotettava viesti vie tilaa jokaisessa paketissa, kunnes se
  kuitataan. Suuret luotettavat viestit (kartan lataus) pilkotaan ja
  lähetetään omalla kanavallaan, jotta ne eivät syrjäytä tilapäivityksiä.

## Itsearviointi

- Osaat vertailla kiertäviä sekvenssinumeroita oikein ja selittää,
  miksi naiivi vertailu rikkoutuu.
- Osaat toteuttaa kuittauskentän, joka kuittaa 33 viimeisintä pakettia.
- Osaat toteuttaa valikoivan uudelleenlähetyksen ja kaksoiskappaleiden
  tunnistuksen.
- Osaat jakaa pelin viestit epäluotettaviin ja luotettaviin kanaviin.
