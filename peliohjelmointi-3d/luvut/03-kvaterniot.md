# Kvaterniot

Edellinen luku näytti, mitä kolmella kulmalla ei voi tehdä. Pelit
tallentavat asennon *kvaterniona*: neljänä lukuna, joilla kiertoja voi
yhdistää, kääntää ja interpoloida ilman lukkiutumista. Kvaternioiden
algebran voi johtaa monella tavalla, mutta peliohjelmoijalle riittää
ymmärtää, mitä luvut tarkoittavat ja mitkä viisi operaatiota niille on.

## Akseli ja kulma

Mikä tahansa asento saadaan yhdellä kierrolla jonkin akselin ympäri.
Yksikkökvaternio tallentaa tämän akselin $\mathbf{u}$ ja kulman
$\theta$ muodossa

$$q = \bigl(\cos\tfrac{\theta}{2},\; \sin\tfrac{\theta}{2}\,\mathbf{u}\bigr)
    = (w, x, y, z).$$

Lukuja on neljä, mutta vapausasteita kolme, koska pituus on aina yksi:
$w^2 + x^2 + y^2 + z^2 = 1$.

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="kvaternio"}
```

Puolikas kulma on esityksen ainoa yllätys. Sen seurauksena $q$ ja $-q$
ovat sama kierto: kulma $\theta + 360°$ vaihtaa kaikkien neljän luvun
merkin, mutta kiertää kappaleen samaan asentoon.

```{.cpp tiedosto="esimerkit/03-kvaternio.cpp" osa="perus"}
```

```{.tuloste tiedosto="esimerkit/03-kvaternio.odotettu" rivit="1-4"}
```

Neljänneskierros y-akselin ympäri vie x-akselin suuntaan −z, ja
liittoluku tuo sen takaisin. Vektori kierretään suoraan kvaterniolla
ilman välimatriisia; matriisiksi kvaternio muutetaan vasta, kun asento
annetaan renderöijälle:

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="kierra"}
```

## Kiertojen yhdistäminen

Kahden kvaternion tulo on kierto, joka tekee ensin oikeanpuoleisen ja
sitten vasemmanpuoleisen kierron. Järjestys on sama kuin matriiseilla,
ja tulo on yhtä vähän vaihdannainen:

```{.cpp tiedosto="esimerkit/03-kvaternio.cpp" osa="yhdistaminen"}
```

```{.tuloste tiedosto="esimerkit/03-kvaternio.odotettu" rivit="6-7"}
```

Tulossa on 16 kertolaskua, kun 3 × 3 -matriisien tulossa on 27, ja
kvaternio vie neljä lukua yhdeksän sijaan. Tärkeämpi etu on kuitenkin
se, mitä pyöristysvirheelle tapahtuu.

## Normalisointi

Kun kappale pyörii, sen asentoa päivitetään joka askeleella pienellä
kierrolla. Pyöristysvirheet ja integroinnin likiarvot kertyvät.
Matriisissa ne näkyvät akseleina, jotka eivät ole enää kohtisuorassa
eivätkä yksikön pituisia, ja korjaus vaatii ortogonalisoinnin (taito
*Lineaarialgebra*). Kvaterniossa ainoa asia, joka voi mennä vikaan, on
pituus, ja korjaus on jako pituudella.

```{.cpp tiedosto="esimerkit/03-kvaternio.cpp" osa="integrointi"}
```

```{.tuloste tiedosto="esimerkit/03-kvaternio.odotettu" rivit="9-10"}
```

Kymmenessä sekunnissa normalisoimaton kvaternio on kasvanut lähes
yhdeksän prosenttia, ja sillä kierretty kappale venyy. Normalisoituna
pituus pysyy ykkösenä. Kulmanopeuden ja voimien käsittely kuuluu
taitoon *Pelifysiikka*; tässä riittää sääntö, että jokaisen kertyvän
päivityksen jälkeen kvaternio normalisoidaan.

## Interpolointi

