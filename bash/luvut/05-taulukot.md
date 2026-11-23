# Taulukot ja assosiatiiviset taulukot {.runko-kokoelmat}

Bashissa on kaksi kokoelmatyyppiä: kokonaisluvuilla indeksoitu taulukko
ja merkkijonoavaimin indeksoitu assosiatiivinen taulukko (Bash 4.0).
Kumpikin sisältää vain merkkijonoja, eikä niitä voi sijoittaa sisäkkäin.
Rajoitetuinakin ne ratkaisevat Bashin tärkeimmän ongelman: miten säilyttää
lista arvoja, joissa voi olla välilyöntejä, ilman että ne hajoavat
sanoiksi.

## Taulukon perusoperaatiot

Taulukko luodaan sulkeilla `palvelimet=(alfa beeta)` ja tiedostosta
`mapfile`-komennolla (synonyymi `readarray`), joka lukee jokaisen rivin
omaksi alkiokseen. Valitsin `-t` poistaa rivinvaihdot.

```{.bash tiedosto="esimerkit/05-taulukot.sh" osa="mapfile"}
```

Taulukko voi olla harva: `unset` poistaa alkion, mutta indeksit eivät
siirry. Uudelleensijoitus `a=("${a[@]}")` tiivistää indeksit.

```{.bash tiedosto="esimerkit/05-taulukot.sh" osa="poisto"}
```

`"${a[*]}"` yhdistää alkiot yhdeksi merkkijonoksi `IFS`:n ensimmäisellä
merkillä. Kun `IFS` asetetaan funktion paikalliseksi muuttujaksi,
muutos ei vuoda muualle:

```{.bash tiedosto="esimerkit/05-taulukot.sh" osa="yhdistys"}
```

Suodatus tehdään silmukalla, joka kerää hyväksytyt alkiot uuteen
taulukkoon:

```{.bash tiedosto="esimerkit/05-taulukot.sh" osa="suodatus"}
```

```{.tuloste tiedosto="esimerkit/05-taulukot.odotettu"}
```

| Lauseke | Merkitys |
|---------|----------|
| `"${a[@]}"` | kaikki alkiot, kukin omana sananaan |
| `"${a[*]}"` | kaikki alkiot yhtenä merkkijonona |
| `${#a[@]}` | alkioiden määrä |
| `${!a[@]}` | indeksit tai avaimet |
| `${a[-1]}` | viimeinen alkio (4.3) |
| `"${a[@]:1:2}"` | viipale: kaksi alkiota indeksistä 1 |
| `a+=(x y)` | lisäys loppuun |
| `unset 'a[i]'` | alkion poisto (lainattuna, ettei `[i]` globaa) |

Ero `@`:n ja `*`:n välillä on sama kuin `"$@"`:n ja `"$*"`:n välillä
argumenteissa: `"${a[@]}"` säilyttää alkiot, `"${a[*]}"` yhdistää ne.
Lainaamaton `${a[@]}` jakaa alkiot uudelleen sanoiksi, mikä hävittää
taulukon hyödyn.

## Komento taulukkona

Taulukon tärkein käyttö on komennon kokoaminen osissa. Komentoa ei
rakenneta merkkijonoksi, koska merkkijono pitäisi jakaa sanoiksi
uudelleen, ja silloin välilyönnit ja lainausmerkit hajoavat. Taulukossa
jokainen argumentti pysyy omana alkionaan:

```{.bash tiedosto="esimerkit/05-komento.sh" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/05-komento.odotettu"}
```

Esimerkin `nayta` tulostaa komennon `printf %q`:lla, joten tulosteesta
näkee, miten argumentit jakautuvat. Oikeassa skriptissä viimeinen rivi
olisi `"${komento[@]}"`, joka ajaa komennon. Sama malli toimii
kuivaharjoitukselle (luku 10), `ssh`-komennoille ja kaikelle, missä
valitsimet riippuvat ehdoista.

## Assosiatiiviset taulukot

Assosiatiivinen taulukko on hajautustaulu. Se on esiteltävä ennen käyttöä
`declare -A` tai funktiossa `local -A`. Ilman esittelyä taulukko on
tavallinen, ja avaimet tulkitaan aritmeettisiksi lausekkeiksi: avain
`api` on muuttujan nimi, jonka arvo on yleensä 0.

Tavallisin käyttö on laskeminen avaimittain. Esimerkki laskee HTTP-
tilakoodit pääsylokista:

```{.bash tiedosto="esimerkit/05-sanalaskuri.sh" osa="laskenta"}
```

