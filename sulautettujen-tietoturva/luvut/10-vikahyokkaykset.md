# Vikahyökkäykset

Sivukanava kuuntelee laitetta, vikahyökkäys (*fault injection*)
häiritsee sitä. Kun suorittimen käyttöjännite notkahtaa nanosekuntien
ajaksi, kellopulssi lyhenee tai piiriin osuu sähkömagneettinen pulssi
tai laservalo, yksittäinen käsky voi jäädä suorittamatta tai rekisterin
bitti kääntyä. Jos vika osuu oikeaan kohtaan, allekirjoituksen
tarkistus "onnistuu" tai debug-lukitus jää lukematta.

## Vikamallit

Hyökkäyksen suunnittelussa ja torjunnassa käytetään yksinkertaisia
malleja siitä, mitä vika tekee:

- **käskyn ohitus**: yksi käsky (esim. ehdollinen hyppy) jää
  suorittamatta
- **bittivirhe**: rekisterin tai muistin bitti kääntyy
- **arvon pakotus**: arvo muuttuu nollaksi tai pelkiksi ykkösiksi

Esimerkki mallintaa käynnistimen päätöksen pienenä käskyohjelmana ja
kokeilee kaikki yksittäiset viat tilanteessa, jossa allekirjoitus EI
kelpaa. Tavallinen koodi on suora käännös lauseesta
`if (!tarkista()) pysähdy(); käynnistä();`, kovennettu koodi käyttää
neljää vastatoimea:

```{.c tiedosto="esimerkit/10-hairio.c" osa="ohjelmat"}
```

```{.c tiedosto="esimerkit/10-hairio.c" osa="kokeile"}
```

```{.tuloste tiedosto="esimerkit/10-hairio.odotettu"}
```

Tavallisessa koodissa riittää yksi ohitettu hyppy, ja jokainen
tulosrekisterin bittivirhe muuttaa hylkäyksen (0) hyväksynnäksi
(nollasta eroava). Kovennettu koodi kestää kaikki yksittäiset viat. Kaksi
täsmällistä vikaa samassa suorituksessa murtaa senkin yhdessä
tapauksessa: vastatoimet nostavat hyökkäyksen hintaa, eivät tee
siitä mahdotonta.

## Vastatoimet

**Vaikeasti käännettävät vakiot.** Hyväksyntä ja hylkäys ovat
32-bittisiä arvoja, joiden Hammingin etäisyys on suuri (tässä toistensa
komplementit), eikä kumpikaan ole 0 tai 1. Yksittäinen bittivirhe ei
muuta toista toiseksi.

**Turvallinen oletusarvo.** Tulosmuuttuja alustetaan hylkäykseksi, joten
ohitettu tarkistus jättää sen hylkääväksi.

**Tuplatarkistus.** Ehto tarkistetaan kahdesti, mieluiten eri tavoilla
ja satunnaisen viiveen jälkeen, jotta sama vika ei osu molempiin.
Esimerkin käynnistin tarkistaa valinnan vielä ennen hyppyä:

```{.c tiedosto="esimerkit/laite/lahde/kaynnistin.c" osa="paa"}
```

**Kulun eheys.** Laskuri kasvaa jokaisessa tarkistuksessa ja
tarkistetaan ennen kriittistä toimintoa; ohitettu tarkistus jättää
laskurin väärään arvoon.

**Satunnaiset viiveet** tekevät vian ajoittamisesta vaikeampaa:
hyökkääjä ei tiedä, milloin tarkistus tapahtuu.

**Laitteiston tunnistimet.** Monissa piireissä on jännitteen ja kellon
valvonta (*brown-out detector*, kellohäiriön tunnistin), joka
nollaa piirin poikkeavissa olosuhteissa. Ne torjuvat suurimman osan
yksinkertaisista häiriöistä.

Kääntäjä voi poistaa tuplatarkistuksen, koska se on sen mielestä
turha. Siksi kriittiset muuttujat merkitään `volatile`-määreellä tai
tarkistus tehdään apufunktiolla, jota kääntäjä ei voi päätellä, ja
lopputulos tarkistetaan konekielestä.

## Mihin hyökätään

Vikahyökkäyksen kohteet ovat harvoja ja tunnettuja:

- allekirjoituksen tai tiivisteen tarkistuksen tulos käynnistimessä
- debug-lukituksen luku käynnistyksessä
- salasanan tai PIN:n tarkistus
- kryptografinen laskenta: virheellinen RSA-CRT-allekirjoitus voi
  paljastaa yksityisavaimen (Bellcoren hyökkäys), joten allekirjoitus
  tarkistetaan ennen kuin se annetaan ulos

## Käytännössä

- **Koveta vain kriittiset kohdat.** Vastatoimet maksavat koodikokoa
  ja aikaa; kohdista ne tarkistuksiin, joiden ohitus antaa hallinnan.
- **Ei boolean-arvoja turvapäätöksissä.** Käytä vakioita, turvallisia
  oletusarvoja ja tuplatarkistuksia.
- **Tarkista konekieli.** Optimoiva kääntäjä voi yhdistää tai poistaa
  tarkistuksia.
- **Ota laitteiston tunnistimet käyttöön** ja valitse piiri, jonka
  valmistaja kertoo vikahyökkäysten vastatoimista.
- **Testaa.** Vikahyökkäyksiä voi simuloida emulaattorissa (kuten
  tässä) tai kokeilla edullisilla häiriölaitteilla.

## Itsearviointi

- Osaat kuvata käskyn ohituksen ja bittivirheen vikamallina ja
  tunnistaa koodista kohdat, joihin ne osuvat.
- Osaat koventaa turvapäätöksen vakioilla, oletusarvolla,
  tuplatarkistuksella ja kulun eheydellä.
- Osaat selittää, miksi vastatoimet nostavat hyökkäyksen hintaa mutta
  eivät tee siitä mahdotonta.