Kahden asennon välillä lyhin reitti on kierto yhden kiinteän akselin
ympäri tasaisella kulmanopeudella. *Slerp* (*spherical linear
interpolation*) kulkee täsmälleen tämän reitin. *Nlerp* interpoloi
neljää lukua suoraan ja normalisoi tuloksen: reitti on sama, mutta
nopeus ei ole aivan tasainen.

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="slerp"}
```

Molemmat funktiot kääntävät ensin toisen kvaternion merkin, jos
pistetulo on negatiivinen. Ilman sitä interpolointi kiertäisi pitkää
reittiä, koska $q$ ja $-q$ ovat sama asento mutta eri pisteitä.

Esimerkki vertaa kolmea tapaa. Kahden asennon välinen kulma mitataan
kvaternioiden pistetulosta:

```{.cpp tiedosto="esimerkit/03-slerp.cpp" osa="kulma"}
```

```{.cpp tiedosto="esimerkit/03-slerp.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-slerp.odotettu"}
```

Slerp etenee tasaisesti: neljännes matkasta on neljännes kulmasta.
Nlerp kulkee samaa reittiä mutta on alussa hieman jäljessä ja lopussa
edellä, enimmillään muutaman asteen. Eulerin kulmien interpolointi
poikkeaa reitiltä: sarake *kierros* kertoo, että puolivälissä reitti on
18 astetta suoraa pidempi, ja nopeus vaihtelee selvästi.

![Sama interpolointi viidessä vaiheessa. Ylärivillä slerp kääntää
konetta tasaisesti yhden akselin ympäri. Alarivillä Eulerin kulmien
interpolointi vie samasta alusta samaan loppuun, mutta välivaiheissa
kone käy asennoissa, jotka eivät ole reitin
varrella.](kuvat/slerp.png){width=100%}

Nlerp on useimmiten oikea valinta, kun asennot ovat lähellä toisiaan,
kuten animaation peräkkäisissä avainkehyksissä: se on halvempi, ja ero
slerpiin on mitätön. Slerp kannattaa, kun kulma on suuri ja tasainen
nopeus näkyy, esimerkiksi kameran käännöksessä.

## Muunnos osina

Solmun muunnos tallennetaan osina: sijainti, kierto ja skaala
(*TRS*, *translation, rotation, scale*). Osat voi interpoloida
erikseen, ja matriisi lasketaan niistä vasta, kun sitä tarvitaan.

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="muunnos"}
```

Kahden kokonaisen matriisin interpolointi alkio kerrallaan ei tuota
kiertoa: välivaiheissa kappale kutistuu ja vääristyy. Siksi kaikki,
mitä interpoloidaan, pidetään TRS-muodossa: animaation avainkehykset,
verkosta saapuvat tilat ja piirron interpolointi kiinteiden askelten
välillä.

Usein tarvitaan myös kierto, joka kääntää yhden suunnan toiseksi,
esimerkiksi aseen piipun kohti maalia:

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="suuntaan"}
```

## Käytännössä

- **Asento kvaterniona, kulmat rajalla.** Tila, animaatio ja verkko
  käyttävät kvaternioita. Eulerin kulmat kuuluvat editoriin ja
  kameraan, matriisit renderöijälle.
- **Normalisoi kertyvän päivityksen jälkeen.** Yksi neliöjuuri askelta
  kohden on halpa vakuutus venymistä vastaan.
- **Tarkista pistetulon merkki ennen interpolointia.** Unohtunut
  merkin kääntö näkyy satunnaisena pitkänä kiepsahduksena, jota on
  vaikea toistaa.
- **Tulon järjestys on sama kuin matriiseilla.** `a * b` tekee ensin
  b:n. Kappaleen omien akselien ympäri kierretään kertomalla oikealta,
  maailman akselien ympäri vasemmalta.
- **Tiedostoissa järjestys vaihtelee.** glTF tallentaa kvaternion
  järjestyksessä (x, y, z, w), moni kirjasto järjestyksessä
  (w, x, y, z). Tarkista aina.

## Itsearviointi

- Osaat kertoa, mitä yksikkökvaternion neljä lukua tarkoittavat ja
  miksi $q$ ja $-q$ ovat sama kierto.
- Osaat yhdistää kaksi kiertoa oikeassa järjestyksessä, kääntää kierron
  ja kiertää vektorin kvaterniolla.
- Osaat selittää, miksi kertyvä kierto normalisoidaan ja miksi se on
  kvaterniolle helpompaa kuin matriisille.
- Osaat valita slerpin ja nlerpin välillä ja perustella, miksi
  muunnokset interpoloidaan TRS-muodossa eikä matriiseina.
