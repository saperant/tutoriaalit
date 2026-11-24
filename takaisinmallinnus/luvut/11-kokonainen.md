# Kokonainen analyysi

Edellisten lukujen tekniikat yhdistyvät tässä yhdeksi työksi.
Tavoitteena on *yhteentoimivuus*: mittalaitteen vientityökalu kirjoittaa
jokaisen rivin eteen 16-bittisen tarkisteen dokumentoimattomalla
algoritmilla, ja haluamme toteuttaa saman algoritmin itse, jotta muut
ohjelmat voivat lukea ja tuottaa yhteensopivia tiedostoja. Ohjelma on
riisuttu. Tämä on direktiivin tarkoittama laillinen käyttökohde: tieto
hankitaan yhteentoimivuutta varten, eikä sitä saa muuten.

Työ etenee viidessä vaiheessa, jotka ovat kaikki yhdessä
analyysiskriptissä, jotta tulos on toistettava.

## 1. Käyttäytyminen ja 2. tuonnit

Ensin katsotaan, mitä ohjelma tekee ja mitä se tuo:

```{.tuloste tiedosto="esimerkit/14-yhteentoimivuus/odotettu" osa="t1"}
```

```{.tuloste tiedosto="esimerkit/14-yhteentoimivuus/odotettu" osa="t2"}
```

Tuonnit kertovat, että ohjelma lukee rivejä (`fgets`), mittaa niiden
pituuden (`strcspn`) ja tulostaa muotoillen (`__printf_chk`). Mitään
monimutkaista kirjastoa ei ole, joten tarkiste lasketaan ohjelmassa
itsessään.

## 3. main ja tarkistefunktio

Riisutussa ohjelmassa ei ole nimiä, joten `main` etsitään tulokohdasta
(luku 7) ja sen kutsuma funktio ristiviittauksesta (luku 3):

```{.bash tiedosto="esimerkit/14-yhteentoimivuus/aja.sh" osa="etsi"}
```

```{.tuloste tiedosto="esimerkit/14-yhteentoimivuus/odotettu" osa="t3"}
```

`main` kutsuu kolmea kirjastofunktiota ja yhtä omaa funktiota rivin ja
sen pituuden välillä: `tarkiste`. Se nimetään (`afn`) ja puretaan.

## 4. Algoritmin lukeminen

```{.tuloste tiedosto="esimerkit/14-yhteentoimivuus/odotettu" osa="t4"}
```

Koodista luetaan algoritmi käsky kerrallaan, luvun 2 ja 5 taidoin:

- Kaksi kerääjää, `edx` (alkuarvo 1) ja `eax` (alkuarvo 0), päivittyvät
  silmukassa tavu kerrallaan.
- `imul rdx,r8` kertoimella `0x828cbfbf` ja `shr rdx,0x27` sekä `imul
  r9d,edx,0xfb` ja vähennys on jakojäännös 251:llä (luku 5:
  $\mathtt{0xfb} = 251$, kokonaissiirto 39 antaa jakajan
  $2^{39} / \mathtt{0x828cbfbf} = 251$). Molemmat kerääjät lasketaan
  siis modulo 251.
- `edx` kasvaa tavulla, `eax` kasvaa `edx`:llä: tämä on Fletcherin
  tarkiste, jossa `a` on tavujen summa ja `b` osasummien summa.
- Lopussa `shl eax,8; or eax,edx` kokoaa tuloksen muotoon
  `(b << 8) | a`, ja `xor ax,0x5a5a` sekoittaa sen vakiolla.
  Tyhjän syötteen haara palauttaa `0x5a5b` eli `(0 << 8 | 1) ^ 0x5a5a`.

## 5. Uudelleentoteutus ja tarkistus

Algoritmi kirjoitetaan Pythonilla ja varmistetaan eroavuustestillä:
samat satunnaiset rivit syötetään alkuperäiselle ohjelmalle ja mallille,
ja tulosten on täsmättävä. Tämä on sama tarkistustapa kuin luvun 9
jäsentimessä ja kääntäjätekniikan differentiaalitestissä.

```{.python tiedosto="esimerkit/14-yhteentoimivuus/tarkiste.py" osa="tarkiste"}
```

```{.tuloste tiedosto="esimerkit/14-yhteentoimivuus/odotettu" osa="t5"}
```

Kahdellatuhannella satunnaisella rivillä ei ole yhtään eroa, joten malli
vastaa ohjelmaa. Tarkiste on nyt dokumentoitu ja toteutettu
uudelleen: yhteentoimivuus on saavutettu. Reunatapaukset (tyhjä rivi,
yhden merkin rivi) on testissä erikseen, koska juuri ne jäävät usein
väärin. Jos myöhemmin löytyy rivi, joka eroaa, malli on puutteellinen
ja analyysiin palataan; eroavuustesti on se verkko, joka sen paljastaa.

## Työn kulku

Esimerkki näyttää takaisinmallinnuksen yleisen kulun:

1. **Havainnoi ulkoapäin** (käytös, strace, tuonnit) ennen koodia.
2. **Löydä aloituskohta** (main, kiinnostava merkkijono, vientifunktio)
   ja etene ristiviittauksin.
3. **Lue kohde** staattisesti ja varmista dynaamisesti; nimeä ja
   kommentoi matkalla.
4. **Muodosta hypoteesi** algoritmista tai muodosta.
5. **Tarkista hypoteesi toteutuksella**: uudelleenkirjoitus, joka
   tuottaa saman tuloksen, on vahvin todiste.

Sama kulku skaalautuu isoihin ohjelmiin, kun jokainen vaihe
skriptataan ja välitulokset talletetaan projektitiedostoon.

## Käytännössä

- **Pidä analyysi toistettavana.** Yksi skripti, joka kääntää kohteen
  ja ajaa kaikki vaiheet, on arvokkaampi kuin muistikuva ruudulta.
- **Varmista jokainen päätelmä.** Luettu algoritmi tarkistetaan
  toteutuksella ja eroavuustestillä, ei silmämääräisesti.
- **Dokumentoi yhteentoimivuustyö.** Kirjaa, mitä tietoa tarvittiin ja
  mihin sitä käytetään; se on sekä hyvää työtä että oikeudellinen
  edellytys.
- **Testaa reunatapaukset erikseen**: tyhjä syöte, maksimipituus,
  nolla-arvot. Ne paljastavat mallin puutteet.

## Itsearviointi

- Osaat yhdistää staattisen ja dynaamisen analyysin yhdeksi
  työnkuluksi aloituskohdasta tarkistettuun tulokseen.
- Osaat lukea tarkistealgoritmin konekielestä ja tunnistaa sen osat
  (modulo-aritmetiikka, kerääjät, sekoitus).
- Osaat toteuttaa algoritmin uudelleen ja varmistaa sen
  eroavuustestillä.
- Osaat kuvata takaisinmallinnuksen yleisen työnkulun ja soveltaa sitä.
