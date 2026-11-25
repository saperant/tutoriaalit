# Dynaaminen muistinhallinta {.runko-muisti}

Paikallinen muuttuja tuhoutuu, kun sen funktio palaa, ja staattisen
muuttujan koko on päätettävä käännösaikana (luku 5, Olion elinaika).
Kun datan on elettävä sen luonutta funktiota pidempään tai sen koko
selviää vasta ajon aikana, se varataan *keosta*. Keosta varattu muisti
on olemassa, kunnes ohjelma itse vapauttaa sen. Tämä vapaus on myös
C:n suurin virhelähde, joten luvussa käydään varaamisen lisäksi läpi
omistus, kolme vakiintunutta varausmallia ja tyypilliset virheet.

## `malloc`, `calloc`, `realloc` ja `free`

Otsikon `<stdlib.h>` funktio `malloc(n)` varaa `n` tavua ja palauttaa
osoittimen varattuun muistiin tai tyhjän osoittimen, jos muistia ei ole.
Muistin sisältö on alustamaton. `calloc(n, koko)` varaa `n` alkiota ja
alustaa ne nolliksi. Varattu muisti vapautetaan funktiolla `free`.

```{.c tiedosto="esimerkit/08-malloc.c" osa="perusteet"}
```

```{.dot otsikko="Esimerkin muisti `malloc`-kutsun ja silmukan jälkeen. Osoitin `luvut` on pinossa, sen osoittama taulukko keossa. Kun `main` palaa, osoitin katoaa, mutta keon lohko säilyy, ellei sitä ole vapautettu."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.9;
  node [shape=plain, style=""];
  pino [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><b>Pino</b> <font point-size="8">(main-funktion muuttujat)</font></td></tr>
    <tr><td align="left" bgcolor="#EEF1F6" width="150">n = 5</td></tr>
    <tr><td align="left" bgcolor="#EEF1F6" port="l">luvut</td></tr></table>>];
  keko [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="5"><b>Keko</b> <font point-size="8">(malloc: 5 × sizeof(int) tavua)</font></td></tr>
    <tr><td port="a" bgcolor="#EEF1F6" width="30">0</td><td bgcolor="#EEF1F6" width="30">1</td><td bgcolor="#EEF1F6" width="30">4</td><td bgcolor="#EEF1F6" width="30">9</td><td bgcolor="#EEF1F6" width="30">16</td></tr></table>>];
  staattinen [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><b>Staattinen muisti</b> <font point-size="8">(koko ajon ajan)</font></td></tr>
    <tr><td align="left" bgcolor="#EEF1F6" width="150">"muisti loppui\n"</td></tr></table>>];
  pino:l:e -> keko:a:w;
  staattinen -> keko [style=invis];
  {rank=same; pino; staattinen}
}
```

Muutama vakiintunut käytäntö:

- Koko lasketaan muodossa `n * sizeof *osoitin`. Se pysyy oikeana,
  vaikka osoittimen tyyppi muuttuisi.
- Paluuarvo tarkistetaan aina.
- `malloc`-kutsun paluuarvoa ei muunneta tyyppimuunnoksella; C:ssä
  `void *` muuntuu automaattisesti.
- Vapautuksen jälkeen osoitin kannattaa asettaa tyhjäksi.
  `free(nullptr)` on sallittu eikä tee mitään.

## Omistus

C ei kerro, kuka vastaa muistin vapauttamisesta. Siitä on sovittava
rajapinnassa ja kerrottava dokumentaatiossa. Tavallinen käytäntö on,
että funktio, joka palauttaa dynaamisesti varatun olion, siirtää sen
*omistuksen* kutsujalle:

```{.c tiedosto="esimerkit/08-malloc.c" osa="yhdista"}
```

```{.c tiedosto="esimerkit/08-malloc.c" osa="omistus"}
```

```{.tuloste tiedosto="esimerkit/08-malloc.odotettu"}
```

C23 standardoi POSIX-järjestelmistä tutun funktion `strdup`, joka
varaa kopion merkkijonosta.

