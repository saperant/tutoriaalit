# Turvallinen ohjelmointi C:llä

Useimmat muistiturvallisuusvirheet syntyvät muutamasta toistuvasta
kuviosta: koko lasketaan väärin, pituus luetaan syötteestä ja siihen
luotetaan, etumerkillinen ja etumerkitön luku sekoittuvat tai
rajapinta ei kerro puskurin kokoa. Tämä luku käy kuviot läpi ja näyttää,
miten kääntäjä ja staattiset analysaattorit löytävät niitä ennen kuin
ohjelmaa on ajettu kertaakaan.

## Koon laskenta

Taulukon varaus `malloc(n * sizeof(struct mittaus))` on yksi C:n
yleisimmistä riveistä ja yksi vaarallisimmista. Jos `n` tulee
syötteestä, kertolasku voi kiertää etumerkittömän tyypin yli ympäri,
ja varaus jää pieneksi. Myöhemmät kirjoitukset `n` alkioon ylittävät
sen. C23 tuo otsakkeen `<stdckdint.h>`, jonka `ckd_add`, `ckd_sub` ja
`ckd_mul` laskevat tuloksen ja kertovat, mahtuiko se:

```{.c tiedosto="esimerkit/02-turvallinen-c/koko.c" osa="koko"}
```

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="koko"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t1"}
```

Alkioita on $2^{60}+1$ ja alkion koko 16 tavua, joten tulo on
$2^{64}+16$, ja 64-bittisessä `size_t`:ssä siitä jää 16. Naiivi versio
varaisi 16 tavua ja kirjoittaisi niihin yli kvintiljoona alkiota.
`calloc(n, koko)` tarkistaa saman kertolaskun itse, mutta `malloc` ja
`realloc` eivät; glibc:n `reallocarray` on tarkistava vaihtoehto
uudelleenvaraukseen.

Syötteen luku on samaa ketjua. `atoi` ei kerro, oliko merkkijono luku
lainkaan tai mahtuiko se tyyppiin, joten virheellinen syöte muuttuu
hiljaa nollaksi tai mielivaltaiseksi arvoksi. `strtoumax` kertoo
molemmat:

```{.c tiedosto="esimerkit/02-turvallinen-c/koko.c" osa="luku"}
```

Tarkistus `teksti[0] == '-'` on tarpeen, koska `strto*`-funktiot
hyväksyvät etumerkittömiin tyyppeihin miinusmerkin ja palauttavat
luvun komplementin.

## Etumerkit ja vertailut

Pituuskenttä luetaan kehyksestä etumerkillisenä, ja tarkistus vertaa
sitä vain ylärajaan:

```{.c tiedosto="esimerkit/02-turvallinen-c/pituus.c" osa="pura"}
```

Arvo `0xffff` tulkitaan luvuksi $-1$. Se läpäisee ehdon
`pituus > DATA_MAX`, ja `memcpy` saa sen `size_t`:ksi muunnettuna:
$2^{64}-1$ tavua. ASan havaitsee negatiivisen koon jo ennen
kopiointia:

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="pituus"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t2"}
```

Korjattu tarkistus kattaa kolme ehtoa: pituus ei ole negatiivinen, se
mahtuu kohteeseen ja se mahtuu saatuun dataan. Kolmas ehto unohtuu
helpoimmin, ja juuri sen puuttuminen oli Heartbleedin syy (luku 10).
Yleissääntö: **pituus, joka on tullut syötteestä, on väite, ei fakta**,
ja se tarkistetaan sekä kohteen että lähteen todellista kokoa vasten.

## Etumerkillinen ylivuoto

Etumerkillisen kokonaisluvun ylivuoto on C:ssä *määrittelemätöntä
käytöstä*. Kääntäjä saa olettaa, ettei sitä tapahdu, ja poistaa
esimerkiksi tarkistuksen `if (x + 1 < x)` kokonaan. UBSan havaitsee
ylivuodon ajossa:

