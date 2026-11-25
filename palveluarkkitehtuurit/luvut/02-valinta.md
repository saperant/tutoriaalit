# Monoliitti vai mikropalvelut

*Monoliitti* on yksi julkaistava kokonaisuus: yksi prosessi, yksi
tietokanta ja yksi julkaisu. *Mikropalvelut* ovat joukko pieniä,
erikseen julkaistavia palveluja, joilla kullakin on oma tietonsa ja
jotka keskustelevat verkon yli. Niiden välissä on *modulaarinen
monoliitti*: yksi julkaisu, mutta sisällä tiukat rajat. Nimet eivät
kerro laadusta. Huonosti jäsennelty monoliitti on "mutapallo", ja
huonosti jaetut mikropalvelut ovat "hajautettu monoliitti", jossa on
molempien haitat (luku 7).

```{.dot otsikko="Kolme tapaa jakaa sama kauppa. Monoliitissa ja modulaarisessa monoliitissa on yksi prosessi ja yksi julkaisu; modulaarisessa moduulien rajat ja taulut on erotettu. Mikropalveluissa jokainen palvelu on oma prosessinsa omine tietokantoineen, ja kutsut kulkevat verkon yli (katkoviivat)."}
digraph {
  rankdir=TB; nodesep=0.25; ranksep=0.4;
  node [height=0.3];
  subgraph cluster_m {
    label="monoliitti:\nyksi prosessi"; style="rounded"; margin=10;
    m1 [label="myynti, varasto ja\nlaskutus sekaisin"];
    mdb [label="yhteiset\ntaulut", shape=cylinder, height=0.5];
    m1 -> mdb;
  }
  subgraph cluster_mm {
    label="modulaarinen monoliitti:\nyksi prosessi, rajat testeinä"; style="rounded"; margin=10;
    a3 [label="laskutus"]; a2 [label="varasto"]; a1 [label="myynti"];
    adb [label="taulut\nmoduuleittain", shape=cylinder, height=0.5];
    a1 -> adb; a2 -> adb; a3 -> adb;
  }
  subgraph cluster_ms {
    label="mikropalvelut:\nkolme prosessia, kutsut verkon yli"; style="rounded,dashed"; margin=10;
    subgraph cluster_p3 { label=""; style="rounded"; margin=6;
      p3 [label="laskutus"]; d3 [label="", shape=cylinder, width=0.45, height=0.35]; p3 -> d3; }
    subgraph cluster_p2 { label=""; style="rounded"; margin=6;
      p2 [label="varasto"]; d2 [label="", shape=cylinder, width=0.45, height=0.35]; p2 -> d2; }
    subgraph cluster_p1 { label=""; style="rounded"; margin=6;
      p1 [label="myynti"]; d1 [label="", shape=cylinder, width=0.45, height=0.35]; p1 -> d1; }
    p2 -> p1 [constraint=false, style=dashed, dir=both];
    p3 -> p2 [constraint=false, style=dashed, dir=both];
  }
}
```

## Mitä jako maksaa

