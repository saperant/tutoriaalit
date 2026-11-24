# Juurisyy, arviointi ja korjaus

Löydös ei ole vielä korjaus. Kaatumiskohta on harvoin virheen syy: se
on vain paikka, jossa korruptio lopulta huomattiin. Tämä luku käy läpi
työn löydöksestä korjaukseen: raportin lukeminen, juurisyyn etsiminen,
vakavuuden arviointi, korjaus, regressiotesti ja saman virheen etsiminen
muualta.

## Raportin lukeminen

Harmaasävykuvan lukija varaa pikselipuskurin otsakkeen mittojen
mukaan ja täyttää sen rivi kerrallaan:

```{.c tiedosto="esimerkit/09-juurisyy/kuva.c" osa="tayta"}
```

Ylisuuri kuva kaataa sen ASanilla:

```{.tuloste tiedosto="esimerkit/09-juurisyy/odotettu" osa="t1"}
```

Raakaraportti siistittynä (osoitteet, prosessinumero ja polut on
korvattu):

```{.bash tiedosto="esimerkit/09-juurisyy/aja.sh" osa="raaka"}
```

```{.tuloste tiedosto="esimerkit/09-juurisyy/odotettu" osa="t2"}
```

Raportin osat ylhäältä alas:

1. **Virheen laji ja osoite**: `heap-buffer-overflow`, eli kirjoitus
   kekovarauksen ulkopuolelle.
2. **Operaatio ja pino**: 65 536 tavun kirjoitus funktiossa `tayta`
   rivillä 42, kutsujana `main`. Kehys `#0` olisi `memset`-kutsun
   sieppaaja sanitoijan sisällä; se on jätetty pois.
3. **Muistialue**: osoite on heti 65 536 tavun varauksen lopun jälkeen.
4. **Varauspino**: alue varattiin funktiossa `varaa` rivillä 32.
5. **Varjomuisti**: jokainen varjotavu kuvaa 8 tavua muistia. `00` on
   käytettävissä, `fa` on keon punaista vyöhykettä; hakasulkeet
   osoittavat virheellisen kohdan.

Raportti kertoo siis, että varaus oli 65 536 tavua ja täyttö kirjoitti
toisen 65 536 tavun rivin. Kysymys on, miksi varaus oli niin pieni.

## Juurisyy

`tayta` laskee rivien osoitteet oikein. Vika on varauksessa:

```{.c tiedosto="esimerkit/09-juurisyy/kuva.c" osa="varaa"}
```

Kuvan mitat ovat 65 536 × 65 537, ja niiden tulo on yli $2^{32}$.
`int`-kertolasku vuotaa yli, ja tulokseksi jää 65 536. UBSan näyttää
juurisyyn suoraan, koska se tarkistaa itse kertolaskun:

```{.tuloste tiedosto="esimerkit/09-juurisyy/odotettu" osa="t3"}
```

Tämä on tavallinen kuvio: kaatumiskohta (`memset`) ja juurisyy
(kertolasku) ovat eri funktioissa, ja vain toinen sanitoija näkee
juurisyyn. Juurisyyn etsinnän kysymykset:

- **Mikä arvo oli väärä kaatumishetkellä?** Tässä puskurin koko.
- **Mistä arvo tuli?** Varauksesta, jonka koko laskettiin
  otsakkeesta.
- **Mikä oletus petti?** Että mittojen tulo mahtuu `int`:iin. Oletus oli
  implisiittinen: kukaan ei päättänyt sitä.
- **Mikä syöte rikkoo oletuksen?** Mitat, joiden tulo on yli $2^{31}$.

gdb:n vahtipisteet ja ehdolliset katkaisut (*Takaisinmallinnus*, luku
8) auttavat, kun arvon alkuperä ei näy koodista suoraan. *Toistettava
ajo* (esim. `rr record`) mahdollistaa ajamisen taaksepäin kaatumisesta
arvon kirjoitushetkeen.

## Hyödynnettävyyden arviointi

Vakavuus arvioidaan sen mukaan, mitä virhe antaa syötteen antajalle.
Arviointi tehdään ilman toimivaa hyökkäystä: riittää tunnistaa
*primitiivi* eli se, mihin virhe pystyy.

| Primitiivi | Esimerkki tästä paketista | Tavallinen arvio |
|--------------------------------|-------------------------|--------------------------|
| lukee rajattoman määrän muistia | muotoilumerkkijono (luku 5) | tietovuoto, voi kumota ASLR:n |
| kirjoittaa varauksen yli | tämä kuvalukija, kekoylivuoto (luku 4) | todennäköisesti koodin suoritus |
| ylikirjoittaa paluuosoitteen | pinon ylivuoto (luku 3) | koodin suoritus ilman suojauksia |
| käyttää vapautettua muistia | istunnot (luku 4) | todennäköisesti koodin suoritus |
| kaatuu nollaosoittimeen | – | yleensä palvelunesto |

