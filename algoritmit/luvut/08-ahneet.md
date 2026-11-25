# Ahneet algoritmit

*Ahne algoritmi* rakentaa ratkaisun askel kerrallaan ja valitsee joka
askeleella sen vaihtoehdon, joka näyttää juuri nyt parhaalta. Valintaa
ei koskaan peruta. Ahneet algoritmit ovat yleensä yksinkertaisia ja
nopeita, mutta ne ovat oikein vain tietyissä tehtävissä, ja ero
oikean ja väärän ahneen säännön välillä voi olla hiuksenhieno. Siksi
ahne algoritmi on aina todistettava. Tavallisin todistustapa on
*vaihtoargumentti*.

## Aikataulutus

Kokoussaliin on tullut varauspyyntöjä, joista osa menee päällekkäin.
Mikä on suurin määrä varauksia, jotka voidaan hyväksyä? Kolme ahnetta
sääntöä tulee mieleen: valitaan varaus, joka alkaa aikaisimmin, joka
on lyhin tai joka loppuu aikaisimmin. Jokainen käy varaukset läpi
säännön mukaisessa järjestyksessä ja hyväksyy jokaisen, joka ei mene
päällekkäin jo hyväksyttyjen kanssa:

```{.c tiedosto="esimerkit/08-aikataulu.c" osa="ahne"}
```

Esimerkki vertaa sääntöjä kahteen vastaesimerkkiin ja raakaan hakuun,
joka kokeilee kaikki varausten osajoukot:

```{.tuloste tiedosto="esimerkit/08-aikataulu.odotettu"}
```

![Kaksi vastaesimerkkiä aikajanalla. Täytetyt palkit ovat säännön
valitsemat varaukset: ylhäällä epäonnistuva sääntö, alhaalla
aikaisimmin loppuva (esimerkin varaukset ja
tulokset).](kuvat/aikataulu.png){width=90%}

Aikaisin alkava epäonnistuu, kun yksi pitkä varaus alkaa ensimmäisenä
ja peittää kolme lyhyttä. Lyhin epäonnistuu, kun lyhyt varaus osuu
kahden pidemmän väliin ja estää molemmat. Satunnaisilla syötteillä
kumpikin sääntö löytää optimin useimmiten, mikä tekee niistä
vaarallisia: virhe ei näy pienellä testillä. Vain aikaisimmin
loppuva on oikein kaikilla 500 syötteellä, ja sen voi todistaa.

**Vaihtoargumentti.** Olkoon $g_1, g_2, \ldots, g_k$ ahneen
valitsemat varaukset loppumisajan mukaan ja $o_1, o_2, \ldots, o_m$
jokin optimaalinen ratkaisu samassa järjestyksessä. Ahne valitsee
ensin varauksen, joka loppuu aikaisimmin kaikista, joten $g_1$ loppuu
viimeistään silloin kun $o_1$. Vaihdetaan $o_1$:n tilalle $g_1$.
Ratkaisu pysyy sallittuna, koska $g_1$ loppuu aikaisemmin eikä voi
mennä päällekkäin $o_2$:n kanssa, ja sen koko on sama. Induktiolla
optimiratkaisun voi muuttaa askel kerrallaan ahneen ratkaisun
alkuosaksi. Jos optimissa olisi enemmän varauksia kuin ahneessa,
$o_{k+1}$ alkaisi $g_k$:n loputtua, ja ahne olisi valinnut sen. Siis
$k = m$.

Todistuksen kaava on yleinen: näytä, että jokaisen optimiratkaisun voi
muuttaa sisältämään ahneen ensimmäisen valinnan huonontamatta sitä, ja
että jäljelle jäävä tehtävä on samaa muotoa. Kun todistus ei onnistu,
algoritmi on yleensä väärin, ja vastaesimerkki löytyy todistuksen
kaatumiskohdasta.

Esimerkin toteutus vertaa jokaista ehdokasta kaikkiin valittuihin, koska
samaa koodia käytetään kaikille kolmelle säännölle. Aikaisimmin
loppuvan säännön kanssa riittää verrata viimeksi valitun loppuun,
ja algoritmi on lajittelun jälkeen lineaarinen: kokonaisuutena
$\Theta(n \log n)$.

