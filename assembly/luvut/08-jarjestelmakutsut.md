# Järjestelmäkutsut ilman C-kirjastoa

Ohjelma ei voi itse lukea tiedostoa, kirjoittaa näytölle tai varata
muistia käyttöjärjestelmältä: se pyytää ydintä tekemään sen
*järjestelmäkutsulla*. C-kirjaston funktiot, kuten `read`, `write` ja
`exit`, ovat ohuita kääreitä näiden kutsujen ympärillä. Tässä luvussa
kääreet ohitetaan ja ydintä kutsutaan suoraan. Näin nähdään, mitä
kirjaston alla tapahtuu, ja samaa tarvitaan käynnistyskoodissa,
staattisesti linkitetyissä minimaalisissa ohjelmissa ja
tietoturvatutkimuksessa.

## Järjestelmäkutsun sopimus

| Asia | x86-64 Linux | RISC-V Linux |
|-|--------------|--------------|
| Käsky | `syscall` | `ecall` |
| Kutsun numero | `rax` | `a7` |
| Argumentit | `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9` | `a0`–`a5` |
| Paluuarvo | `rax` | `a0` |
| Virhe | paluuarvo −4095…−1 (−errno) | sama |
| Käsky muuttaa lisäksi | `rcx`, `r11` | ei muita |
| `read`, `write`, `exit` | 0, 1, 60 | 63, 64, 93 |

Neljäs argumentti on x86-64:llä `r10` eikä `rcx`, koska `syscall`
tallentaa paluuosoitteen `rcx`:ään ja liput `r11`:een. Muuten sopimus
muistuttaa funktiokutsua. Virhe palautetaan negatiivisena
virhekoodina: `-9` on `-EBADF`. C-kirjaston kääre siirtää koodin
`errno`-muuttujaan ja palauttaa −1. Kutsujen numerot ovat
arkkitehtuurikohtaisia: RISC-V käyttää Linuxin uudempaa, kaikille
uusille arkkitehtuureille yhteistä numerointia, x86-64 historiallista.
Numerot löytyvät otsakkeista `asm/unistd.h` ja hakemistosta
`/usr/include/asm-generic/`.

## Esimerkki: suodin isoille kirjaimille

Ohjelma lukee syötettä, muuttaa ASCII-pienaakkoset isoiksi ja
kirjoittaa tuloksen. Se on klassinen Unix-suodin, kuten `tr a-z A-Z`,
ilman C-kirjastoa:

```{.gnuassembler tiedosto="esimerkit/09-kaiku/x86.S" osa="silmukka"}
```

```{.gnuassembler tiedosto="esimerkit/09-kaiku/rv.S" osa="silmukka"}
```

Syöte:

```{.tuloste tiedosto="esimerkit/09-kaiku/syote"}
```

Tuloste:

```{.tuloste tiedosto="esimerkit/09-kaiku/odotettu"}
```

Silmukka lukee enintään 64 tavua kerrallaan, joten pitkä rivi luetaan
monessa osassa. `read` palauttaa luettujen tavujen määrän, nollan
syötteen loppuessa ja negatiivisen arvon virheessä. Kirjaimen
tunnistus käyttää luvun 4 etumerkitöntä välitarkistusta: `merkki - 'a'`
on välillä 0–25 täsmälleen pienaakkosille.

Tulosteessa näkyy suotimen rajoitus: `äiti` muuttui muotoon `äITI`.
Ä on UTF-8:ssa kaksi tavua (`c3 a4`), eikä kumpikaan ole ASCII-alueella.
Tavuja käsittelevä koodi ei tiedä mitään merkistöstä. Merkistön
tunteva muunnos vaatisi UTF-8:n purkamista ja Unicoden kirjainkoon
taulukoita, mikä on syy käyttää kirjastoa.

