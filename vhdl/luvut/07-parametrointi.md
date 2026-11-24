# Generic-parametrit ja generate

Uudelleenkäytettävä lohko on parametroitu: väylän leveys, puskurin
syvyys, kanavien määrä ja ajoitusvakiot annetaan instansioinnissa.
VHDL:ssä tähän on kolme välinettä: *generic-parametrit*,
*rajoittamattomat portit*, joiden leveys tulee liitetystä signaalista,
ja `generate`-lauseet, jotka monistavat tai valitsevat rakenteita
elaboroinnissa.

## Generic-parametrit

Generic on entiteetin vakio, jonka arvo kiinnitetään instanssin
`generic map` -osassa. Sillä voi olla oletusarvo. Tyypillisiä ovat
`positive`- tai `natural`-leveydet, `boolean`-valinnat ja `time`-viiveet
testipenkeissä. Generic-parametrista johdetaan muut koot, kuten
luvun 8 CRC-laskimessa, jonka pituuslaskurin leveys lasketaan
funktiolla `bitit(MAKSIMI + 1)`.

Parametroinnin perussääntö on, että käyttäjän antama tieto on yhdessä
paikassa ja muu lasketaan siitä. Jos sama asia annetaan kahdesti, ne
voivat olla ristiriidassa. Silloin entiteetin oma `assert` paljastaa
ristiriidan ennen ensimmäistä kellojaksoa:

```{.vhdl tiedosto="esimerkit/07-tarkistus.kaatuu.vhd" osa="tarkistus"}
```

```{.vhdl tiedosto="esimerkit/07-tarkistus.kaatuu.vhd" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-tarkistus.virhe"}
```

Entiteetin `begin`-osa saa sisältää vain passiivisia lauseita, kuten
`assert`-lauseita, ja ne koskevat jokaista arkkitehtuuria. Parempi
ratkaisu tässä olisi poistaa toinen parametri ja laskea `SYVYYS :=
2**SYVYYS_BITTEINA`, mutta tarkistus on hyödyllinen aina, kun
parametreilla on rajoituksia, joita tyyppi ei ilmaise, kuten parillisuus
tai suurin tuettu arvo. Useimmat synteesityökalut arvioivat tällaiset
väittämät elaboroinnissa ja pysäyttävät synteesin.

## Rajoittamattomat portit

VHDL-2008 sallii portin, jonka tyyppi on rajoittamaton, kuten
`std_logic_vector` ilman leveyttä. Leveys tulee instanssiin liitetystä
signaalista, ja arkkitehtuuri lukee sen attribuuteilla `'length`,
`'range` ja `'element`. Tällöin generic-parametria ei tarvita
lainkaan, eikä parametri ja liitetyn signaalin leveys voi olla
ristiriidassa.

Esimerkki on monikanavainen PWM-lohko. Kanavien määrä ja tarkkuus
tulevat porteista. Pulssisuhteiden taulukko käyttää VHDL-2008:n
mahdollisuutta jättää myös alkion leveys auki:

```{.vhdl tiedosto="esimerkit/07-pwm.vhd" osa="paketti"}
```

```{.vhdl tiedosto="esimerkit/07-pwm.vhd" osa="pwm"}
```

```{.tuloste tiedosto="esimerkit/07-pwm.odotettu"}
```

