# Luurankoanimaatio

Kaksiulotteisen pelin hahmo vaihtaa kuvaa. Kolmiulotteisen hahmon
verkkoa ei voi tallentaa uudelleen jokaista asentoa varten: kävely,
juoksu, hyppy ja niiden välimuodot veisivät liikaa muistia, eikä
asentoja voisi yhdistellä. Sen sijaan hahmolla on *luuranko*, muutaman
kymmenen nivelen hierarkia. Animaatio liikuttaa niveliä, ja verkon
jokainen kärki seuraa niitä niveliä, joihin se on sidottu. Tässä
luvussa tehdään koko ketju: luuranko, sidonta, skinnaus, animaatioleike
ja kahden animaation sekoitus.

## Luuranko on muunnoshierarkia

Nivel on solmu näkymäpuussa: sillä on vanhempi ja paikallinen muunnos.
*Poosi* on yksi paikallinen muunnos jokaiselle nivelelle. Nivelten
matriisit mallin koordinaatistossa lasketaan samalla läpikäynnillä kuin
luvussa *Muunnoshierarkia*.

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="luuranko"}
```

Esimerkin luuranko on käsivarsi: olkapää, kyynärpää ja ranne metrin
välein.

```{.cpp tiedosto="esimerkit/11-luuranko.cpp" osa="kasivarsi"}
```

```{.cpp tiedosto="esimerkit/11-luuranko.cpp" osa="taivutus"}
```

```{.tuloste tiedosto="esimerkit/11-luuranko.odotettu" rivit="1-4"}
```

Kyynärpään kierto ei muuta kyynärpään omaa paikkaa vaan kaiken, mikä on
sen alla: ranne nousee suoraan kyynärpään yläpuolelle.

## Sidontapoosi

Verkko mallinnetaan yhdessä asennossa, *sidontapoosissa* (*bind pose*),
ja sen kärjet tallennetaan mallin koordinaatistossa. Jotta kärki
voisi seurata niveltä, se on ensin siirrettävä nivelen omaan
koordinaatistoon sellaisena kuin nivel sidontahetkellä oli. Tämän tekee
*käänteinen sidontamatriisi*, joka lasketaan kerran.

*Skinnausmatriisi* on kahden muunnoksen tulo: kärki viedään
sidontapoosista nivelen koordinaatistoon ja sieltä nivelen nykyisen
asennon mukana takaisin malliin.

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="sidonta"}
```

Sidontapoosissa skinnausmatriisi on yksikkömatriisi: nivelen matriisi
ja sen käänteismatriisi kumoavat toisensa, ja verkko pysyy paikallaan.

## Skinnaus

Jos jokainen kärki seuraisi täsmälleen yhtä niveltä, verkko taittuisi
nivelen kohdalta kuin pahvi. Siksi kärjellä on *painot*: se seuraa
enintään neljää niveltä, ja lopullinen paikka on niiden antamien
paikkojen painotettu keskiarvo. Menetelmän nimi on *lineaarinen
sekoitusskinnaus* (*linear blend skinning*).

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="skinnaus"}
```

Käsivarren ympärille tehdään putki, jonka kärkien painot määräytyvät
niiden paikasta. Kyynärpään kohdalla paino liukuu olkavarrelta
kyynärvarrelle:

```{.cpp tiedosto="esimerkit/11-luuranko.cpp" osa="painot"}
```

```{.cpp tiedosto="esimerkit/11-luuranko.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/11-luuranko.odotettu" rivit="6-8"}
```

![Käsivarsi sidontapoosissa, taivutettuna jäykällä sidonnalla ja
taivutettuna sekoitetuilla painoilla. Luut on piirretty mustalla ja
nivelet punaisella. Jäykässä sidonnassa verkko leikkaa itsensä
kyynärpäässä; sekoitettuna taive on pyöreä mutta
kapeampi.](kuvat/skinnaus.png){width=100%}

Sekoitus tekee taipeesta pehmeän, mutta sillä on hintansa: kyynärpään
kohdalla käsivarren paksuus putoaa 30 sentistä 21 senttiin. Kahden
kierretyn paikan keskiarvo on lähempänä niveltä kuin kumpikaan niistä.
Ilmiö on lineaarisen sekoituksen tunnettu heikkous, ja se on pahin
kiertyvissä nivelissä, joissa verkko kuristuu kuin karkkipaperi.
Pelit elävät sen kanssa lisäämällä apuniveliä tai käyttämällä
kaksoiskvaternioihin perustuvaa sekoitusta.

Näytönohjaimella skinnaus tehdään verteksivarjostimessa (taito
*GPU-ohjelmointi: OpenGL ja Vulkan*): peli laskee joka ruudulla
skinnausmatriisit, muutaman kymmenen matriisia hahmoa kohden, ja
näytönohjain soveltaa ne kärkiin.

## Animaatioleike

*Leike* (*clip*) on tallennettu liike. Se koostuu *kanavista*, joista
jokainen animoi yhden nivelen yhtä ominaisuutta *avainkehyksillä*:
ajanhetkillä ja niiden arvoilla.

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="leike"}
```

