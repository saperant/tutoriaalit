# Johdanto {.runko-johdanto}

Peli on reaaliaikainen simulaatio, jota pelaaja ohjaa. Sekunnissa
kymmeniä kertoja peli lukee syötteen, siirtää maailman tilaa eteenpäin
ja piirtää tuloksen. Kaikki muu, kuten fysiikka, tekoäly, ääni ja
käyttöliittymä, ripustetaan tämän silmukan varaan. Peliohjelmoinnin
vaikeus ei ole yksittäisissä algoritmeissa vaan siinä, että kaiken on
valmistuttava 16 millisekunnissa joka ruudulla, toistettavasti ja ilman
nykimistä.

Tavoitteena on ymmärtää, mitä pelimoottori tekee pelin alla: pelisilmukka, syöte,
tilat, piirto, entiteetit, törmäykset, fysiikka, resurssit, ääni ja
käyttöliittymä. Lopuksi kootaan kokonainen pieni peli, *Kipinä*, ja
sille SDL2-kirjastoon perustuva ikkunaversio.

## Esitiedot ja rajaus

Esitietoina ovat taidot *Moderni C++* ja *Lineaarialgebra*: lukija osaa
modernin C++:n ja lineaarialgebran perusteet (vektorit ja matriisit).

Tutoriaalin pelit ovat kaksiulotteisia. Se ei käsittele seuraavia
aiheita:

- kolmiulotteisen pelin rakenne (orientaatiot, kamerat, 3D-törmäykset,
  animaatio): taito *3D-peliohjelmointi*; luku *3D ja pelimoottorit*
  on silta siihen
- jäykän kappaleen dynamiikka, rajoitteet ja pehmeät kappaleet: taito
  *Pelifysiikka*
- verkkopelaaminen (tilan synkronointi, viiveen piilottaminen,
  rollback): taito *Reaaliaikaiset moninpelit*
- renderöinnin matematiikka ja grafiikkarajapinnat: taidot
  *Renderöinnin perusteet* ja *GPU-ohjelmointi: OpenGL ja Vulkan*.

## Mihin peliohjelmointia tarvitaan

Pelien lisäksi samat rakenteet ovat simulaattoreissa, visualisoinneissa,
virtuaalitodellisuudessa, robotiikan ohjauksessa ja kaikissa
vuorovaikutteisissa reaaliaikasovelluksissa. Kiinteä aika-askel,
deterministinen simulaatio ja tallennettavissa oleva syöte ovat yhtä
tärkeitä lentosimulaattorissa kuin tasohyppelyssä.

Useimmat pelit tehdään nykyään valmiilla pelimoottorilla (Godot, Unity,
Unreal). Moottori ei poista tämän tutoriaalin asioita vaan piilottaa
ne: pelisilmukka, kiinteä fysiikka-askel, komponentit, törmäyskerrokset
ja resurssien elinkaari ovat moottorissa nimetyillä asetuksilla. Kun
ymmärtää, mitä niiden alla tapahtuu, osaa käyttää moottoria oikein ja
tunnistaa sen rajat (luku *3D ja pelimoottorit*).

## Tutoriaalin rakenne

| Luku | Aihe |
|------|------|
| Pelisilmukka | kiinteä aika-askel, interpolointi, determinismi |
| Syöte | toiminnot, reunat, puskurointi, tallennus |
| Pelin tila | tilakoneet, kohtaukset, tapahtumajono |
| 2D-grafiikka | kuvapuskuri, spritet, atlas, animaatio, kamera |
| Entiteetit | oliohierarkia vastaan ECS ja datan asettelu |
| Törmäykset | AABB, ympyrät, SAT, laaja vaihe, tunneloituminen |
| Fysiikka ja törmäysvaste | integraattorit, hyppy, hahmo ja ruutukartta, impulssit, pinot |
| Pelitekoäly | reitinhaku (A\*), näkölinja, vartija |
| Resurssit | kahvat, objektipooli, välimuisti, kuumalataus, tallennus |
| Ääni ja käyttöliittymä | miksaus, välitön käyttöliittymä |
| Kipinä | kokonainen peli ja SDL2-etupää |
| 3D ja pelimoottorit | näkymäpuu, kamera, moottorien periaatteet |

## Esimerkit ja työkalut

Esimerkit ovat C++23:a. Pelilogiikka ja fysiikka eivät tarvitse
kirjastoja, joten ne käännetään ja ajetaan testeissä GCC 14:llä ja
Clang 20:llä AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa.
Molempien kääntäjien tulosteen on oltava sama, mikä samalla varmistaa
simulaation determinismin. Grafiikka piirretään ohjelmistona omaan
kuvapuskuriin, jonka pikseleistä lasketaan tarkistussumma. Ikkunaversio
käyttää SDL2:ta, ja sen testi ajaa ilman näyttöä SDL:n
dummy-videoajurilla.

Kehityskontissa (`.devcontainer/peliohjelmointi`) on kääntäjät ja SDL2.
Tavallisen esimerkin voi kääntää komennolla

```text
g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined 01-silmukka.cpp
```

ja SDL2-esimerkit esimerkkihakemiston Makefilellä (`make sdl`,
`make pelaa`). Ikkunassa pelaaminen vaatii näytön, joten kontissa toimii
vain testitila.

## Ensimmäinen pelisilmukka

Jokainen peli on pohjimmiltaan silmukka, jossa on kolme vaihetta:
syötteen käsittely, tilan päivitys ja piirto. Tila on tavallista dataa.

```{.cpp tiedosto="esimerkit/01-silmukka.cpp" osa="tila"}
```

Päivitys saa aika-askeleen `dt` ja syötteen, ja piirto vain lukee
tilaa. Tässä esimerkissä silmukka ei odota kelloa, joten tuloste on
sama joka ajolla.

```{.cpp tiedosto="esimerkit/01-silmukka.cpp" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/01-silmukka.odotettu"}
```

Vaiheiden erottaminen on tärkeämpää kuin miltä näyttää. Kun päivitys
ei piirrä ja piirto ei muuta tilaa, päivityksen voi ajaa ilman
grafiikkaa (testit, palvelin, tekoälyn harjoittelu), piirtää saman tilan
useaan kertaan (interpolointi, luku *Pelisilmukka*) ja tallentaa
syötteen, josta peli toistuu täsmälleen samana (luku *Syöte*).
