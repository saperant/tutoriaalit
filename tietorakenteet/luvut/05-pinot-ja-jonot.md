# Pinot, jonot ja rengaspuskurit

Pino ja jono ovat abstrakteja tietotyyppejä, joissa alkioita lisätään
ja poistetaan vain päistä. *Pino* (engl. stack) palauttaa viimeksi
lisätyn alkion ensin (LIFO, last in, first out); *jono* (engl. queue)
palauttaa ensimmäisenä lisätyn ensin (FIFO, first in, first out).
Kummankin operaatiot ovat vakioaikaisia, ja kumpikin toteutetaan
yleensä taulukolla eikä listalla.

## Pino taulukossa

Pino on taulukko ja koko. Lisäys kirjoittaa paikkaan `koko` ja
kasvattaa kokoa; poisto pienentää kokoa. Päällimmäinen alkio on
`taulukko[koko - 1]`. Jos pinon suurin syvyys tiedetään, taulukko voi
olla kiinteän kokoinen ja pino kokonaan automaattisessa muistissa.
Muuten se on luvun 3 vektori.

Pino sopii kaikkeen, missä viimeksi aloitettu asia on lopetettava
ensin: funktiokutsut, sisäkkäiset lohkot, peruutus (undo) ja syvyyshaku.
Esimerkki tarkistaa, ovatko sulkeet tasapainossa. Pinoon tallennetaan
avaava sulje ja sen sarake, jotta virheilmoitus osaa kertoa paikan:

```{.c tiedosto="esimerkit/05-sulut.c" osa="pino"}
```

Sulkeva sulje täsmää vain pinon päällimmäiseen avaavaan:

```{.c tiedosto="esimerkit/05-sulut.c" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/05-sulut.odotettu"}
```

Rivillä 2 hakasulje sulkeutuu ennen kaarisuljetta, rivillä 3 aaltosulje
jää auki (virhe raportoidaan avaavan sulkeen kohdalle), ja rivillä 4
sulkevalle sulkeelle ei ole paria. Kiinteä syvyys tekee pinosta myös
puolustuksen: syöte, jossa on tuhat sisäkkäistä suljetta, saa
virheilmoituksen eikä kasvata muistinkäyttöä rajatta. Rekursiivinen
jäsennin olisi samassa tilanteessa vaarassa ylittää kutsupinon.

## Jono ja rengaspuskuri

Jono tarvitsee kaksi päätä: lisäys tapahtuu loppuun ja poisto alusta.
Jos taulukon alusta poistettaisiin siirtämällä loput alkiot, poisto
olisi $O(n)$. Ratkaisu on antaa molempien päiden liikkua ja kiertää
taulukon loppu takaisin alkuun. Tällainen *rengaspuskuri* (engl. ring
buffer, circular buffer) on kiinteän kokoisen jonon tavallisin
toteutus: ajurien vastaanottopuskurit, äänipuskurit ja säikeiden
väliset viestijonot ovat rengaspuskureita.

### Indeksointi

Kun puskurin koko on $K$, looginen paikka $i$ vastaa taulukon
indeksiä $i \bmod K$. Jos $K$ on kahden potenssi, jakojäännös on
bittimaski `i & (K - 1)`, joka on nopeampi kuin jakolasku ja toimii
oikein myös silloin, kun `i` kiertää etumerkittömän tyypin ympäri.

### Täysi vai tyhjä?

Rengaspuskurin klassinen sudenkuoppa on, että täysi ja tyhjä puskuri
näyttävät samalta: kummassakin luku- ja kirjoitusindeksi osoittavat
samaan paikkaan. Ratkaisuja on kolme:

| Tapa | Täysi | Tyhjä | Haitta |
|------|-------|-------|--------|
| Yksi paikka tyhjänä | `(k + 1) % K == l` | `k == l` | yksi paikka hukkaan |
| Erillinen laskuri | `maara == K` | `maara == 0` | molemmat osapuolet kirjoittavat laskuria |
| Kaksi juoksevaa indeksiä | `k - l == K` | `k - l == 0` | $K$:n oltava kahden potenssi |