## Kasvava taulukko

`realloc(p, koko)` muuttaa varatun alueen kokoa. Se voi joutua
siirtämään datan uuteen paikkaan, joten se palauttaa uuden osoittimen.
Jos varaus epäonnistuu, `realloc` palauttaa tyhjän osoittimen ja jättää
vanhan alueen ennalleen. Paluuarvo on siksi otettava ensin
apumuuttujaan: kirjoittamalla suoraan `p = realloc(p, koko)` vanha
osoitin katoaisi virhetilanteessa, ja muisti vuotaisi.

Seuraava dynaaminen taulukko kaksinkertaistaa kapasiteettinsa aina,
kun tila loppuu. Näin lisäys on keskimäärin vakioaikainen.

```{.c tiedosto="esimerkit/08-vektori.c" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/08-vektori.c" osa="lisaa"}
```

```{.c tiedosto="esimerkit/08-vektori.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-vektori.odotettu"}
```

Lauseke `(Vektori){}` on *yhdistetty literaali* (*compound literal*):
nimetön, nolliksi alustettu `Vektori`-olio, jolla vanha arvo
korvataan (luku 6).

## Joustava taulukkojäsen

Rakenteen viimeinen jäsen voi olla kooltaan määrittelemätön taulukko
(C99). Rakenne ja sen vaihtelevanpituinen data varataan silloin yhdellä
`malloc`-kutsulla ja vapautetaan yhdellä `free`-kutsulla:

```{.c tiedosto="esimerkit/08-joustava.c" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/08-joustava.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-joustava.odotettu"}
```

## Tyypilliset virheet

Dynaamisen muistin virheet ovat C-ohjelmien yleisimpiä ja vakavimpia
virheitä:

- **Muistivuoto**: muistia ei vapauteta, ja ohjelman muistinkulutus
  kasvaa.
- **Käyttö vapautuksen jälkeen** (*use after free*): vapautettua muistia
  luetaan tai siihen kirjoitetaan. Muisti on ehkä jo annettu toiseen
  käyttöön.
- **Kaksoisvapautus**: sama alue vapautetaan kahdesti, mikä sotkee
  muistinhallinnan tietorakenteet.
- **Ylivuoto**: kirjoitetaan varatun alueen ohi.

Nämä virheet eivät yleensä kaada ohjelmaa heti, vaan ne turmelevat
muistia ja aiheuttavat oireita aivan muualla. Siksi testaus
sanitoijien kanssa on C-ohjelmoinnissa välttämätöntä. Seuraavassa
ohjelmassa ainoa osoitin varattuun muistiin katoaa:

```{.c tiedosto="esimerkit/08-vuoto.kaatuu.c"}
```

AddressSanitizer (LeakSanitizer) ilmoittaa ohjelman lopussa:

```{.tuloste tiedosto="esimerkit/08-vuoto.virhe"}
```

Ilmoituksessa on myös kutsupino, josta näkee, missä vuotanut muisti
varattiin. Toisessa esimerkissä kaksi rakennetta jakaa saman muistin, ja
toisen vapauttaminen jättää toiseen roikkuvan osoittimen:

```{.c tiedosto="esimerkit/08-vapautettu.kaatuu.c"}
```

```{.tuloste tiedosto="esimerkit/08-vapautettu.virhe"}
```

```{.dot otsikko="Rakenteen sijoitus kopioi osoittimen, ei sen osoittamaa muistia. Kun lohko vapautetaan `a`:n kautta, myös `b.arvot` osoittaa vapautettuun muistiin."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.8;
  node [shape=record, style="filled", height=0.3];
  a [label="{Taulu a | <p> arvot}"];
  b [label="{Taulu b | <p> arvot}"];
  lohko [shape=plain, style="", label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="4"><font point-size="8">keon lohko (vapautettu)</font></td></tr>
    <tr><td port="a" width="26" style="dashed">42</td><td width="26" style="dashed">?</td><td width="26" style="dashed">?</td><td width="26" style="dashed">?</td></tr></table>>];
  a:p:e -> lohko:a:w [label="free"];
  b:p:e -> lohko:a:w [label="luku", style=dashed];
}
```

