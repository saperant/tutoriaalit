# Muuttujat, lainaus ja laajennukset {.runko-tyypit}

Bashissa on yksi perustyyppi, merkkijono. Luvut ovat merkkijonoja, joita
aritmetiikkalauseke tulkitsee kokonaislukuina, ja taulukot (luku 5) ovat
merkkijonojen kokoelmia. Tyyppien sijaan Bashin ydin on *laajennus*:
miten muuttujaviittaus, komentokorvaus tai kuvio muuttuu komennon
argumenteiksi. Tämä luku käy läpi laajennukset ja lainauksen, joka
hallitsee niitä.

## Muuttujat

Sijoituksessa ei ole välilyöntejä yhtäsuuruusmerkin ympärillä:
`nimi=arvo`. Rivi `nimi = arvo` ajaisi komennon `nimi` argumenteilla `=`
ja `arvo`. Arvo luetaan muuttujasta laajennuksella `$nimi` tai
`${nimi}`; aaltosulkeita tarvitaan, kun nimen perään tulee kirjaimia
(`"${versio}_beta"`) ja kaikissa alla esitellyissä muunnoksissa.

Käytäntönä on:

- **Isot kirjaimet** ympäristömuuttujille (`PATH`, `HOME`) ja skriptin
  vakioille, jotka määritellään `readonly`:llä.
- **Pienet kirjaimet** skriptin omille muuttujille. Näin oma muuttuja ei
  vahingossa korvaa ympäristömuuttujaa: muuttuja nimeltä `PATH` tai
  `USER` muuttaisi koko skriptin toimintaa.
- **`export`** vain muuttujille, jotka lapsiprosessien on nähtävä.
  Viejä on tavallinen muuttuja, joka kopioidaan käynnistettävien ohjelmien
  ympäristöön.
- **`local`** kaikille funktion muuttujille (luku 4).

## Laajennusten järjestys

Bash käsittelee jokaisen komentorivin vaiheittain. Kun järjestyksen
tuntee, lainauksen säännöt ovat johdonmukaisia:

1. aaltosulkulaajennus: `kuva.{png,jpg}` → `kuva.png kuva.jpg`
2. tilde: `~/bin` → `/home/ada/bin`
3. parametri-, komento- ja aritmetiikkalaajennus: `$x`, `$(komento)`,
   `$(( 1 + 2 ))`
4. **sanojen jako**: vaiheen 3 tulokset jaetaan muuttujan `IFS`
   merkeistä (oletuksena välilyönti, sarkain ja rivinvaihto)
5. **polkunimilaajennus** (*glob*): sanat, joissa on `*`, `?` tai `[`,
   korvataan täsmäävillä tiedostonimillä
6. lainausmerkkien poisto

Vaiheet 4 ja 5 kohdistuvat vain lainaamattomiin laajennuksiin.
Kaksinkertaiset lainausmerkit `"$x"` sallivat vaiheen 3 mutta estävät
vaiheet 4 ja 5. Tästä seuraa tutoriaalin tärkein sääntö: **laajennus
lainataan aina**, ellei jakoa tai globia nimenomaan haluta.

## Lainaus

Esimerkki näyttää, mitä lainaamattomalle muuttujalle tapahtuu.
Työhakemistossa on tiedostot `kesän raportti.txt` ja `muistio.txt`.

```{.bash tiedosto="esimerkit/03-lainaus.sh" osa="jako"}
```

```{.bash tiedosto="esimerkit/03-lainaus.sh" osa="glob"}
```

Tulosteen kuusi ensimmäistä riviä (koko tuloste on alempana) näyttävät,
että lainaamaton `$tiedosto` jaettiin kahdeksi argumentiksi ja
lainaamaton `$kuvio` laajeni tiedostonimiksi. Lainattuna kumpikin säilyi
yhtenä argumenttina. Sama virhe komennossa `rm` poistaa väärät tiedostot.
ShellCheck tunnistaa sen (varoitus SC2086):

```{.bash tiedosto="esimerkit/03-siivous.ei-kaanny.sh"}
```

Korjattu rivi käyttää myös erotinta `--`, joka kertoo komennolle, että
valitsimet päättyivät. Ilman sitä tiedostonimi `-rf` tulkittaisiin
valitsimeksi.

Bashissa on kolmenlaisia lainausmerkkejä:

