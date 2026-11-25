# Tapaustutkimus: sanojen esiintymät

Tehtävä on tavallinen: lasketaan lokitiedoston kaltaisesta tekstistä
kymmenen yleisintä sanaa. Ensimmäinen versio on kirjoitettu niin kuin
C++ usein opetetaan, ja kolme seuraavaa poistavat siitä yksi kerrallaan
tämän tutoriaalin hintoja: virran, tarpeettomat merkkijonot,
solmupuun ja täyden lajittelun. Jokainen versio tuottaa saman
tuloksen, ja jokaisesta mitataan muistinvaraukset, käskyt ja aika.

## Vaihe 1: virta, puu ja lajittelu

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="v1"}
```

Koodi on lyhyt ja oikein, mutta lähes jokainen rivi maksaa.
`std::istringstream` kulkee jokaisen sanan kohdalla virran koneiston
läpi (luku 10). `std::string sana` kasvaa ja kopioituu. `std::map`
varaa solmun jokaiselle uudelle sanalle ja vertaa merkkijonoja
puun jokaisella tasolla. Lopuksi koko sanasto kopioidaan vektoriin ja
lajitellaan, vaikka tarvitaan vain kymmenen ensimmäistä.

## Vaihe 2: oma pilkkoja ja hajautustaulu

Pilkkoja käy tekstin läpi näkyminä, kopioimatta:

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="pilko"}
```

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="v2"}
```

Hajautustaulu tekee haun yhdellä hajautuksella ja vertailulla. Mutta
`maarat[std::string{s}]` rakentaa avaimen joka haulla, ja sanat ovat
yli 15 merkkiä, joten jokainen haku varaa ja vapauttaa muistia, myös
silloin kun sana on jo taulussa.

## Vaihe 3: heterogeeninen haku

C++20 sallii hajautustaulun haun eri tyyppisellä avaimella, jos
hajautin ja vertailija ovat *läpinäkyviä* (engl. transparent):
niillä on jäsentyyppi `is_transparent`. Silloin `find(std::string_view)`
ei rakenna `std::string`iä:

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="v3"}
```

Uusi `std::string` syntyy vain uudelle sanalle. `reserve` varaa
hajautustaulun ämpärit kerralla, joten taulua ei tarvitse rakentaa
uudelleen sen kasvaessa. `std::map` ja `std::set` tukevat samaa
`std::less<>`-vertailijalla jo C++14:stä alkaen.

## Vaihe 4: näkymät avaimina ja osittainen lajittelu

Kun teksti elää koko laskennan ajan, avaimiksi kelpaavat näkymät
tekstiin. Merkkijonoja ei rakenneta lainkaan ennen tulosta, ja
`std::partial_sort` järjestää vain kymmenen ensimmäistä:

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="v4"}
```

Hinta on elinaikasopimus: tulos ei saa viitata tekstiin, joten sanat
kopioidaan tulokseen `std::string`eiksi. Näkymiä avaimina sisältävä
taulu ei saa elää tekstiä pidempään.

## Tulokset

```{.cpp tiedosto="esimerkit/11-sanat.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/11-sanat.odotettu"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-sanat.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/11-sanat.txt"}
```

![Neljä vaihetta kolmella mittarilla. Varaukset ja käskyt on laskettu deterministisesti; ajan pylväissä jana on hajonta (mediaanin absoluuttinen poikkeama).](kuvat/sanat.png){width=95%}

Varausten määrä kertoo tarinan: vaihe 2 tekee niitä eniten, koska
jokainen haku rakentaa avaimen, vaikka se on muuten nopeampi kuin
vaihe 1. Vaihe 3 tekee suunnilleen yhtä monta varausta kuin vaihe 1, nyt vain
uusille sanoille ja niiden solmuille. Vaihe 4 varaa vain hajautustaulun
solmut. Käskymäärä sanaa kohden laskee joka vaiheessa, ja vaihe 4 tekee
alle kolmanneksen vaiheen 1 työstä.

Ajoissa vaiheet 3 ja 4 olivat kirjoittajan kuormitetulla koneella
kohinan rajoissa, ja niiden järjestys vaihteli ajosta toiseen.
Kun käskyt ja varaukset vähenevät mutta aika ei, jäljellä oleva hinta
on muistissa: libstdc++:n hajautustaulun solmut ovat erillisiä
varauksia, ja jokainen haku seuraa osoitinta. Seuraava askel olisi
avoimen osoituksen hajautustaulu (luku 8) tai sanojen numerointi
kokonaisluvuiksi jo jäsennyksessä.

## Menetelmä

Vaiheet noudattavat samaa järjestystä kuin mikä tahansa optimointi:

1. **Oikea ja yksinkertainen ensin.** Vaihe 1 on testien
   vertailukohta, ja jokaisen vaiheen tulosta verrataan siihen.
2. **Mittaa, mihin työ menee.** Varauslaskuri ja Cachegrind kertovat
   ilman kohinaa, mitä kukin muutos poisti.
3. **Poista yksi hinta kerrallaan.** Virta, väliaikaiset avaimet,
   solmut ja täysi lajittelu ovat erillisiä muutoksia, ja jokaisen
   vaikutus on mitattu erikseen.
4. **Vahvista ajalla.** Käskyjen väheneminen ei takaa nopeutusta;
   vaiheiden 3 ja 4 ero osoittaa, että pullonkaula siirtyi muistiin.

## Käytännössä

- **Tekstin käsittely näkyminä**: pilko `std::string_view`iksi ja
  rakenna `std::string` vain, kun arvo tallennetaan.
- **Läpinäkyvä hajautin ja `std::equal_to<>`** hajautustauluihin,
  joiden avaimet ovat merkkijonoja; `std::less<>` järjestettyihin.
- **`reserve` hajautustaululle**, kun avainten määrä tiedetään
  suunnilleen.
- **`std::partial_sort` tai `std::nth_element`**, kun tarvitaan vain
  k ensimmäistä.
- **Pidä vertailuversio testeissä**: yksinkertainen versio on paras
  testi optimoidulle.

## Itsearviointi

- Osaat tunnistaa yksinkertaisesta C++-koodista virran,
  väliaikaisten merkkijonojen, solmusäiliöiden ja täyden lajittelun
  hinnat.
- Osaat käyttää heterogeenista hakua läpinäkyvällä hajauttimella ja
  vertailijalla.
- Osaat käyttää näkymiä avaimina ja määritellä niiden
  elinaikasopimuksen.
- Osaat optimoida vaiheittain niin, että jokaisen vaiheen vaikutus on
  mitattu ja tulos testattu.
