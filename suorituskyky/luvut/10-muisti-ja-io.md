# Muistinvaraus ja I/O

Kaksi tavallista pullonkaulaa ei näy laskennassa lainkaan: muistin
varaaminen ja vapauttaminen sekä järjestelmäkutsut. Kumpikin maksaa
kiinteän hinnan jokaisesta kutsusta, joten ratkaisu on molemmissa
sama: tee harvempia ja suurempia kutsuja.

## Mitä malloc maksaa

`malloc` etsii vapaan lohkon, päivittää varaajan tietorakenteet ja
palauttaa osoitteen; `free` palauttaa lohkon ja yhdistää sen
naapureihinsa. glibcin varaaja käyttää säiekohtaisia välimuisteja
(tcache), joten pieni varaus maksaa parhaimmillaan kymmeniä
nanosekunteja. Hinta kasvaa, kun varauksia on miljoonia, kun säikeet
varaavat ja vapauttavat samaa muistia tai kun lohkot ovat suuria
(yli 128 KiB:n varaukset tehdään omalla `mmap`-kutsullaan). Lisäksi
erikseen varatut oliot hajautuvat ympäri kekoa, mikä huonontaa
välimuistin käyttöä, kun niitä käydään läpi.

## Areena

*Areena* (engl. arena, region, bump allocator) varaa muistia suurina
lohkoina ja jakaa sitä peräkkäin siirtämällä osoitinta. Yksittäisiä
olioita ei vapauteta; koko areena vapautetaan kerralla, kun sen oliot
eivät ole enää tarpeen. Malli sopii kaikkeen, millä on selvä elinkaari:
pyynnön käsittely palvelimessa, kääntäjän yhden funktion syntaksipuu,
pelin yhden ruudun väliaikaiset tiedot.

```{.c tiedosto="esimerkit/10-areena.c" osa="areena"}
```

Varaus pyöristetään `max_align_t`-tyypin tasaukseen, jotta mikä
tahansa tyyppi sopii palautettuun osoitteeseen, kuten `malloc`
lupaa. Lohkon lopussa oleva joustava taulukkojäsen `data[]` on tasattu
samoin. Binäärihakupuu rakennetaan kummallakin varaajalla saman
koodin kautta:

```{.c tiedosto="esimerkit/10-areena.c" osa="puu"}
```

```{.c tiedosto="esimerkit/10-areena.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/10-areena.odotettu"}
```

Kymmenentuhatta `malloc`-kutsua korvautui viidellä 64 KiB:n lohkolla.
Kolmensadantuhannen avaimen puun rakentaminen, läpikäynti ja
vapauttaminen:

```{.tuloste tiedosto="esimerkit/tulokset/10-areena.txt"}
```

Areena oli noin kaksi kertaa nopeampi. Osa erosta tulee varauksista
ja vapautuksesta (yksi `free` lohkoa kohden eikä solmua kohden), osa
siitä, että peräkkäin varatut solmut ovat muistissa lähekkäin. Areenan
riskit ovat elinkaaren virheet: osoitin areenan olioon on
roikkuva, kun areena vapautetaan, ja AddressSanitizer ei näe
areenan sisäisiä virheitä, ellei areena merkitse muistia itse
(`ASAN_POISON_MEMORY_REGION`).

Muita varausstrategioita ovat *olioallas* (engl. pool), joka jakaa
samankokoisia lohkoja vapaalistasta ja sallii yksittäiset
vapautukset, sekä valmis varaaja kuten jemalloc tai mimalloc, joka
voi nopeuttaa paljon varaavaa monisäikeistä ohjelmaa ilman
koodimuutoksia. Paras varaus on kuitenkin se, jota ei tehdä:
taulukon kapasiteetin varaaminen etukäteen, puskurin uudelleenkäyttö
silmukassa ja pienten olioiden sijoittaminen pinoon tai suoraan
taulukkoon.

## Sivuvirheet

Käyttöjärjestelmä antaa muistia sivuina vasta, kun sitä kosketaan
ensimmäisen kerran. Suuri `malloc` palauttaa heti, mutta ensimmäinen
kirjoitus jokaiselle 4 KiB:n sivulle aiheuttaa sivuvirheen, jossa ydin
varaa ja nollaa fyysisen sivun. Sadan megatavun puskurin
ensimmäinen täyttö maksaa siksi kymmeniätuhansia sivuvirheitä, ja
toinen täyttö on huomattavasti nopeampi. Tämä on yksi syy luvun 2
lämmittelyyn. Sivuvirheiden määrän näkee `getrusage`-funktion
kentästä `ru_minflt` tai komennolla `/usr/bin/time -v`. Kuumassa
silmukassa toistuva suuren puskurin varaaminen ja vapauttaminen
maksaa sivuvirheet joka kerta; puskuri kannattaa varata kerran.