```{.bash tiedosto="esimerkit/03-lainaus.sh" osa="lainaukset"}
```

```{.tuloste tiedosto="esimerkit/03-lainaus.odotettu"}
```

- **Yksinkertaiset** `'…'`: kaikki merkit sellaisenaan, ei laajennuksia.
  Yksinkertaista lainausmerkkiä ei voi esiintyä niiden sisällä.
- **Kaksinkertaiset** `"…"`: laajennukset `$x`, `$(…)` ja `$((…))`
  tehdään, mutta tulosta ei jaeta eikä globata.
- **ANSI-C** `$'…'`: kenoviivasekvenssit kuten `\t`, `\n` ja `\x41`.
  Käytetään erikoismerkkien kirjoittamiseen.

Sijoituksen oikeaa puolta (`kopio=$alkuperainen`) ja `[[ ]]`:n
vasenta puolta ei jaeta, joten lainaus ei niissä ole pakollista. Moni
lainaa silti aina, jotta sääntö on yksinkertainen.

## Parametrilaajennukset

Parametrilaajennukset muokkaavat muuttujan arvoa ilman ulkoisia
ohjelmia. Ne ovat sekä nopeampia että luotettavampia kuin `basename`,
`dirname`, `sed` tai `cut` yksittäisille arvoille.

```{.bash tiedosto="esimerkit/03-laajennukset.sh" osa="polut"}
```

`#` poistaa alusta ja `%` lopusta. Yksi merkki poistaa lyhimmän
täsmäävän osan, kaksi pisimmän. Kuviot ovat glob-kuvioita, eivät
säännöllisiä lausekkeita.

```{.bash tiedosto="esimerkit/03-laajennukset.sh" osa="oletukset"}
```

`${x:-oletus}` antaa oletuksen, jos muuttuja on tyhjä tai asettamaton,
ja `${x:=oletus}` lisäksi asettaa sen. Kaksoispisteetön muoto `${x-o}`
reagoi vain asettamattomaan muuttujaan. Komento `:` ei tee mitään; sitä
käytetään, kun halutaan vain laajennuksen sivuvaikutus.

```{.bash tiedosto="esimerkit/03-laajennukset.sh" osa="merkkijonot"}
```

```{.bash tiedosto="esimerkit/03-laajennukset.sh" osa="pakollinen"}
```

`${1:?viesti}` lopettaa skriptin viestiin, jos argumentti puuttuu. Se on
tiivis tapa ilmaista pakollinen parametri.

```{.tuloste tiedosto="esimerkit/03-laajennukset.odotettu"}
```

| Laajennus | Merkitys |
|-----------|----------|
| `${#x}` | pituus merkkeinä |
| `${x:alku:pituus}` | osajono, negatiivinen alku lopusta (`${x: -3}`) |
| `${x#kuvio}`, `${x##kuvio}` | lyhin/pisin etuliite pois |
| `${x%kuvio}`, `${x%%kuvio}` | lyhin/pisin jälkiliite pois |
| `${x/a/b}`, `${x//a/b}` | ensimmäinen/kaikki korvaukset |
| `${x^}`, `${x^^}`, `${x,,}` | iso alkukirjain, isot, pienet (4.0) |
| `${x:-o}`, `${x:=o}` | oletus, oletus ja sijoitus |
| `${x:?viesti}` | virhe, jos tyhjä tai asettamaton |
| `${x:+arvo}` | `arvo`, jos `x` ei ole tyhjä; muuten tyhjä |
| `${x@Q}` | arvo uudelleen syötettävässä lainatussa muodossa (4.4) |

## Aritmetiikka

Aritmetiikkalauseke `$(( … ))` laskee 64-bittisillä etumerkillisillä
kokonaisluvuilla, ja komento `(( … ))` palauttaa toden, kun tulos on
nollasta poikkeava. Lausekkeen sisällä muuttujat luetaan ilman
`$`-merkkiä.

```{.bash tiedosto="esimerkit/03-aritmetiikka.sh" osa="kokonaisluvut"}
```

Desimaalit hoidetaan *kiinteällä pilkulla*: lasketaan pienemmissä
yksiköissä (sentit, promillet, millisekunnit) ja muotoillaan tulostettaessa.
Pyöristys lähimpään saadaan lisäämällä jakajan puolikas ennen jakoa.

```{.bash tiedosto="esimerkit/03-aritmetiikka.sh" osa="kiintea"}
```

