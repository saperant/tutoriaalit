# Arkkitehtuurin ja muistikartan tunnistaminen

Raaka kuva ei kerro, mihin osoitteeseen se ladataan eikä missä
oheislaitteet ovat. Nämä on pääteltävä, ennen kuin koodia voi lukea
oikein: ilman latausosoitetta hyppyjen ja osoittimien kohteet ovat
mielivaltaisia, eikä literaalivarannon osoitinta voi erottaa luvusta.
Cortex-M tekee päättelystä poikkeuksellisen helppoa, koska se alkaa
aina kiinteästä rakenteesta, vektoritaulusta.

## Käytetyt alueet

Flash-vedos on enimmäkseen tyhjää (`0xFF`, pyyhitty flash). Käytetyt
alueet erottuvat heti, ja niiden rajat kertovat kuvan karkean
rakenteen:

```{.bash tiedosto="esimerkit/03-muistikartta/aja.sh" osa="alueet"}
```

```{.tuloste tiedosto="esimerkit/03-muistikartta/odotettu" osa="s1"}
```

Neljä aluetta: käynnistyslatain osoitteesta 0, sovelluksen otsake
osoitteesta `0x10000`, sovellus osoitteesta `0x10100` ja asetuslohko
osoitteesta `0x3f000`. Jo tämä paljastaa laitteen rakenteen: erillinen
käynnistyslatain ja sovellus, joiden välissä on otsake.

## Vektoritaulu

Cortex-M aloittaa lukemalla osoitteesta 0 kaksi sanaa: pinon
alkuarvon ja Reset-käsittelijän osoitteen. Niitä seuraa muiden
poikkeusten ja keskeytysten käsittelijät. Taulun tulkinta kertoo
pinon sijainnin (ja siten RAM-alueen), ensimmäisen suoritettavan
koodin osoitteen ja käytössä olevat keskeytykset. Käynnistyslataimen
taulu osoitteessa 0:

```{.bash tiedosto="esimerkit/03-muistikartta/aja.sh" osa="boot"}
```

```{.tuloste tiedosto="esimerkit/03-muistikartta/odotettu" osa="s2"}
```

Pino on `0x2000....`, joten RAM alkaa osoitteesta `0x20000000`.
Reset-osoite on pariton, mikä vahvistaa Thumb-tilan. Käynnistyslatain
jatkaa sovelluksen otsakkeeseen `0x10000` ja sovelluksen omaan
vektoritauluun `0x10100`:

```{.bash tiedosto="esimerkit/03-muistikartta/aja.sh" osa="sovellus"}
```

```{.tuloste tiedosto="esimerkit/03-muistikartta/odotettu" osa="s3"}
```

Sovelluksen taulussa useimmat vektorit osoittavat samaan osoitteeseen:
se on oletuskäsittelijä, jota käytetään kaikille käsittelemättömille
poikkeuksille. Taulu asettaa oman VTOR-rekisterinsä kautta voimaan;
tämän selvittää koodista (luku 4).

## Latausosoitteen päättely

Raaka kuva, joka on irrotettu säiliöstä (päivityspaketin sovellusosio),
ei kerro latausosoitettaan. Sen voi päätellä: Thumb-koodi on
paikkariippumatonta, mutta literaalivarannot sisältävät absoluuttisia
osoitteita merkkijonoihin. Oikealla latausosoitteella nämä osoittimet
osuvat merkkijonojen alkuun, väärällä eivät. Kokeillaan jokaista
tasattua ehdokasosoitetta ja lasketaan osumat:

```{.python tiedosto="esimerkit/tyokalut/kanta.py" osa="pisteet"}
```

```{.tuloste tiedosto="esimerkit/03-muistikartta/odotettu" osa="s4"}
```

Osoite `0x10100` erottuu selvästi: sillä kymmenet osoittimet osuvat
merkkijonoihin, muilla korkeintaan yksi sattumalta. Sama tekniikka
toimii isommille Linux-pohjaisille kuville, joissa latausosoitetta ei
tiedetä.

## Oheislaitteiden tunnistus

Muistiin kuvatut oheislaiterekisterit ovat kiinteissä osoitteissa,
jotka koodi lataa literaalivarannoista tai `movw`/`movt`-pareilla.
Keräämällä funktioiden lataamat vakiot ja poimimalla ne, jotka osuvat
oheislaitealueelle (`0x40000000`–`0x5FFFFFFF`) tai ytimen
järjestelmäalueelle (`0xE00.....`), saadaan lista käytetyistä
oheislaitteista. Pienen SVD-tyylisen kuvauksen avulla osoitteet
nimetään:

```{.python tiedosto="esimerkit/tyokalut/oheislaitteet.py" osa="svd"}
```

```{.bash tiedosto="esimerkit/03-muistikartta/aja.sh" osa="oheis"}
```

```{.tuloste tiedosto="esimerkit/03-muistikartta/odotettu" osa="s5"}
```

Sovellus käyttää UART0:aa (`0x40004000`) ja FPGA:n LED-rekisteriä
(`0x40028000`), viittaa RAM-alueeseen `0x20000000` alkaen ja lataa
asetuslohkon osoitteen `0x3f000`. ASCII-tavuinen vakio `ASET`
paljastuu asetuslohkon taikaluvuksi. Käynnistyslatain käyttää
lisäksi System Control Spacea (`0xE000E000`); siitä selviää koodissa,
että se asettaa VTOR:n ennen hyppyä sovellukseen.

Oheislaitekartta on nyt riittävä koodin lukemiseen: tiedetään, mihin
osoitteeseen kuva kuuluu, missä RAM ja pino ovat ja mitä rekistereitä
koodi koskettaa.

## Käytännössä

- **Cortex-M:ssä aloita aina vektoritaulusta.** Pinon alkuarvo antaa
  RAM-alueen, Reset-osoite ensimmäisen koodin ja oletuskäsittelijän
  toistuva osoite kertoo, mitkä keskeytykset ovat oikeasti käytössä.
- **Päättele latausosoite osoitinjoukosta.** Merkkijono-osoittimien
  osumamäärä on vahva signaali: oikea kanta erottuu selvästi muista.
- **Rakenna oheislaitekartta vakioista.** Kerää koodin lataamat
  vakiot ja luokittele ne osoitealueittain. Valmistajan SVD- tai
  CMSIS-otsake nimeää rekisterit; ilman niitä osoitealueet silti
  kertovat, mihin lohkoon viittaus osuu.
- **Puolustus:** muistikartta ja oheislaitteet eivät ole salaisuuksia
  — ne ovat laitteen datalehdessä. Niiden piilottaminen ei suojaa
  mitään; suojaus kuuluu pääsynvalvontaan ja salaukseen, ei
  hämäryyteen.

## Itsearviointi

- Osaat erottaa flash-vedoksen käytetyt alueet tyhjästä flashista ja
  päätellä niistä kuvan rakenteen.
- Osaat tulkita Cortex-M:n vektoritaulun: pinon, Reset-osoitteen ja
  oletuskäsittelijän.
- Osaat päätellä raa'an kuvan latausosoitteen merkkijono-osoittimien
  avulla.
- Osaat kerätä koodin lataamat vakiot ja tunnistaa niistä
  oheislaiterekisterit.