## Kun ahneus ei riitä

Vaihtorahan antaminen on toinen tuttu ahne algoritmi: annetaan aina
suurin kolikko, joka mahtuu jäljellä olevaan summaan.

```{.c tiedosto="esimerkit/08-kolikot.c" osa="ahne"}
```

```{.tuloste tiedosto="esimerkit/08-kolikot.odotettu"}
```

Euron kolikoilla ahne on optimaalinen jokaisella summalla 1–1000
senttiä. Keksityllä sarjalla {1, 3, 4} se epäonnistuu jo summalla
6: ahne antaa 4 + 1 + 1, vaikka 3 + 3 riittää. Ahneus ei toimi, koska
suurimman kolikon valinta ei ole turvallinen: optimiratkaisussa ei
välttämättä ole yhtään nelosta. Optimi lasketaan dynaamisella
ohjelmoinnilla, joka on seuraavan luvun aihe: pienin kolikkomäärä
summalle $s$ on $1 + \min_c \textrm{pienin}(s - c)$.

Kolikkosarjoja, joilla ahne on aina optimaalinen, kutsutaan
*kanonisiksi*. Euro, dollari ja useimmat todelliset rahajärjestelmät
ovat kanonisia, mutta kanonisuus on tarkistettava. Esimerkin vertailu
summiin asti 1000 on sellainen tarkistus.

## Huffmanin koodaus

Tekstin merkit tallennetaan tavallisesti kiinteän mittaisina,
esimerkiksi kahdeksalla bitillä. Jos merkkien yleisyydet tunnetaan,
yleisille merkeille kannattaa antaa lyhyet koodit ja harvinaisille
pitkät. Koodien on oltava *etuliitteettömiä*: mikään koodi ei ole
toisen alkuosa, jotta bittijonon voi purkaa yksiselitteisesti ilman
erottimia. Etuliitteetön koodi on binääripuu, jonka lehdissä ovat
merkit; koodi on polku juuresta lehteen, vasen haara 0 ja oikea 1.

David Huffmanin algoritmi (1952) rakentaa optimaalisen puun ahneesti.
Aluksi jokainen merkki on oma puunsa, jonka paino on merkin
esiintymien määrä. Kaksi kevyintä puuta yhdistetään, kunnes jäljellä on
yksi puu. Kevyimmät puut löytyvät binäärikeosta (taito
*Tietorakenteet*):

```{.c tiedosto="esimerkit/08-huffman/huffman.c" osa="rakenna"}
```

Seuraavan osion pakkausesimerkin puusta näkyy periaate. Kuvassa ovat
tekstin kuusi yleisintä merkkiä; kolme pistettä merkitsee alipuuta,
jossa on harvinaisempia merkkejä. Yleisimmät merkit ovat lähellä
juurta ja saavat kolmen bitin koodin:

```{.dot tiedosto="kaaviot/huffman-puu.dot" otsikko="Huffmanin puun yläosa: koodi on polku juuresta lehteen (pakkausesimerkin tulosteesta)"}
```

Algoritmin oikeellisuus perustuu vaihtoargumenttiin. Optimaalisessa
puussa kaksi harvinaisinta merkkiä voidaan aina sijoittaa syvimmälle
sisaruksiksi: jos syvimmällä olisi yleisempi merkki, sen vaihtaminen
harvinaisemman kanssa ei pidentäisi koodia. Kun nämä kaksi yhdistetään
yhdeksi merkiksi, jonka paino on niiden summa, jäljelle jää samanlainen
mutta yhtä merkkiä pienempi tehtävä. Työ on $O(k \log k)$, kun eri
merkkejä on $k$.

Tasapeleistä on sovittava. Saman painon puista voi valita kumman
tahansa, ja kaikki valinnat antavat yhtä hyvän koodin, mutta eri koodit.
Pakkaajan ja purkajan on rakennettava täsmälleen sama puu, joten
esimerkki ratkaisee tasapelit alipuun pienimmän merkin mukaan
(`huffman.h`):

```{.c tiedosto="esimerkit/08-huffman/huffman.h"}
```