Kun liukulukuja todella tarvitaan, laskenta annetaan `awk`:lle tai
`bc`:lle. Arvot välitetään `awk`:lle muuttujina (`-v`), ei liittämällä
niitä ohjelmatekstiin.

```{.bash tiedosto="esimerkit/03-aritmetiikka.sh" osa="awk"}
```

Ylivuotoa ei tarkisteta, ja nollalla jakaminen on virhe. Etunollallinen
luku tulkitaan oktaaliluvuksi, joten `$(( 08 ))` on virhe. Päivämäärien ja
kellonaikojen kaltaiset arvot muunnetaan kymmenjärjestelmään etuliitteellä
`10#`: `$(( 10#$kuukausi ))`.

## Tulostus ja muotoilu

`printf` on Bashin tulostuskomento. Muotoilumerkkijono toimii kuten C:ssä,
ja jos argumentteja on enemmän kuin määreitä, muotoilua toistetaan:

```{.bash tiedosto="esimerkit/03-aritmetiikka.sh" osa="printf"}
```

```{.tuloste tiedosto="esimerkit/03-aritmetiikka.odotettu"}
```

`echo` sopii vakiotekstin tulostukseen. Muuttujan arvon tulostamiseen se ei
sovi, koska arvo `-n` tai `-e` tulkittaisiin valitsimeksi ja kenoviivojen
käsittely vaihtelee kuorien välillä. `printf '%s\n' "$x"` toimii aina.
Määre `%q` tulostaa arvon lainattuna niin, että sen voi syöttää
uudelleen Bashille (luku 5), ja `printf -v muuttuja` kirjoittaa tuloksen
muuttujaan ilman alikuorta.

Lukujen muotoilu riippuu lokaalista: suomalaisessa lokaalissa `printf`
odottaa ja tulostaa desimaalipilkun. Siksi esimerkki asettaa
`LC_ALL=C`. Skripti, jonka tulostetta toinen ohjelma lukee, asettaa
lokaalin aina itse.

## Käytännössä

- **Lainaa jokainen laajennus.** `"$x"`, `"$(komento)"` ja `"${taulu[@]}"`.
  Poikkeuksia ovat `[[ ]]`:n vasen puoli, sijoituksen oikea puoli ja
  `(( ))`, mutta lainaus ei niissäkään haittaa. Lainaamaton laajennus
  koodissa on merkki siitä, että jakoa tai globia todella halutaan, ja
  silloin se kommentoidaan.
- **Erota valitsimet `--`:lla**, kun argumentti tulee muuttujasta:
  `rm -- "$tiedosto"`, `grep -- "$kuvio" "$tiedosto"`.
- **Parametrilaajennus ulkoisen ohjelman sijaan** yksittäisille arvoille.
  `${polku##*/}` ei käynnistä prosessia, eikä siinä ole `basename`-
  komennon reunatapauksia.
- **Pakolliset parametrit `${1:?}`:llä ja oletukset `${X:-}`:llä**
  funktion tai skriptin alussa. Ne dokumentoivat rajapinnan samalla.
- **Rahat ja prosentit kokonaislukuina.** Kiinteä pilkku on tarkka ja
  nopea. `awk` tai `bc` vain todellisiin liukulukuihin.
- **`printf` datalle, `echo` vakioteksteille.**
- **Kiinteä lokaali**, kun tuloste on toisen ohjelman syötettä tai
  testin odotettu tulos: `export LC_ALL=C`.
- **Hinta:** jokainen `$(…)` on alikuori ja usein uusi prosessi. Kun sama
  tieto tarvitaan silmukassa, se lasketaan kerran silmukan ulkopuolella.

## Itsearviointi

- Osaat selittää laajennusten järjestyksen ja sen, miksi lainaamaton
  muuttuja voi muuttua useaksi argumentiksi tai tiedostolistaksi.
- Osaat valita yksinkertaisten, kaksinkertaisten ja ANSI-C-lainausmerkkien
  välillä.
- Osaat poimia polusta tiedostonimen, hakemiston ja päätteen
  parametrilaajennuksilla.
- Osaat laskea prosenttiosuuden yhden desimaalin tarkkuudella
  kokonaislukuaritmetiikalla.
- Osaat kertoa, miksi `printf '%s\n'` on turvallisempi kuin `echo`
  mielivaltaiselle datalle.
