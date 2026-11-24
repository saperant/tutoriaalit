# Yleiset sudenkuopat

Kiinteän pilkun virheet ovat harvoin hienovaraisia. Ne tuottavat
väärän etumerkin, kaksinkertaisen arvon tai kokonaan väärän tuloksen,
mutta usein vain tietyillä arvoilla, joten testit eivät välttämättä
löydä niitä. Tähän lukuun on koottu tavallisimmat.

## Etumerkkilaajennus

Laitteistorekisterien kentät ovat usein kapeampia kuin ohjelman tyypit.
12-bittinen AD-muunnin palauttaa kahden komplementin näytteen 16-bittisen
rekisterin alimmissa biteissä, ja ylimmissä biteissä voi olla tilabittejä.
Pelkkä maskaus hävittää etumerkin:

```{.c tiedosto="esimerkit/10-etumerkki.c" osa="laajennus"}
```

```{.c tiedosto="esimerkit/10-etumerkki.c" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/10-etumerkki.odotettu"}
```

Positiiviset näytteet toimivat, joten virhe löytyy vasta, kun signaali
käy negatiivisena. Laajennus `(x ^ m) - m`, jossa `m` on etumerkkibitin
paino, on siirrettävä eikä riipu siirtojen toteutuksesta. Laitteistossa
etumerkkilaajennus on pelkkää johdotusta: etumerkkibitti kytketään
ylimpiin bitteihin.

## Kertolasku kapeassa tyypissä

C laskee lausekkeen operandien tyypissä, ei sen muuttujan tyypissä,
johon tulos sijoitetaan. Vakio `3 * (1 << 30)` lasketaan `int`-tyypissä ja
vuotaa yli, vaikka tulos sijoitetaan 64-bittiseen muuttujaan. Kääntäjä
huomaa vakiolausekkeen ylivuodon käännösaikana:

```{.c tiedosto="esimerkit/10-kapea.ei-kaanny.c" osa="raja"}
```

```text
error: integer overflow in expression of type 'int' results in
'-1073741824' [-Werror=overflow]
```

Korjattu versio laskee `int64_t`-tyypissä, koska ensimmäinen operandi
`INT64_C(1)` on jo leveä. Sama virhe ajonaikaisissa arvoissa ei näy
käännöksessä: `a * b`, jossa `a` ja `b` ovat `int32_t`-tyyppisiä, lasketaan
32 bitissä, vaikka tulos sijoitettaisiin `int64_t`:hen. Q1.31-kertolaskussa
toinen operandi muunnetaan siksi aina ensin leveämmäksi:
`(int64_t)a * b`.

## Määrittelemätön ylivuoto C:ssä

Laitteiston kertymä kiertää, mutta C:n etumerkillinen ylivuoto on
määrittelemätön käyttäytyminen: kääntäjä saa olettaa, ettei sitä
tapahdu, ja optimoida sen mukaan. Bittitarkka C-malli, joka luottaa
kiertoon `int32_t`-kertymässä, voi toimia ilman optimointeja ja hajota
`-O2`:lla. UBSan pysäyttää ohjelman:

```{.c tiedosto="esimerkit/10-ylivuoto.kaatuu.c" osa="kertyma"}
```

```text
runtime error: signed integer overflow: 1073741824 + 1073741824
cannot be represented in type 'int'
```

Jos kierto on tarkoitettu, se mallinnetaan etumerkittömillä tyypeillä
(`uint32_t`, jonka ylivuoto on määritelty) ja muunnetaan lopuksi
etumerkilliseksi, kuten luvun 5 `kierto`-funktiossa. Jos kierto ei ole
tarkoitettu, kertymä levennetään.

## Muita tavallisia virheitä

| Virhe | Oire | Korjaus |
|-------|------|---------|
| `x / 2` siirron sijaan | negatiiviset pyöristyvät eri suuntaan kuin laitteistossa | malliin `lattia(x, 1)` |
| siirto ≥ tyypin leveys | määrittelemätön, usein ”ei mitään” | tarkista siirtomäärän raja |
| $-1 \times -1$ | tulos −1 tai ylivuoto | saturoi kulmatapaus |
| pyöristys ennen kertymää | ylimääräinen kohina | pyöristä vasta lopuksi |
| muoto väärin dokumentoitu | kertaa 2 tai 1/2 virhe | muoto nimeen tai tyyppiin |
| etumerkitön vähennyslasku | suuri positiivinen tulos | laajenna ennen vähennystä |

## Käytännössä

- **Testaa ääriarvot.** Testivektoreihin kuuluvat aina
  $-2^{n-1}$, $2^{n-1} - 1$, 0 ja −1 sekä niiden kaikki parit
  kertolaskuun. Satunnaiset testit eivät osu kulmatapauksiin.
- **Käännä mallit sanitoijilla.** UBSan löytää määrittelemättömät
  ylivuodot ja siirrot, jotka optimoiva kääntäjä muuten piilottaisi.
- **Kirjoita leveyden muunnos näkyviin.** `(int64_t)a * b` on parempi
  kuin luottamus C:n korotussääntöihin. Lukija näkee heti, missä
  leveydessä tulo lasketaan.
- **Mallinna kierto etumerkittömillä tyypeillä.** Kun laitteisto
  kiertää, mallikin kiertää määritellysti.

## Itsearviointi

- Osaat laajentaa kapean kentän etumerkillisen arvon siirrettävästi.
- Osaat selittää, missä tyypissä C laskee lausekkeen, ja välttää
  kertolaskun kapeassa tyypissä.
- Osaat mallintaa laitteiston kiertävän aritmetiikan C:llä ilman
  määrittelemätöntä käyttäytymistä.
- Osaat laatia testivektorit, jotka kattavat kiinteän pilkun
  kulmatapaukset.