Kun moduuli muuttuu palveluksi, metodikutsusta tulee verkkokutsu.
Esimerkin RPC-kirjasto (luku 5) tekee etäkutsusta paikallisen
näköisen, ja testi mittaa eron samalla koneella:

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/rpc/RpcTest.java" osa="hinta"}
```

Paikallinen kutsu kestää nanosekunteja, saman koneen HTTP-kutsu
kymmeniä tai satoja mikrosekunteja ja konesalien välinen kutsu
millisekunteja. Ero on vähintään tuhatkertainen, eikä se ole ainoa
hinta. Verkkokutsu voi myös epäonnistua tavoilla, joita metodikutsu ei
voi: vastaus katoaa, palvelu on hidas tai kaatunut, tai pyyntö meni
perille mutta vastaus ei tullut takaisin. Tietoa ei voi enää muuttaa
yhdessä transaktiossa, joten järjestelmä on hetkittäin epäjohdonmukainen
(*eventual consistency*). Lisäksi jokainen palvelu tarvitsee oman
julkaisuputkensa, valvontansa, lokinsa ja päivystyksensä
(*operatiivinen kuorma*).

## Mitä jako tuottaa

Hinnalla saadaan neljä asiaa, joita monoliitti ei anna:

- **Itsenäinen julkaisu.** Tiimi julkaisee palvelunsa koordinoimatta
  muita. Tämä on mikropalvelujen tärkein peruste.
- **Vikojen eristäminen.** Raportoinnin muistivuoto ei kaada
  maksuja.
- **Erillinen skaalaus.** Hakupalvelusta voi ajaa kymmenen kopiota ja
  laskutuksesta yhden.
- **Teknologinen vapaus.** Koneoppimispalvelu voi olla Pythonia ja
  maksut Javaa.

Jos mikään näistä ei ole todellinen tarve, jako on pelkkää hintaa.
Moni organisaatio on palannut mikropalveluista modulaariseen
monoliittiin, kun ne huomasivat maksavansa hajautuksesta saamatta
itsenäisiä julkaisuja.

## Conwayn laki

Melvin Conway havaitsi 1968, että järjestelmän rakenne jäljittelee sen
tekijäorganisaation viestintärakennetta. Kolme tiimiä tuottaa kolmeen
osaan jakautuvan järjestelmän, ja osien rajapinnat ovat siellä, missä
tiimit keskustelevat. Laki toimii myös toisin päin (*käänteinen
Conwayn manööveri*): jos halutaan kolme itsenäistä palvelua, tarvitaan
kolme tiimiä, joista kukin omistaa yhden palvelun kokonaan. Palvelu,
jota viisi tiimiä muokkaa, ei ole itsenäinen, vaikka se olisi oma
prosessinsa.

Kirja *Team Topologies* (Skelton ja Pais) neuvoo mitoittamaan palvelut
niin, että yksi tiimi pystyy omistamaan ne kognitiivisesti. Tiimityypit,
kognitiivinen kuorma ja Conwayn lain mittaaminen ovat taidossa *Tiimit
ja organisaatiomallit*; tässä riittää sääntö, että palvelun raja ja
tiimin raja vedetään samaan kohtaan.

## Päätöksen tueksi

| Kysymys | Monoliitti | Modulaarinen monoliitti | Mikropalvelut |
|---------|------------|-------------------------|---------------|
| Tiimejä | 1–2 | 2–8 | monta, itsenäisiä |
| Julkaisu | yksi | yksi | palvelukohtainen |
| Transaktiot | tavalliset | tavalliset | saga, eventual consistency |
| Kutsun hinta | nanosekunteja | nanosekunteja | millisekunteja, voi epäonnistua |
| Rajojen valvonta | ei mitään | testit | prosessiraja |
| Operatiivinen kuorma | pieni | pieni | suuri (alusta, valvonta, päivystys) |
| Rajojen siirto | helppo | helppo | kallis (data ja sopimukset) |

Hyvä oletus on aloittaa modulaarisena monoliittina ja erottaa moduuli
palveluksi, kun sille on konkreettinen syy: tiimi tarvitsee oman
julkaisutahdin, osa skaalautuu muista poikkeavasti tai vika halutaan
eristää. Moduulin rajat on silloin jo testattu, ja sen tieto on jo
omissa tauluissaan, joten erottaminen on lähinnä siirtotyötä (luku 3).

## Käytännössä

- **Aloita yhdestä julkaistavasta**, jaa sisältä. Rajat on halpa
  siirtää prosessin sisällä ja kallis siirtää verkon yli.
- **Perustele jako hyödyllä, ei muodilla.** Kirjaa ADR:ään, mikä
  neljästä hyödystä (julkaisu, vikojen eristys, skaalaus, teknologia)
  palvelun erottamisella saavutetaan.
- **Laske palvelu–tiimi-suhde.** Jos palveluja on enemmän kuin
  ihmisiä, jokainen julkaisu on koordinointia ja jokainen päivystys
  raskas.
- **Hinnat:** verkkokutsu on vähintään tuhatkertainen metodikutsuun
  nähden ja voi epäonnistua; jaettu transaktio korvautuu sagalla;
  jokainen palvelu tarvitsee putken, valvonnan ja päivystyksen.

## Itsearviointi

- Osaat selittää monoliitin, modulaarisen monoliitin ja
  mikropalvelujen erot ja nimetä kunkin hinnat.
- Osaat perustella palvelun erottamisen konkreettisella hyödyllä ja
  kirjata päätöksen arkkitehtuuripäätöstietueeksi.
- Osaat selittää Conwayn lain ja sen, miksi palvelun omistaa yksi
  tiimi.
- Osaat arvioida, mitä metodikutsun muuttaminen verkkokutsuksi
  maksaa viiveenä, vikoina ja johdonmukaisuutena.
