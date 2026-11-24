# CRDT:t

Edellisissä luvuissa samanaikaiset kirjoitukset olivat ongelma:
LWW hukkasi toisen, ja vektorikellojen sisarukset jättivät yhdistämisen
sovellukselle. *Ristiriidattomat replikoidut tietotyypit* (*conflict-free
replicated data types*, CRDT; Shapiro ym. 2011) kääntävät asetelman.
Tietotyyppi suunnitellaan niin, että samanaikaiset muutokset voi aina
yhdistää yksiselitteisesti, jolloin replikat voivat ottaa muutoksia
vastaan toisistaan tietämättä ja silti päätyä samaan tilaan.

## Yhdistämisen lait

Tilapohjaisessa CRDT:ssä (*state-based*, CvRDT) replikat lähettävät
toisilleen koko tilansa, ja vastaanottaja yhdistää sen omaansa
funktiolla `yhdista`. Jos yhdistäminen on

- **vaihdannainen**: yhdista(a, b) = yhdista(b, a),
- **liitännäinen**: yhdista(yhdista(a, b), c) = yhdista(a, yhdista(b, c)) ja
- **idempotentti**: yhdista(a, a) = a,

ja jokainen paikallinen muutos kasvattaa tilaa tämän järjestyksen
suhteen, replikat lähentyvät samaan tilaan, kunhan jokainen tila
päätyy ennen pitkää jokaiselle replikalle. Viestien järjestyksellä ei ole
väliä (vaihdannaisuus ja liitännäisyys), eikä sillä, montako kertaa
sama tila tulee perille (idempotenssi). Matemaattisesti tilat
muodostavat puolihilan (*join-semilattice*), ja yhdistäminen on sen
pienin yläraja.

Operaatiopohjainen CRDT (*operation-based*, CmRDT) lähettää tilan sijaan
operaatiot. Viestit ovat pieniä, mutta jakelun on taattava, että jokainen
operaatio toimitetaan täsmälleen kerran ja syy-seuraussuhteen
mukaisessa järjestyksessä. Delta-CRDT:t ovat välimuoto: ne lähettävät
tilan muuttuneen osan, ja yhdistäminen on edelleen idempotentti.

## Laskurit

Kasvava laskuri (*G-Counter*) pitää jokaiselle replikalle oman
osuutensa. Replika kasvattaa vain omaansa, yhdistäminen ottaa
alkioittain maksimin, ja arvo on osuuksien summa:

```{.cpp tiedosto="esimerkit/yhteinen/crdt.hpp" osa="glaskuri"}
```

Maksimi toimii, koska kunkin replikan oma osuus vain kasvaa: suurempi
luku sisältää aina pienemmän tiedon. Yksi yhteinen luku ei toimisi:
jos kaksi replikaa kasvattaa arvoa 5 samanaikaisesti, kumpikin saa 6,
ja maksimi on 6 eikä 7.

Kaksisuuntainen laskuri (*PN-Counter*) on kaksi kasvavaa laskuria,
toinen lisäyksille ja toinen vähennyksille:

```{.cpp tiedosto="esimerkit/yhteinen/crdt.hpp" osa="pnlaskuri"}
```

## Havainnoiva poistojoukko

Kasvava joukko (*G-Set*), johon voi vain lisätä, yhdistetään unionilla.
Poisto on vaikeampi: jos replika A poistaa alkion ja replika B lisää sen
samanaikaisesti, kumpi voittaa? Kaksivaiheinen joukko (*2P-Set*) pitää
poistetut erillisessä joukossa, mutta poistettua alkiota ei voi enää
lisätä. *Havainnoiva poistojoukko* (*observed-remove set*, OR-Set) antaa
jokaiselle lisäykselle yksilöllisen tunnisteen. Poisto poistaa ne
tunnisteet, jotka poistaja on nähnyt, ja samanaikainen lisäys toisessa
replikassa saa uuden tunnisteen, jota poisto ei koske:

```{.cpp tiedosto="esimerkit/yhteinen/crdt.hpp" osa="orjoukko"}
```

Semantiikka on "lisäys voittaa": samanaikaisen lisäyksen ja poiston
jälkeen alkio on joukossa. Hinta on hautakivet: poistetut tunnisteet
on säilytettävä, jotta myöhään saapuva vanha tila ei palauttaisi
poistettua alkiota. Käytännön toteutukset karsivat hautakivet, kun
kaikki replikat ovat varmasti nähneet poiston, mikä vaatii taas
tietoa kaikista replikoista.

## Juoruava verkko