Arvion tekijät:

- **Kuka hallitsee syötettä?** Verkon yli kuka tahansa, paikallinen
  käyttäjä vai vain ylläpitäjä.
- **Kuinka paljon syötteestä hallitaan?** Koko, sisältö, kohde.
- **Mitkä suojaukset ovat käytössä?** Kanari, ASLR ja CFI nostavat
  työmäärää mutta eivät poista virhettä.
- **Millä oikeuksilla ohjelma toimii?** Juurena ajettava palvelu on eri
  asia kuin hiekkalaatikossa ajettava muunnin.

Varmuuden vuoksi muistikorruptio arvioidaan hyödynnettäväksi, ellei
toisin osoiteta. Kuvalukijan virhe on kekoylivuoto, jonka koko ja
sisältö tulevat tiedostosta: se arvioidaan vakavaksi.

## Korjaus

Korjaus kohdistuu juurisyyhyn, ei kaatumiskohtaan. `tayta` on oikein;
`varaa`-funktion korjattu haara (`KORJATTU` yllä) laskee koon
tarkistetusti ja rajaa mitat ja koon. Korjauksessa on kolme kerrosta: mitat ovat positiivisia ja kohtuullisia,
kertolasku ei vuoda yli ja kokonaiskoko on sovelluksen kannalta järkevä.
Viimeinen ei ole muistiturvallisuuden vaan palvelunestosuojan vuoksi:
kelvollinenkin otsake ei saa varata gigatavuja.

## Regressiotesti

Korjauksen mukana tulee testi, joka kattaa löydöksen ja sen lähisyötteet:

```{.bash tiedosto="esimerkit/09-juurisyy/aja.sh" osa="regressio"}
```

```{.tuloste tiedosto="esimerkit/09-juurisyy/odotettu" osa="t4"}
```

Testi ajetaan sanitoijakäännöksellä, joten se kaatuisi, jos virhe
palaisi. Jos löydös tuli fuzzerilta, sen syöte lisätään myös korpukseen
(luku 8).

## Variaatioanalyysi

Kun virhe on löytynyt yhdestä paikasta, sama kuvio on todennäköisesti
muuallakin: sama kehittäjä, sama tottumus, kopioitu koodi.
*Variaatioanalyysi* (*variant analysis*) etsii virheen sukulaiset
järjestelmällisesti. Kertolaskun leveneminen jälkikäteen on kuvio,
jonka clang-tidy tunnistaa:

```{.text tiedosto="esimerkit/09-juurisyy/koodi/.clang-tidy"}
```

```{.bash tiedosto="esimerkit/09-juurisyy/aja.sh" osa="variantit"}
```

```{.tuloste tiedosto="esimerkit/09-juurisyy/odotettu" osa="t5"}
```

```{.c tiedosto="esimerkit/09-juurisyy/koodi/pienoiskuva.c"}
```

```{.c tiedosto="esimerkit/09-juurisyy/koodi/taulukko.c"}
```

Kumpikin laskee tulon `int`- tai `unsigned`-tyypissä ja leventää sen
`size_t`:ksi vasta lopuksi, jolloin ylivuoto on jo tapahtunut.
Kolmas tiedosto, `aani.c`, käyttää `ckd_mul`-funktiota, eikä siitä tule
löydöstä. Laajempaan variaatioanalyysiin käytetään kyselykieliä, kuten
CodeQL:ää tai Semgrepiä, joilla kuvion voi kuvata tarkemmin
(esimerkiksi: syötteestä luettu arvo, joka päätyy varauksen kokoon
ilman tarkistusta).

## Käytännössä

- **Erota kaatumiskohta ja juurisyy.** Korjaus kaatumiskohtaan
  (esim. rajatarkistus `memset`-kutsuun) jättää väärän arvon muualle
  ohjelmaan.
- **Aja löydös kaikilla sanitoijilla.** Eri sanitoija voi osoittaa
  juurisyyn suoraan.
- **Arvioi primitiivi, älä rakenna hyökkäystä.** Muistikorruptio on
  vakava, ellei toisin osoiteta.
- **Lisää regressiotesti ja etsi variaatiot** ennen kuin korjaus
  sulautetaan.

## Itsearviointi

- Osaat lukea ASanin raportin osat, myös varjomuistin, ja kertoa niistä
  virheen lajin, kohdan ja muistialueen.
- Osaat jäljittää virheen kaatumiskohdasta juurisyyhyn ja nimetä
  pettäneen oletuksen.
- Osaat arvioida virheen vakavuuden primitiivin, syötteen hallinnan,
  suojausten ja oikeuksien perusteella.
- Osaat kirjoittaa korjauksen, regressiotestin ja variaatioanalyysin
  samalle virheelle.
