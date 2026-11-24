# Ohjelman käynnistys

`main` ei ole ohjelman ensimmäinen funktio. Ennen sitä ydin lataa
ohjelman, dynaaminen linkkeri lataa ja sitoo kirjastot, kirjastojen
ja ohjelman alustusfunktiot ajetaan, ja C-kirjaston käynnistyskoodi
valmistelee argumentit. `main`:n palattua sama tehdään käänteisessä
järjestyksessä. Järjestyksen tunteminen ratkaisee kysymykset, kuten
"miksi globaali olio on vielä alustamaton" ja "miksi lokitus ei toimi
destruktorissa".

## Ytimestä mainiin

1. **`execve`**: ydin lukee ELF-otsakkeen ja ohjelmaotsakkeet,
   kartoittaa `LOAD`-segmentit ja lukee `INTERP`-otsakkeesta
   dynaamisen linkkerin polun. Se kartoittaa myös linkkerin ja
   rakentaa pinon: `argc`, `argv`, ympäristö ja *aputaulukko*
   (*auxiliary vector*). Suoritus alkaa dynaamisen linkkerin
   aloitusosoitteesta, ei ohjelman.
2. **`ld.so`**: linkkeri lataa `NEEDED`-kirjastot (luku 7), tekee
   relokaatiot (luku 5) ja sitoo symbolit (luku 8). Se ajaa kirjastojen
   alustusfunktiot riippuvuusjärjestyksessä: kirjasto, jota toinen
   tarvitsee, alustetaan ensin. Lopuksi se hyppää ohjelman
   aloitusosoitteeseen.
3. **`_start`** (`crt1.o`, PIE-ohjelmassa `Scrt1.o`): assemblyllä
   kirjoitettu käynnistyskoodi lukee `argc`:n ja `argv`:n pinosta ja
   kutsuu funktiota `__libc_start_main`.
4. **`__libc_start_main`**: C-kirjasto alustaa itsensä (säikeet,
   `stdio`), ajaa ohjelman alustusfunktiot (`.preinit_array`,
   `.init`, `.init_array`) ja kutsuu `main`:ia.
5. **`exit`**: `main`:n paluuarvo välitetään `exit`:lle, joka ajaa
   `atexit`-käsittelijät ja destruktorit käänteisessä järjestyksessä,
   tyhjentää `stdio`-puskurit ja tekee järjestelmäkutsun `exit_group`.

## Lataaja ja aloituskohta

```{.bash tiedosto="esimerkit/14-kaynnistys/aja.sh" osa="lataaja"}
```

Ohjelman `INTERP`-otsake nimeää dynaamisen linkkerin. Polku on
kiinteä osa x86-64-ABI:a, ja ohjelma ei käynnisty järjestelmässä,
jossa polkua ei ole: tämä on syy virheilmoitukseen `No such file or
directory`, kun ohjelmatiedosto on selvästi olemassa (esimerkiksi
glibc-ohjelma musl-pohjaisessa kontissa). ELF-otsakkeen
aloitusosoite on symbolin `_start` osoite. Osiot `.init_array` ja
`.fini_array` sisältävät alustus- ja lopetusfunktioiden osoitteet;
`.init` ja `.fini` ovat vanhempi mekanismi, jota nykyään käytetään
vain C-kirjaston omaan koodiin.

Ohjelmaan linkitetään automaattisesti käynnistystiedostot, jotka
`gcc -v` näyttää:

| Tiedosto | Lähde | Sisältö |
|----------|-------|---------|
| `Scrt1.o` (`crt1.o`) | glibc | `_start`, PIE-ohjelmissa `S`-versio |
| `crti.o` | glibc | `.init`- ja `.fini`-osioiden alku |
| `crtbeginS.o` | GCC | poikkeustaulujen ja vanhojen konstruktorien tuki |
| *ohjelman objektit* | | |
| `crtendS.o` | GCC | edellisten loppumerkit |
| `crtn.o` | glibc | `.init`- ja `.fini`-osioiden loppu |

`-nostartfiles` jättää ne pois, ja ohjelman on silloin määriteltävä
oma `_start` (luku 11). `-nostdlib` jättää pois sekä käynnistystiedostot
että kirjastot.

## Alustusten järjestys

Attribuutti `constructor` lisää funktion osoitteen
`.init_array`-osioon, ja `destructor` osioon `.fini_array`.
C++-kääntäjä tekee saman globaalien olioiden konstruktoreille.
Esimerkissä sekä jaetulla kirjastolla että ohjelmalla on
alustuksia, ja ohjelma rekisteröi lisäksi `atexit`-käsittelijän:

```{.c tiedosto="esimerkit/14-kaynnistys/kirjasto.c" osa="kirjasto"}
```

```{.c tiedosto="esimerkit/14-kaynnistys/main.c" osa="jarjestys"}
```