Kokeessa kolme replikaa tekee 10 ms välein satunnaisen paikallisen
muutoksen ja lähettää 20 ms välein koko tilansa satunnaiselle
naapurille (*gossip*). Verkko kadottaa ja monistaa viidesosan viesteistä,
ja viiveet vaihtelevat 1–40 ms, joten tilat saapuvat sekaisin.
Vertailukohtana on laskuri, jonka arvo ratkaistaan LWW-säännöllä:

```{.cpp tiedosto="esimerkit/05-crdt.cpp" osa="tila"}
```

```{.cpp tiedosto="esimerkit/05-crdt.cpp" osa="replika"}
```

Muutokset loppuvat hetkellä 1000, ja juoru jatkuu toisen sekunnin:

```{.cpp tiedosto="esimerkit/05-crdt.cpp" osa="koe"}
```

```{.cpp tiedosto="esimerkit/05-crdt.cpp" osa="lisays-voittaa"}
```

```{.tuloste tiedosto="esimerkit/05-crdt.odotettu"}
```

Jokaisella siemenellä PN-laskuri on kaikissa replikoissa sama ja
täsmälleen kaikkien muutosten summa, ja joukot ovat samat. LWW-laskuri
on jokaisella siemenellä väärin, koska samanaikaiset kasvatukset
korvasivat toisensa. Viimeinen rivi näyttää lisäys voittaa
-semantiikan: B poisti maidon, jonka se oli nähnyt, mutta A:n
samanaikainen uusi lisäys säilyi.

Testi on luonteeltaan juuri sellainen, jonka simulaattori tekee
helpoksi: invariantti ("kaikki replikat lähentyvät samaan tilaan, ja
laskurin arvo on muutosten summa") tarkistetaan jokaisella siemenellä
viestien katoamisen, monistumisen ja uudelleenjärjestyksen alla.
Yhdistämisen lait voi lisäksi testata suoraan satunnaisilla tiloilla,
mikä löytää rikkeen nopeammin kuin koko järjestelmän ajo.

## Missä CRDT:itä käytetään

Riak tarjoaa laskurit, joukot ja kartat CRDT:inä, Redis Enterprise
käyttää niitä konesalien väliseen replikointiin, ja yhteismuokkaimet
(Automerge, Yjs) mallintavat tekstin ja JSON-dokumentit CRDT:inä, jotta
käyttäjät voivat muokata ilman verkkoa ja yhdistää myöhemmin.
*Paikallinen ensin* (*local-first*) -sovellukset rakentuvat samalle
ajatukselle.

CRDT:t eivät ratkaise kaikkea. Ne takaavat lähentymisen, eivät
sovelluksen invariantteja: kaksi replikaa voi kumpikin myydä viimeisen
tuotteen, ja yhdistetty varastosaldo on −1. Ehto "saldo ei mene
negatiiviseksi" vaatii koordinointia, eli sopimista ennen muutosta.
CALM-teoreema (*consistency as logical monotonicity*, Hellerstein ja
Alvaro 2020) muotoilee rajan: koordinointia ei tarvita täsmälleen
niille ongelmille, jotka voi ilmaista monotonisesti, eli joissa uusi
tieto ei koskaan kumoa aiempaa päätelmää.

## Käytännössä

- **Valitse semantiikka tietoisesti.** Lisäys voittaa, poisto voittaa ja
  LWW ovat kaikki "oikeita" CRDT:itä, mutta ne antavat eri tuloksen.
  Ostoskorissa lisäys voittaa, käyttöoikeuksissa poiston on syytä
  voittaa.
- **Laske metatiedon hinta.** Laskurin koko kasvaa replikoiden määrän
  mukaan ja joukon hautakivet poistojen mukaan. Rajaa replikat ja
  suunnittele karsinta.
- **Testaa lait erikseen.** Satunnaisilla tiloilla tehty testi
  vaihdannaisuudelle, liitännäisyydelle ja idempotenssille on halpa ja
  löytää useimmat virheet.
- **Koordinoi vain siellä, missä on pakko.** Rakenna monotoniset osat
  CRDT:illä ja käytä konsensusta (luvut 7–8) vain ehtoihin, jotka sitä
  vaativat.

## Itsearviointi

- Osaat luetella yhdistämisen kolme lakia ja selittää, miksi ne takaavat
  lähentymisen ilman järjestystä ja kertalähetystä.
- Osaat toteuttaa kasvavan ja kaksisuuntaisen laskurin ja selittää,
  miksi yksi yhteinen luku ei toimi.
- Osaat toteuttaa havainnoivan poistojoukon ja kuvata sen lisäys
  voittaa -semantiikan ja hautakivien hinnan.
- Osaat testata CRDT:n lähentymisen juoruavassa, häviävässä verkossa.
- Osaat kertoa, mitä CRDT:t eivät takaa ja milloin koordinointi on
  välttämätöntä.