## Järjestelmäkutsut ja puskurointi

Järjestelmäkutsu siirtyy käyttäjätilasta ytimeen ja takaisin, ja se
maksaa satoja nanosekunteja tai enemmän (Spectre-korjaukset ovat
lisänneet hintaa). Tiedostoon kirjoittaminen rivi kerrallaan omilla
`write`-kutsuilla maksaa tämän jokaisella rivillä. C:n `stdio`
puskuroi: `fprintf` kirjoittaa muistipuskuriin, ja vasta täysi puskuri
lähetetään yhdellä `write`-kutsulla. Kutsujen määrän voi laskea
virralla, jonka kirjoitusfunktion ohjelma antaa itse:

```{.c tiedosto="esimerkit/10-puskurointi.c" osa="laskuri"}
```

```{.c tiedosto="esimerkit/10-puskurointi.c" osa="tavat"}
```

```{.c tiedosto="esimerkit/10-puskurointi.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/10-puskurointi.odotettu"}
```

Sama miljoona tavua kirjoitettiin 100 000, 133 tai 17 kutsulla.
glibcin oletuspuskuri on 8 KiB tällaiselle virralle (tiedostolle
yleensä tiedostojärjestelmän lohkon koko). Mittaus:

```{.tuloste tiedosto="esimerkit/tulokset/10-puskurointi.txt"}
```

Puskurointi nopeutti kirjoitusta moninkertaisesti. Suurempi puskuri
vähensi kutsuja edelleen kahdeksasosaan, mutta aika ei enää juuri
muuttunut: kun järjestelmäkutsut on karsittu, aika kuluu `fprintf`-
funktion muotoiluun. Tämä on optimoinnin yleinen kulku: kun yksi
pullonkaula poistuu, seuraava tulee näkyviin, ja on mitattava
uudelleen, kannattaako jatkaa.

Muita I/O-keinoja:

- **Lue suurina paloina.** `fread` tai `read` suureen puskuriin ja
  jäsennys muistista on nopeampaa kuin `fgetc` merkki kerrallaan, joka
  maksaa funktiokutsun ja lukituksen jokaisesta merkistä
  (`getc_unlocked` välttää lukituksen).
- **Muistikuvaus.** `mmap` kuvaa tiedoston osoiteavaruuteen, jolloin
  kopiointi puskuriin jää pois. Se sopii suurille, satunnaisesti
  luettaville tiedostoille.
- **Vältä tarpeetonta tyhjennystä.** `fflush` jokaisen rivin jälkeen
  ja rivipuskuroitu `stderr` ovat järjestelmäkutsuja. Lokit kannattaa
  kirjoittaa puskuroituina.
- **Asynkroninen I/O.** Linuxin `io_uring` jonottaa monta I/O-pyyntöä
  yhdellä kutsulla. Se on palvelinohjelmoinnin aihe.

## Käytännössä

- **Laske varaukset ja järjestelmäkutsut** ennen kuin optimoit niitä.
  `ltrace`, `strace -c` ja Valgrindin `--tool=dhat` kertovat määrät.
- **Varaa harvemmin.** Ennakoi kapasiteetti, käytä puskurit uudelleen
  ja varaa kerralla taulukko olioita yksittäisten olioiden sijaan.
- **Käytä areenaa**, kun olioilla on yhteinen elinkaari, ja vapauta
  koko areena kerralla.
- **Puskuroi I/O** ja lue ja kirjoita suurina paloina.
- **Muista sivuvirheet.** Ensimmäinen kosketus suureen muistiin maksaa
  ytimen työtä.

## Itsearviointi

- Osaat selittää, mitä `malloc` ja `free` maksavat ja miksi erikseen
  varatut oliot huonontavat välimuistin käyttöä.
- Osaat toteuttaa areenavaraajan oikealla tasauksella ja kertoa sen
  riskit.
- Osaat selittää, miksi suuren muistialueen ensimmäinen käyttö on
  hidas.
- Osaat mitata järjestelmäkutsujen määrän ja vähentää sitä
  puskuroinnilla.