Leikkeen poosi tietyllä hetkellä saadaan etsimällä kustakin kanavasta
kaksi avainkehystä hetken ympäriltä ja interpoloimalla niiden välillä:
sijainti ja skaala lineaarisesti, kierto slerpillä.

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="nayte"}
```

Nivelet, joilla ei ole kanavaa, pysyvät sidontapoosissa. Esimerkissä on
kaksi leikettä samalle käsivarrelle:

```{.cpp tiedosto="esimerkit/11-animaatio.cpp" osa="leikkeet"}
```

```{.cpp tiedosto="esimerkit/11-animaatio.cpp" osa="naytteet"}
```

```{.tuloste tiedosto="esimerkit/11-animaatio.odotettu" rivit="1-7"}
```

Leike toistuu: hetki 1,25 antaa saman poosin kuin hetki 0,25.

## Sekoitus ja ristihäivytys

Poosit ovat dataa, joten niitä voi yhdistellä. Kahden poosin *sekoitus*
interpoloi jokaisen nivelen muunnoksen erikseen:

```{.cpp tiedosto="esimerkit/yhteinen/luuranko.hpp" osa="sekoitus"}
```

```{.cpp tiedosto="esimerkit/11-animaatio.cpp" osa="sekoitus"}
```

```{.tuloste tiedosto="esimerkit/11-animaatio.odotettu" rivit="9-12"}
```

Painolla 0,5 käsi sekä vilkuttaa että on puoliksi nostettuna.
Sekoituksella tehdään kaksi asiaa. Kun paino seuraa pelin tilaa, kuten
hahmon nopeutta, kahdesta leikkeestä saadaan portaaton siirtymä
kävelystä juoksuun. Kun paino liukuu lyhyessä ajassa nollasta yhteen,
tuloksena on *ristihäivytys* (*crossfade*), jolla vaihdetaan leikkeestä
toiseen ilman nykäystä:

```{.cpp tiedosto="esimerkit/11-animaatio.cpp" osa="haivytys"}
```

```{.tuloste tiedosto="esimerkit/11-animaatio.odotettu" rivit="14-21"}
```

Molemmat leikkeet etenevät häivytyksen ajan. Jos lähtevä leike
pysäytettäisiin, liike hidastuisi näkyvästi juuri vaihdon kohdalla.

```{.dot otsikko="Hahmon animaatio ruudun aikana. Pelin tila valitsee leikkeet ja painot; loppu on laskentaa."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.25;
  node [width=0, height=0, margin="0.1,0.06"];
  tila [label="pelin tila\n(nopeus,\nmaassa?)"];
  a [label="leike A\nhetkellä t"];
  b [label="leike B\nhetkellä t"];
  sek [label="sekoitus\npainolla w"];
  hier [label="nivelmatriisit\n(hierarkia)"];
  skin [label="skinnaus-\nmatriisit"];
  verkko [label="verkon\nkärjet"];
  tila -> a; tila -> b; tila -> sek [label="w"];
  a -> sek; b -> sek; sek -> hier -> skin -> verkko;
}
```

Pelimoottoreissa leikkeiden valinta ja painot kuvataan tilakoneena tai
sekoituspuuna. Liikkeiden tekeminen, käänteinen kinematiikka ja
animaation pakkaus ovat omia aiheitaan; pelin rakenteen kannalta
animaatiojärjestelmä on funktio pelin tilasta poosiksi.

## Käytännössä

- **Animaatio tuottaa poosin, ei matriiseja.** Sekoitus tehdään
  paikallisille muunnoksille TRS-muodossa. Matriiseja sekoittamalla
  hahmo kutistuu.
- **Skinnausmatriisi = nivelen matriisi × käänteinen sidontamatriisi.**
  Jos sidontapoosissa hahmo ei näytä mallinnetulta, toinen niistä on
  väärin tai kerrottu väärin päin.
- **Painojen summa on yksi.** Muuten kärki siirtyy kohti origoa tai
  siitä poispäin. Painot normalisoidaan tuonnissa.
- **Animaation aika on pelin aikaa.** Leikettä kuljetetaan kiinteän
  askeleen ajalla, jotta toisto on deterministinen.
- **Juuriliike päätetään erikseen.** Joko animaatio liikuttaa hahmoa
  (liike poimitaan juurinivelestä ja annetaan hahmo-ohjaimelle) tai
  ohjain liikuttaa ja animaatio kävelee paikallaan. Jos molemmat
  liikuttavat, jalat liukuvat.

## Itsearviointi

- Osaat kuvata ketjun leikkeestä verkon kärkiin: näyte, poosi,
  nivelmatriisit, skinnausmatriisit ja painotettu summa.
- Osaat selittää, mitä käänteinen sidontamatriisi tekee ja miksi
  skinnausmatriisi on sidontapoosissa yksikkömatriisi.
- Osaat kertoa, miksi lineaarinen sekoitusskinnaus kaventaa taivetta.
- Osaat näytteistää leikkeen, sekoittaa kaksi poosia ja toteuttaa
  ristihäivytyksen.