```{.bash tiedosto="esimerkit/14-kaynnistys/aja.sh" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/14-kaynnistys/odotettu"}
```

Järjestyksen säännöt:

- **Kirjastot ennen ohjelmaa.** Lataaja alustaa riippuvuudet ennen
  niiden käyttäjiä, joten ohjelman konstruktori voi käyttää kirjastoa.
- **Prioriteetti tiedoston sisällä ja välillä.** Pienempi numero
  ajetaan ensin; prioriteetit 0–100 on varattu toteutukselle. Ilman
  prioriteettia ajetaan viimeisenä.
- **Lopetus käänteisessä järjestyksessä.** `atexit`-käsittelijät ja
  destruktorit muodostavat yhden pinon: `main`:n aikana rekisteröity
  käsittelijä ajetaan ennen konstruktorin aikana rekisteröityä.
  Kirjaston destruktori ajetaan viimeisenä.
- **Prioriteetiton järjestys eri tiedostojen välillä on
  määrittelemätön.** C++:ssa tämä on *staattisen alustuksen
  järjestysongelma* (*static initialization order fiasco*): globaali
  olio, joka käyttää toisen tiedoston globaalia oliota, voi nähdä sen
  alustamattomana. Ratkaisu on funktion sisäinen staattinen muuttuja,
  joka alustetaan ensimmäisellä käytöllä.

`_exit` ja `quick_exit` ohittavat destruktorit, ja kaatuminen ohittaa
kaiken. Tärkeää tietoa ei siksi kannata jättää destruktorin
kirjoitettavaksi.

## Aputaulukko

Ydin välittää ohjelmalle aputaulukon, jossa on tietoja, joita
ohjelma ei muuten saisi ilman järjestelmäkutsua: sivun koko,
ohjelmaotsakkeiden sijainti, aloitusosoite, suorittimen ominaisuudet
ja satunnaislukujen siemen pinon suojaukselle. `LD_SHOW_AUXV=1`
tulostaa sen; skripti poimii muutaman kentän ja peittää osoitteet:

```{.bash tiedosto="esimerkit/14-kaynnistys/aja.sh" osa="auxv"}
```

| Kenttä | Sisältö |
|--------|---------|
| `AT_PHDR`, `AT_PHNUM` | ohjelmaotsakkeet muistissa |
| `AT_ENTRY` | ohjelman aloitusosoite (latausosoite lisättynä) |
| `AT_BASE` | dynaamisen linkkerin latausosoite |
| `AT_PAGESZ` | sivun koko |
| `AT_HWCAP`, `AT_HWCAP2` | suorittimen ominaisuudet |
| `AT_RANDOM` | 16 satunnaista tavua, pinon suojauksen siemen |
| `AT_SECURE` | 1 setuid-ohjelmissa: rajoitettu ympäristö |
| `AT_SYSINFO_EHDR` | vDSO: ytimen kirjasto nopeille kutsuille |

C:ssä kenttiä luetaan funktiolla `getauxval(AT_PAGESZ)`. vDSO on
ytimen jokaiseen prosessiin kartoittama pieni jaettu kirjasto, jonka
kautta esimerkiksi `clock_gettime` toimii ilman järjestelmäkutsua.

## Käytännössä

- **Pidä konstruktorit pieninä.** Ne ajetaan ennen `main`:ia ilman
  virheenkäsittelyä, ja kirjaston konstruktori hidastaa jokaisen
  sitä käyttävän ohjelman käynnistystä. Laiska alustus ensimmäisellä
  käytöllä on lähes aina parempi.
- **Älä luota prioriteetittomaan järjestykseen.** Jos alustus
  riippuu toisesta, tee riippuvuus näkyväksi funktiokutsuna tai käytä
  prioriteettia.
- **Älä käytä muita palveluja destruktorissa.** Lokikirjasto, säikeet
  tai toinen kirjasto voi olla jo purettu. Tyhjennä puskurit ja sulje
  tiedostot hallitusti ennen `main`:n paluuta.
- **Tarkista lataajan polku kontteja varten.** `readelf -l ohjelma |
  grep interpreter`. Musl-pohjaiseen kuvaan tarvitaan musl-käännös
  tai staattinen ohjelma.

## Itsearviointi

- Osaat kuvata vaiheet `execve`:stä `main`:iin ja kertoa, mitä ydin,
  dynaaminen linkkeri ja C-kirjasto kukin tekevät.
- Osaat selittää `INTERP`-otsakkeen ja aloitusosoitteen sekä sen,
  miksi ohjelma voi antaa virheen `No such file or directory`.
- Osaat ennustaa konstruktorien, destruktorien ja
  `atexit`-käsittelijöiden järjestyksen kirjaston ja ohjelman välillä.
- Osaat kertoa, mitä aputaulukko sisältää ja miten sitä luetaan.