Ohjelma alkaa symbolista `_start` eikä funktiosta `main`. Ytimen
käynnistämällä ohjelmalla ei ole paluuosoitetta: pinon päällä on
argumenttien määrä, argumentit ja ympäristömuuttujat (`argc`, `argv`,
`envp`). Ohjelman on lopetettava itsensä `exit`-kutsulla. Paluu
`ret`-käskyllä kaataisi sen. C-ohjelmissa `_start` on C-kirjaston
käynnistyskoodissa (`crt1.o`), joka alustaa kirjaston, kutsuu `main`:ia
ja välittää sen paluuarvon `exit`:lle.

Esimerkissä on kaksi yksinkertaistusta. Ensinnäkin `write` voi
kirjoittaa vähemmän kuin pyydettiin, esimerkiksi kun putki on täynnä
tai kutsu keskeytyy signaaliin. Oikea ohjelma kirjoittaa silmukassa,
kunnes kaikki tavut on kirjoitettu. Toiseksi `read` voi epäonnistua
virheellä `-EINTR`, jolloin kutsu toistetaan. Lopetuskoodi on 1, jos
`read` epäonnistui, ja 0, jos syöte loppui normaalisti.

## Mitä C-kirjasto tekee lisäksi

Ilman C-kirjastoa ohjelma on pieni (staattisena muutamia satoja tavuja
koodia), mutta siltä puuttuu paljon:

- **Puskurointi.** `printf` ja `fwrite` keräävät tulosteen puskuriin ja
  kutsuvat `write`:a harvoin. Jokainen järjestelmäkutsu maksaa satoja
  kellojaksoja kontekstin vaihtoon. Esimerkin 64 tavun puskuri on
  tarkoituksella pieni, jotta paloittelu näkyy. Todellinen suodin
  käyttäisi kymmenien kilotavujen puskuria.
- **Virheiden käsittely ja `errno`.** Kirjasto muuntaa negatiiviset
  paluuarvot `errno`-arvoiksi ja toistaa keskeytyneet kutsut tarvittaessa.
- **Alustus.** Kirjasto alustaa säikeiden paikallisen muistin,
  pinosuojan arvon, staattiset konstruktorit ja muistinvarauksen.
- **Siirrettävyys.** POSIX-rajapinta on sama kaikilla
  arkkitehtuureilla, järjestelmäkutsujen numerot ja sopimukset eivät.

## Käytännössä

- **Käytä kirjastoa, kun voit.** Suorat järjestelmäkutsut kuuluvat
  käynnistyskoodiin, minimaalisiin staattisiin ohjelmiin, ytimen
  testeihin ja hyökkäyskoodin analyysiin. Sovelluskoodissa kirjasto on
  turvallisempi ja siirrettävämpi.
- **Tarkista paluuarvo aina.** Negatiivinen arvo on virhe, ja
  osittainen `write` on normaali tilanne, ei virhe.
- **Muista syscallin sivuvaikutukset.** x86-64:llä `syscall` tuhoaa
  `rcx`:n ja `r11`:n. Silmukkalaskuri `rcx`:ssä ei säily kutsun yli,
  kuten esimerkissä, jossa laskuri alustetaan joka kierroksella.
- **strace näyttää kutsut.** `strace ./ohjelma` listaa jokaisen
  järjestelmäkutsun argumentteineen ja paluuarvoineen. Se on nopein
  tapa tarkistaa, mitä ohjelma todella pyytää ytimeltä.

## Itsearviointi

- Osaat tehdä järjestelmäkutsun `syscall`- ja `ecall`-käskyillä ja
  tiedät kummankin argumentti- ja paluuarvorekisterit.
- Osaat tulkita järjestelmäkutsun paluuarvon, myös negatiiviset
  virhekoodit.
- Osaat kirjoittaa ohjelman, joka alkaa symbolista `_start` ja
  lopettaa itsensä `exit`-kutsulla.
- Osaat luetella, mitä C-kirjasto tekee järjestelmäkutsujen lisäksi,
  ja milloin suorat kutsut ovat perusteltuja.
