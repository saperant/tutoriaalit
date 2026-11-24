# Johdanto {.runko-johdanto}

Renderöinti tarkoittaa kuvan laskemista kuvauksesta: kolmioverkoista,
materiaaleista, valoista ja kamerasta. Näytönohjain tekee sen
miljardeille pikseleille sekunnissa, mutta sen tekemä työ on
periaatteessa yksinkertaista. Jokainen kolmion kärki kerrotaan
matriiseilla, kolmio jaetaan pikseleiksi, jokaiselle pikselille
lasketaan väri ja lähimmän pinnan väri jää näkyviin. Tämä tutoriaali
rakentaa koko ketjun alusta asti tavallisena C++-ohjelmana, jotta
jokainen vaihe on näkyvissä ja testattavissa.

Esitietoina ovat taidot *Lineaarialgebra* ja *Moderni C++*.
Lineaarialgebrasta tarvitaan vektorit, matriisit, homogeeniset
koordinaatit sekä katse- ja perspektiivimatriisi, jotka johdettiin
sen luvussa *Homogeeniset koordinaatit*. Täällä niitä
käytetään eikä johdeta uudelleen: kun matriisi tulee vastaan, luku
kertoo, mitä sen tulos tarkoittaa pikseleiden kannalta.

## Mihin renderöinnin perusteita tarvitaan

Pelit, CAD-ohjelmat, karttasovellukset, lääketieteellinen kuvantaminen,
käyttöliittymät ja datan visualisointi piirtävät kaikki kolmioita
saman putken läpi. Grafiikkarajapinnat (OpenGL, Vulkan, Direct3D,
Metal) ja pelimoottorit piilottavat putken kiinteät vaiheet ja
jättävät ohjelmoijalle varjostimet. Kun putki on kerran rakennettu
itse, rajapintojen käsitteet asettuvat paikoilleen: miksi syvyyspuskuri
on epälineaarinen, miksi tekstuuri välkkyy kaukana, mistä kolmioiden
välinen sauma tulee ja miksi normaalit pitää muuntaa eri matriisilla
kuin paikat.

Ohjelmistorasteroijaa käytetään myös sellaisenaan: testeissä ja
palvelimilla ilman näytönohjainta (Mesa llvmpipe, SwiftShader),
upotetuissa laitteissa ja työkaluissa, jotka tuottavat kuvia
eräajona. Taito *Peliohjelmointi* piirsi 2D-grafiikkansa omalla
ohjelmistorenderöijällä; tässä samaa ajatusta jatketaan kolmanteen
ulottuvuuteen.

## Tutoriaalin rakenne

| Luku | Aihe |
|------|------|
| Kuvat ja pikselit | kuvapuskuri, lineaarinen valo, sRGB, PPM |
| Viivat | Bresenhamin algoritmi, DDA |
| Kolmiot | reunafunktiot, vasen-ylä-sääntö, barysentriset painot |
| Muunnokset | malli-, näkymä- ja projektiomatriisi, näkymäportti |
| Perspektiivi | perspektiivikorjattu interpolointi |
| Leikkaus | lähitaso, Sutherland–Hodgman, hylkäys |
| Syvyys ja näkyvyys | z-puskuri, tarkkuus, takapintojen karsinta |
| Valaistus | Lambert, Phong, Blinn–Phong, varjostustavat |
| Tekstuurit | näytteenotto, suodatus, mipmapit |
| Reunanpehmennys | SSAA, MSAA, näytekuviot |
| Grafiikkaputki | varjostimet funktioina, koko kohtaus |

Luvuissa rakentuu pieni kirjasto, joka on hakemistossa
`esimerkit/yhteinen/`: kuvapuskuri (`kuva.hpp`), vektorit ja matriisit
(`vektori.hpp`), rasterointi (`rasteri.hpp`), mallit (`malli.hpp`),
tekstuurit (`tekstuuri.hpp`), valaistus (`valo.hpp`) ja itse putki
(`putki.hpp`). Kirjasto on kirjoitettu selkeäksi, ei nopeaksi; luvussa
*Grafiikkaputki* kerrotaan, mitä nopea toteutus tekisi toisin.

Jatkotaidot ovat *GPU-ohjelmointi*, joka siirtää saman putken
näytönohjaimelle OpenGL:llä ja Vulkanilla, ja *Säteenseuranta ja
fysikaalinen valaistus*, joka laskee valon kulun toisella tavalla:
pikselistä maailmaan eikä kolmiosta pikseleihin.

## Esimerkit ja testaus

Esimerkit ovat C++23:a ilman ulkoisia kirjastoja. Testeissä jokainen
käännetään GCC 14:llä ja Clang 20:llä AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa, ja kummankin tulosteen on oltava
täsmälleen sama kuin tiedostossa `<nimi>.odotettu`. Kuvista tulostetaan
tarkistussumma, peitto ja keskikirkkaus, joten yksikin muuttunut pikseli
näkyy testissä:

```text
kolmio         summa 735413f5  peitto  1036/3072  kirkkaus 48
```

Tarkistussumma on FNV-1a-tiiviste kuvan tavuista. Jotta tulos olisi
sama kahdella kääntäjällä, esimerkit noudattavat muutamaa sääntöä:
kierrot annetaan kosinina ja sinina eikä kulmina (trigonometristen
funktioiden tarkkuus vaihtelee toteutuksittain), kärkipisteet
pyöristetään kiinteän pilkun ruudukkoon ennen peittotestiä (luku
*Kolmiot*) ja värit pyöristetään tavuiksi vasta lopuksi. Samat
käytännöt tekevät renderöijästä testattavan muutenkin: kuvan voi
tallentaa vertailukuvaksi ja ajaa regressiotestinä.

Esimerkit kirjoittavat kuvan myös PPM-tiedostoon. Tämän dokumentin
kuvat on tuotettu niistä komennolla `make kuvat`, joka kääntää
esimerkit optimoituina ja muuntaa kuvat PNG-muotoon pienellä
Python-skriptillä (`kuvat/ppm2png.py`).

## Työkalut

```text
make testaa   # rakenne, esimerkit kahdella kääntäjällä
make pdf      # tämä dokumentti ja pikaopas
make kuvat    # kuvitus hakemistoon kuvat/
```

Kehityskontissa (`.devcontainer/renderoinnin-perusteet`) ovat GCC,
Clang, Pandoc ja TeX. Yksittäisen esimerkin voi kääntää ja ajaa
suoraan:

```text
g++ -std=c++23 -O2 esimerkit/09-varjostus.cpp -o varjostus
./varjostus && display 09-varjostus.ppm
```

PPM-tiedoston avaavat useimmat kuvankatseluohjelmat (GIMP, ImageMagick,
feh). Sanitoijien kanssa käännetty versio on hidas mutta paljastaa
puskurien ylitykset heti, mikä on rasteroijassa tavallisin virhe.