## Tiedoston pakkaus

Pakkausohjelma laskee tiedoston tavujen frekvenssit, rakentaa puun ja
kirjoittaa tiedostoon ensin otsikon ja sitten koodatut bitit.
Otsikossa on alkuperäinen pituus ja jokaisen esiintyvän tavun
frekvenssi, joista purkaja rakentaa saman puun. Bitit kerätään tavuksi
ennen kirjoittamista:

```{.c tiedosto="esimerkit/08-huffman/main.c" osa="bitit"}
```

```{.c tiedosto="esimerkit/08-huffman/main.c" osa="pakkaa"}
```

Purkaja lukee otsikon, rakentaa puun ja kulkee sitä bitti kerrallaan
juuresta lehteen. Jokainen lehti tuottaa yhden tavun. Alkuperäinen
pituus kertoo, milloin lopetetaan, koska viimeisen tavun täytebitit
näyttäisivät muuten koodeilta. Lukufunktio tarkistaa, ettei tiedosto
lopu kesken: vioittunut tai katkennut tiedosto ei saa johtaa taulukon
ohi lukemiseen.

```{.c tiedosto="esimerkit/08-huffman/main.c" osa="pura"}
```

Ohjelma pakkaa syötteenä annetun suomenkielisen tekstin tiedostoon
`pakattu.huf`, purkaa sen ja vertaa tulosta alkuperäiseen:

```{.tuloste tiedosto="esimerkit/08-huffman.odotettu"}
```

Yleisimmät merkit, a ja välilyönti, saavat kolmen bitin koodit, ja
keskipituus on 4,375 bittiä tavua kohti. Shannonin entropia
$H = -\sum p_i \log_2 p_i$ on alaraja kaikille merkki kerrallaan
toimiville koodeille, ja Huffmanin koodi on alle 0,04 bittiä sen
yläpuolella. Algoritmi käsittelee tavuja eikä merkkejä: ääkköset ovat
UTF-8:ssa kaksi tavua, ja niiden yhteinen ensimmäinen tavu saa oman
koodinsa.

Lyhyellä tekstillä otsikko vie viidesosan pakatusta tiedostosta.
Todelliset pakkaajat tallentavat otsikkoon frekvenssien sijaan vain
koodien pituudet (*kanoninen Huffman-koodi*), jolloin otsikko on
muutaman kymmenen tavun mittainen. DEFLATE (zip, gzip, PNG) yhdistää
Huffmanin koodin LZ77-menetelmään, joka korvaa toistuvat jaksot
viittauksilla aiempaan tekstiin.

## Käytännössä

- **Todista tai etsi vastaesimerkki.** Ahne sääntö, joka toimii
  useimmilla syötteillä, on vaarallisempi kuin selvästi väärä. Vertaa
  raakaan hakuun pienillä satunnaisilla syötteillä.
- **Vaihtoargumentti on tavallisin todistus.** Näytä, että optimin voi
  muuttaa sisältämään ahneen valinnan huonontamatta sitä.
- **Lajittele oikean avaimen mukaan.** Useimmat ahneet algoritmit ovat
  lajittelu ja lineaarinen läpikäynti: $\Theta(n \log n)$.
- **Ratkaise tasapelit määrätysti.** Kun kaksi ohjelmaa rakentaa saman
  rakenteen, kuten pakkaaja ja purkaja, tasapelin ratkaisun on oltava
  osa määrittelyä.
- **Tarkista syöte purettaessa.** Pakattu tiedosto on ulkoista dataa:
  jokainen luettu pituus ja indeksi tarkistetaan.

## Itsearviointi

- Osaat tunnistaa, milloin ahne sääntö on oikein, ja todistaa sen
  vaihtoargumentilla.
- Osaat antaa vastaesimerkin väärälle ahneelle säännölle, kuten
  aikaisimmin alkavalle tai lyhimmälle varaukselle.
- Osaat rakentaa Huffmanin koodin keolla ja selittää, miksi kahden
  kevyimmän yhdistäminen on optimaalista.
- Osaat suunnitella pakatun tiedoston muodon, josta purkaja rakentaa
  saman koodin, ja purkaa sen tarkistaen syötteen.