Kun virhe on saman funktion sisällä, GCC voi havaita sen jo
käännösaikana (`-Wuse-after-free`), mutta funktiorajojen yli ulottuvat
virheet löytyvät vain ajon aikana. Parhaiten virheitä ehkäisee selkeä
omistuskäytäntö: jokaisella varauksella on yksi omistaja, joka
vapauttaa sen.

## Areena: yhteinen elinaika

Jos monella oliolla on sama elinaika, esimerkiksi yhden verkkopyynnön
käsittelyn ajan, niitä ei kannata varata ja vapauttaa yksitellen.
*Areena* (*arena*, *bump allocator*) varaa yhden suuren lohkon ja jakaa
siitä paloja peräkkäin. Koko areena vapautetaan tai tyhjennetään
kerralla. Tekniikkaa käyttävät esimerkiksi kääntäjät, pelimoottorit ja
verkkopalvelimet.

```{.c tiedosto="esimerkit/08-areena.c" osa="areena"}
```

Paloja tasataan `max_align_t`-tyypin vaatimaan rajaan, jotta niihin voi
sijoittaa minkä tahansa tyyppisen olion. Tasaus näkyy tulosteessa: kolme
merkkijonoa ja kolme solmua vievät 96 tavua, vaikka dataa on vähemmän.

```{.c tiedosto="esimerkit/08-areena.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-areena.odotettu"}
```

Areenassa yksittäistä oliota ei voi vapauttaa, mutta vuotoja ei myöskään
synny: kun käsittely päättyy, kaikki vapautuu yhdellä kutsulla.

## Käytännössä

- **Yksi omistaja jokaiselle varaukselle.** Omistus kirjataan funktion
  kommenttiin ("kutsuja vapauttaa"). Kun omistus siirtyy, lähettäjän
  osoitin nollataan.
- **Symmetriset parit.** Jokaisella `_luo`- tai `_init`-funktiolla on
  `_tuhoa`- tai `_vapauta`-pari, ja tuhoamisfunktio hyväksyy tyhjän
  osoittimen kuten `free`. Kutsujan siivouskoodi yksinkertaistuu.
- **`n * sizeof *p` ja ylivuoto.** Koon laskemisen kertolasku voi
  ylivuotaa suurilla `n`:n arvoilla, jolloin varataan liian vähän. Tarkista
  kertolasku (`ckd_mul`) tai käytä `calloc`ia, joka tarkistaa sen itse.
- **Kasvatus geometrisesti.** Kapasiteetti kaksinkertaistetaan (tai
  kerrotaan 1,5:llä), jolloin lisäys on keskimäärin vakioaikainen.
- **Varauksen epäonnistuminen.** Kirjasto palauttaa virheen. Sovellus voi
  käyttää käärettä (usein nimeltään `xmalloc`), joka lopettaa ohjelman
  hallitusti, jos muisti loppuu, kunhan valinta on tietoinen.
- **Areenat ja poolit**, kun olioilla on yhteinen elinaika tai sama koko.
  Ne vähentävät `malloc`-kutsuja ja tekevät vuodot lähes mahdottomiksi.
- **Sanitoijat aina testeissä.** Vuodot ja vapautetun muistin käyttö
  löytyvät AddressSanitizerilla.

## Itsearviointi

- Osaat kirjoittaa dynaamisesti kasvavan taulukon, joka säilyy ehjänä,
  jos `realloc` epäonnistuu.
- Osaat dokumentoida ja noudattaa omistussääntöä funktion rajapinnassa.
- Osaat toteuttaa areenan ja kertoa, milloin se sopii yksittäisiä
  varauksia paremmin.
- Osaat tulkita AddressSanitizerin raportin muistivuodosta ja vapautetun
  muistin käytöstä.