`${maarat[$koodi]:-0}` antaa nollan avaimelle, jota ei vielä ole; tämä on
tarpeen, koska `set -u` pysäyttäisi skriptin asettamattoman alkion
lukemiseen. Avainten järjestys on määrittelemätön, joten tuloste
lajitellaan:

```{.bash tiedosto="esimerkit/05-sanalaskuri.sh" osa="tulostus"}
```

Avaimen olemassaolo testataan `[[ -v taulu[avain] ]]`:lla (4.3). Se
erottaa puuttuvan avaimen avaimesta, jonka arvo on tyhjä.

```{.bash tiedosto="esimerkit/05-sanalaskuri.sh" osa="olemassaolo"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/05-sanalaskuri.syote"}
```

tuloste on

```{.tuloste tiedosto="esimerkit/05-sanalaskuri.odotettu"}
```

Virheellinen rivi ohitettiin, koska sen neljäs kenttä ei ollut
tilakoodi. Syötteen validointi ennen käyttöä on tarpeen myös siksi, että
avain päätyy aritmeettiseen lausekkeeseen ja tavalliseen taulukkoon
indeksinä; validoimaton syöte siinä voi suorittaa koodia (luku 12).

## Merkkijonot

Merkkijonojen käsittely tehdään parametrilaajennuksilla (luku 3),
`[[ =~ ]]`:lla (luku 4) ja `printf`:llä. Merkkijonon jakaminen osiin
tehdään `read`-komennolla eikä lainaamattomalla laajennuksella, koska
`read` ei globaa:

- `IFS=, read -ra kentat <<< "$rivi"` jakaa pilkuista taulukoksi
- `IFS=: read -r kayttaja _ uid _ <<< "$rivi"` poimii nimetyt kentät

`${#x}` ja `${x:i:n}` laskevat merkkejä lokaalin merkistön mukaan. C-
lokaalissa monitavuinen merkki, kuten `ä`, lasketaan kahdeksi.

## Standardityökalut kokoelmien sijaan

Bashin "standardikirjasto" ovat Unixin työkalut. Suurelle datalle ne ovat
moninkertaisesti nopeampia kuin Bash-silmukka, koska yksi prosessi
käsittelee kaiken:

| Tehtävä | Työkalu |
|---------|---------|
| lajittelu, uniikit | `sort`, `sort -u`, `uniq -c` |
| suodatus | `grep -E`, `grep -F` (kiinteä merkkijono) |
| sarakkeet | `cut -d, -f2`, `awk -F,` |
| korvaus | `sed -E 's/…/…/'` |
| ryhmittely ja summat | `awk` (luku 6) |
| joukko-operaatiot lajitelluille | `comm`, `join` |
| JSON | `jq` |

Nyrkkisääntö: Bash-taulukko kymmenille tai sadoille alkioille, putki ja
työkalut tuhansille tai miljoonille riveille.

## Käytännössä

- **Lista on taulukko, ei välilyönnein eroteltu merkkijono.** Merkkijono
  `"a b c"` hajoaa heti, kun alkiossa on välilyönti.
- **Komento taulukkoon.** `komento=(rsync -a); komento+=(--dry-run);
  "${komento[@]}"`. Tämä korvaa `eval`-käskyn lähes aina.
- **`"${a[@]}"` aina lainattuna.** Tyhjä taulukko laajenee nollaksi
  argumentiksi, mikä on oikein.
- **`declare -A` ennen käyttöä**, ja oletusarvo `${t[$k]:-0}`, kun
  `set -u` on päällä.
- **Lajittele assosiatiivisen taulukon tuloste**, koska avainten
  järjestys vaihtelee Bash-versioittain.
- **`mapfile -t`** tiedoston lukemiseen taulukoksi; ei `a=($(cat t))`,
  joka jakaa ja globaa.
- **Hinta:** tavallinen taulukko on linkitetty lista, joka on nopea
  läpikäyntiin ja loppuun lisäämiseen. Assosiatiivinen taulukko on
  hajautustaulu. Kumpikaan ei sovi satoihin tuhansiin alkioihin;
  silloin data kuuluu putkeen tai toiseen kieleen.

## Itsearviointi

- Osaat lukea tiedoston taulukoksi, käydä sen läpi ja yhdistää alkiot
  erottimella.
- Osaat koota komennon argumentit taulukkoon ehdollisesti ja ajaa sen
  niin, että välilyönnit säilyvät.
- Osaat laskea esiintymät avaimittain assosiatiivisella taulukolla ja
  tulostaa ne lajiteltuina.
- Osaat testata, onko assosiatiivisessa taulukossa tietty avain.