Alla oleva kaavio on piirretty samasta simulaatiosta. Yhteinen laskuri
kiertää kuusitoista arvoa, ja kukin kanava on ylhäällä niin monta
jaksoa kuin sen pulssisuhde on. Lähdöt ovat rekistereitä, joten ne
seuraavat laskuria yhden jakson viiveellä.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/07-pwm.json" otsikko="Neljän kanavan PWM: pulssisuhteet 0, 4, 8 ja 15 kuudestoistaosaa"}
```

Testipenkki esittelee signaalin `suhteet_t(0 to 3)(3 downto 0)`: neljä
kanavaa, neljän bitin tarkkuus. Arkkitehtuurin vakio `LEVEYS` luetaan
attribuutilla `suhteet'element'length`, ja `assert` tarkistaa, että
lähtöjä on yhtä monta kuin kanavia.

## for-generate

`for ... generate` monistaa rinnakkaisia lauseita, prosesseja tai
instansseja elaboroinnissa. PWM-esimerkissä jokaiselle kanavalle syntyy
oma vertailijaprosessi ja lähtörekisteri. Silmukkamuuttuja `k` on
vakio jokaisessa kopiossa, joten `lahdot(k)` on staattinen viittaus, ja
eri kopiot saavat ohjata saman vektorin eri bittejä.

Generate-lohkolla on nimi (`kanavat`), ja kopiot näkyvät hierarkiassa
nimillä `kanavat(0)`, `kanavat(1)` ja niin edelleen. Lohkoon voi
esitellä omia signaaleja `begin`-sanan edelle, jolloin jokainen kopio
saa omansa.

Prosessin sisäinen `for`-silmukka ja `for-generate` tuottavat usein
saman laitteiston. Silmukka sopii kombinaatiologiikkaan, jossa
iteraatiot riippuvat toisistaan, kuten luvun 4 prioriteettikooderissa.
Generate sopii toisistaan riippumattomiin kopioihin, erityisesti
instansseihin, joita silmukka ei voi luoda.

## if-generate ja geneeriset tyypit

`if ... generate` valitsee rakenteen elaboroinnissa. VHDL-2008 lisäsi
siihen `elsif`- ja `else`-haarat sekä `case ... generate` -muodon.
Seuraava viivelinja käyttää sitä erikoistapaukseen N = 0. Lisäksi
viivelinjan alkiotyyppi on *geneerinen tyyppi*: sama entiteetti
viivästää tavuja, kokonaislukuja tai tietueita.

```{.vhdl tiedosto="esimerkit/07-viive.vhd" osa="viive"}
```

```{.vhdl tiedosto="esimerkit/07-viive.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/07-viive.odotettu"}
```

Geneerisellä tyypillä ei ole operaatioita, joita entiteetti ei saa
parametrina: viivelinja vain kopioi arvoja, joten se ei tarvitse
yhtäsuuruutta tai yhteenlaskua. Jos tarvitsee, VHDL-2008 sallii
aliohjelman generic-parametrina (`function "+" (a, b : alkio_t) return
alkio_t is <>`). Synteesityökalujen tuki geneerisille tyypeille on
parantunut, mutta se kannattaa tarkistaa käytetystä työkalusta ennen
kuin niitä käytetään synteesikoodissa. Testipenkeissä ja malleissa
niitä voi käyttää vapaasti.

## Käytännössä

- **Yksi lähde jokaiselle tiedolle.** Leveys tulee liitetystä
  signaalista tai yhdestä generic-parametrista, ja muut koot
  lasketaan siitä. Kaksi toisistaan riippuvaa parametria on
  ristiriidan paikka.
- **Tarkista parametrien rajoitukset.** Entiteetin `assert` tai
  arkkitehtuurin alussa oleva tarkistus kertoo käyttäjälle, mikä on
  vialla, ennen kuin virhe näkyy outona käytöksenä.
- **Generate-lohkot nimetään.** Nimet näkyvät hierarkiassa,
  aaltomuodoissa ja ajoitusraporteissa.
- **Oletusarvo vain järkevälle oletukselle.** Generic, jolla ei ole
  luontevaa oletusta (esim. kellotaajuus), jätetään ilman, jolloin
  unohtunut arvo on elaborointivirhe.
- **Uusi kieliominaisuus, uusi tuki.** VHDL-2008:n rajoittamattomat
  alkiot ja geneeriset tyypit toimivat simulaattoreissa, mutta
  synteesituki vaihtelee. Ennen kuin piirre otetaan käyttöön
  tuotantokoodissa, se kokeillaan kohdetyökalulla.

## Itsearviointi

- Osaat parametroida entiteetin generic-parametreilla tai
  rajoittamattomilla porteilla ja lukea leveydet attribuuteilla.
- Osaat monistaa logiikkaa `for-generate`-lauseella ja valita
  rakenteen `if-generate`-lauseella.
- Osaat tarkistaa parametrien rajoitukset `assert`-lauseella.
- Osaat kertoa, mitä geneeriset tyypit mahdollistavat ja missä niiden
  tukea on syytä varmistaa.
