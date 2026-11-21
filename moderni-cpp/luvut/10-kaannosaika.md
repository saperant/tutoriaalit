# Käännösaikainen laskenta

C++ voi suorittaa tavallista koodia jo käännösaikana. Näin laskettu
tulos on ohjelmassa valmiina vakiona, ja virheet, kuten ylivuoto tai
määrittelemätön käyttäytyminen, havaitaan käännösvirheinä.

## `constexpr`-funktiot

`constexpr`-funktio *voidaan* suorittaa käännösaikana, jos sen
argumentit ovat vakiolausekkeita ja tulosta tarvitaan vakiona. Muuten
se suoritetaan ajoaikana kuten tavallinen funktio. C++11:ssä
`constexpr`-funktion runko sai sisältää vain yhden `return`-lauseen;
C++14:stä alkaen silmukat ja paikalliset muuttujat ovat sallittuja.

```{.cpp tiedosto="esimerkit/10-constexpr.cpp" osa="funktio"}
```

`static_assert` tarkistaa ehdon käännösaikana. Jos laskenta
ylivuotaisi, esimerkiksi `kertoma(21)`, ylivuoto olisi
määrittelemätöntä käyttäytymistä, eikä `static_assert` kääntyisi.
Heittomerkit `'` ovat C++14:n numeroerottimia, jotka helpottavat
pitkien lukujen lukemista.

Käännösaikaisella laskennalla voi myös rakentaa hakutaulukoita. Alla
lambda kutsutaan heti, ja sen tulos alustaa vakion:

```{.cpp tiedosto="esimerkit/10-constexpr.cpp" osa="taulukko"}
```

C++20 salli dynaamisen muistinvarauksen käännösaikana, kunhan muisti
vapautetaan ennen laskennan päättymistä. Siksi `constexpr`-funktiossa voi
käyttää `std::vector`- ja `std::string`-olioita. Seuraava funktio
laskee alkulukujen summan Eratostheneen seulalla:

```{.cpp tiedosto="esimerkit/10-constexpr.cpp" osa="vektori"}
```

## `consteval` ja `constinit`

`consteval` (C++20) määrittelee *välittömän funktion*, joka on aina
suoritettava käännösaikana. `constinit` puolestaan takaa, että staattinen
muuttuja alustetaan käännösaikana, mutta muuttuja ei ole vakio vaan sitä
saa muuttaa. Tämä estää niin sanotun staattisen alustusjärjestyksen
ongelman, jossa globaali muuttuja käyttää toista, vielä alustamatonta
globaalia muuttujaa.

```{.cpp tiedosto="esimerkit/10-constexpr.cpp" osa="consteval"}
```

```{.cpp tiedosto="esimerkit/10-constexpr.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-constexpr.odotettu"}
```

Sama `kertoma`-funktio toimii sekä käännös- että ajoaikana.
`consteval`-funktiota taas ei voi kutsua arvolla, joka selviää vasta
ajoaikana:

```{.cpp tiedosto="esimerkit/10-consteval.ei-kaanny.cpp"}
```

Käännösaikainen laskenta pidentää käännösaikaa, mutta se on usein
hyvä kauppa: virheet löytyvät aiemmin, eikä tuloksia tarvitse laskea
joka ajokerralla. Hyvä käytäntö on merkitä `constexpr` kaikki
funktiot, jotka voivat sellaisia olla.