Kolmannessa mallissa indeksejä ei pienennetä modulo $K$, vaan ne
kasvavat vapaasti, ja taulukon paikka lasketaan vasta käytettäessä.
Täyttöaste on indeksien erotus. Etumerkittömässä aritmetiikassa erotus
on oikein silloinkin, kun kirjoitusindeksi on jo kiertänyt nollaan ja
lukuindeksi ei, koska laskutoimitukset tehdään modulo $2^{32}$ ja
$2^{32}$ on jaollinen $K$:lla.

```{.c tiedosto="esimerkit/05-rengas.c" osa="rengas"}
```

Testi aloittaa indeksit neljän askeleen päästä ympärikierrosta, jotta
reunatapaus tulee testatuksi heti eikä vasta tuntien käytön jälkeen.
Kirjoittaja tuottaa neljä tavua kierroksessa, lukija ehtii käsitellä
kaksi, joten puskuri täyttyy ja kirjoittaja joutuu odottamaan:

```{.tuloste tiedosto="esimerkit/05-rengas.odotettu"}
```

Mallin suurin etu näkyy rinnakkaisuudessa. Kirjoittaja muuttaa vain
indeksiä `kirjoitettu` ja lukija vain indeksiä `luettu`; kumpikin vain
lukee toisen indeksin. Siksi yksi kirjoittaja ja yksi lukija voivat
käyttää puskuria ilman lukkoa, kunhan indeksit ovat atomisia ja
kirjoitus näkyy oikeassa järjestyksessä (vapautus–hankinta-semantiikka).
Erillinen laskuri tekisi tämän mahdottomaksi, koska molemmat
muuttaisivat samaa muuttujaa. Muistijärjestys käsitellään taidossa
*Rinnakkaisohjelmointi*.

## Kasvava jono ja pakka

Jos jonon kokoa ei tiedetä etukäteen, rengaspuskurin voi kasvattaa
kuten vektorin: varataan kaksinkertainen taulukko ja kopioidaan
alkiot loogisessa järjestyksessä uuden taulukon alkuun. Silloin lisäys
on tasoitetusti $O(1)$. Kasvava rengaspuskuri on samalla *pakka*
(engl. deque): lisäys ja poisto onnistuvat vakioajassa kummastakin
päästä, ja $i$:nnen alkion saa laskemalla `data[(alku + i) & (K - 1)]`.

Jonon voi toteuttaa myös yksöislinkitetyllä listalla, jolla on
häntäosoitin: lisäys loppuun, poisto alusta. Se kannattaa vain, kun
alkioita ei voi siirtää muistissa tai kun tarvitaan tunkeileva jono
(luku 4), joka ei varaa muistia.

## Käytännössä

- **Pino on taulukko ja koko.** Kiinteä syvyysraja on hyvä
  puolustus vihamielistä syötettä vastaan.
- **Rengaspuskurin koko kahden potenssina.** Indeksi on bittimaski, ja
  vapaasti juoksevat etumerkittömät indeksit kiertävät ympäri oikein.
- **Testaa ympärikierto heti.** Aloita indeksit lähellä tyypin
  maksimia, ettei virhe paljastu vasta pitkän ajon jälkeen.
- **Yksi kirjoittaja, yksi lukija, ei yhteistä muuttujaa.** Kahden
  indeksin malli on lukottoman jonon perusta.
- **Päätä täyden puskurin käytös.** Odottaako kirjoittaja, hylätäänkö
  uusin vai ylikirjoitetaanko vanhin? Valinta kuuluu rajapintaan.

## Itsearviointi

- Osaat toteuttaa pinon taulukolla ja käyttää sitä sisäkkäisten
  rakenteiden tarkistamiseen.
- Osaat selittää, miksi täysi ja tyhjä rengaspuskuri sekoittuvat, ja
  nimetä kolme tapaa erottaa ne.
- Osaat toteuttaa rengaspuskurin kahdella vapaasti juoksevalla
  indeksillä ja perustella, miksi erotus on oikein ympärikierrossakin.
- Osaat kertoa, miksi kahden indeksin malli sopii yhden kirjoittajan ja
  yhden lukijan jonoon ilman lukkoa.