```{.c tiedosto="esimerkit/02-turvallinen-c/summa.c" osa="summa"}
```

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="summa"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t3"}
```

Korjattu versio laskee summan `ckd_add`-funktiolla ja palauttaa
virheen. Tarkistus tehdään *ennen* laskua tai tarkistavalla
funktiolla, ei jälkikäteen tulosta tutkimalla.

## Turvalliset rajapinnat

Rajapinta, joka ei kerro puskurin kokoa, ei voi tarkistaa sitä. `gets`
poistettiin standardista C11:ssä juuri tästä syystä, ja `strcpy`,
`strcat` ja `sprintf` kärsivät samasta. Nyrkkisäännöt:

| Vältä | Käytä | Huomaa |
|-------|-------|--------|
| `gets` | `fgets`, `getline` | tarkista, mahtuiko rivi |
| `strcpy`, `strcat` | `memcpy` tunnetulla pituudella, `snprintf` | katkaisu on virhetilanne |
| `sprintf` | `snprintf` | paluuarvo kertoo tarvittavan pituuden |
| `strncpy` | `memcpy` tai `snprintf` | ei lisää loppunollaa aina |
| `atoi`, `atol` | `strtol`, `strtoumax` | tarkista `errno` ja loppuosoitin |
| `malloc(a * b)` | `calloc`, `ckd_mul`, `reallocarray` | tarkista kertolasku |

Hiljainen katkaisu on oma virheensä: jos käyttäjänimi katkaistaan 16
merkkiin, kaksi eri nimeä voi muuttua samaksi. Siksi korjatut
esimerkit hylkäävät liian pitkän syötteen eivätkä katkaise sitä.

Ohjeistoista *SEI CERT C Coding Standard* on avoin ja perusteltu
sääntökokoelma (esim. INT32-C etumerkillisistä ylivuodoista, STR31-C
merkkijonojen tilasta). *MISRA C* on sulautettujen ja
turvallisuuskriittisten järjestelmien ohjeisto, joka rajoittaa kieltä
tiukemmin. Molempia valvotaan staattisella analyysilla.

## Kääntäjän varoitukset

Kääntäjä löytää monta virhettä ilman ajoa, kun varoitukset ovat
päällä. Asetustiedoston lukijassa on tyypillisiä virheitä:

```{.c tiedosto="esimerkit/02-turvallinen-c/asetukset.c" osa="lue"}
```

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="varoitukset"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t4"}
```

`-Wconversion` huomaa, että osoitinten erotus (`ptrdiff_t`) kapenee
`int`:ksi, ja `-Wsign-compare` etumerkillisen ja etumerkittömän
vertailun, jossa negatiivinen arvo muuttuisi suureksi. Tuotantokoodin
vähimmäistaso on `-Wall -Wextra`; `-Wconversion` ja `-Wformat=2` ovat
työläämpiä mutta löytävät juuri tämän luvun virheitä. Varoitukset
kannattaa tehdä virheiksi (`-Werror`) CI:ssä, jotta uusia ei kerry.

## Staattinen analyysi

GCC:n `-fanalyzer` seuraa ohjelman polkuja ja muistin tilaa
funktioiden sisällä ja välillä:

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="analyzer"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t5"}
```

Analysaattori löysi polun, jolla arvo vapautetaan kahdesti, ja liitti
löydökseen CWE-luokan (*CWE-415: Double Free*). clang-tidy on toinen
avoin analysaattori; sen tarkistukset valitaan hakemiston
asetustiedostossa:

```{.text tiedosto="esimerkit/02-turvallinen-c/.clang-tidy"}
```

```{.bash tiedosto="esimerkit/02-turvallinen-c/aja.sh" osa="tidy"}
```

```{.tuloste tiedosto="esimerkit/02-turvallinen-c/odotettu" osa="t6"}
```

clang-tidy löysi kapenevan muunnoksen, `strcpy`:n, tarkistamattoman
paluuarvon ja `atoi`:n, ja lisäksi sen, mitä kumpikaan kääntäjä ei
huomannut: `malloc(strlen(erotin + 1))` varaa yhden tavun liian vähän,
koska loppunollalle ei ole tilaa (tarkistus
`misplaced-operator-in-strlen-in-alloc`). Eri analysaattorit löytävät eri asioita, joten
niitä kannattaa ajaa useampaa. Kaupallisia vaihtoehtoja ovat
esimerkiksi Coverity ja CodeQL (jälkimmäinen on maksuton avoimille
projekteille); *Turvallinen kehitys* käsittelee analyysin liittämistä
kehitysprosessiin.

## Käytännössä

- **Tarkista koko ennen varausta.** `ckd_mul` tai `calloc`; älä luota
  siihen, ettei syöte ole koskaan suuri.
- **Kohtele syötteen pituuskenttää väitteenä.** Tarkista se sekä
  kohteen että saadun datan todellista kokoa vasten, ja hylkää
  negatiiviset arvot ennen kuin ne muuttuvat `size_t`:ksi.
- **Valitse rajapinnat, jotka kantavat koon mukanaan**, ja käsittele
  katkaisu virheenä.
- **Varoitukset päälle ja virheiksi.** `-Wall -Wextra -Wconversion
  -Wformat=2 -Werror` uudessa koodissa; vanhassa koodissa varoitukset
  otetaan käyttöön asteittain.
- **Aja ainakin kahta staattista analysaattoria** CI:ssä ja käsittele
  niiden löydökset kuten kääntäjävirheet: korjaa tai perustele.

## Itsearviointi

- Osaat laskea varattavan koon ylivuodolta suojatusti `ckd_mul`-
  funktiolla ja perustella, miksi `malloc(n * koko)` on vaarallinen.
- Osaat tunnistaa etumerkillisen pituuden, joka ohittaa ylärajan
  tarkistuksen, ja kirjoittaa täydellisen rajatarkistuksen.
- Osaat valita turvallisen vaihtoehdon `gets`-, `strcpy`-, `sprintf`-
  ja `atoi`-kutsuille.
- Osaat ajaa GCC:n varoitukset, `-fanalyzer`-analyysin ja clang-tidyn
  ja tulkita niiden löydökset.
