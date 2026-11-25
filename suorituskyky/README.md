# Suorituskyvyn analyysi ja optimointi

Tiivis suomenkielinen tutoriaali ohjelmien suorituskyvyn mittaamisesta
ja parantamisesta laitteiston ehdoilla C23:lla: luotettava mittaus,
Amdahlin laki ja roofline-malli, profilointi (gprof, Callgrind,
Cachegrind, perf), välimuistitietoinen ohjelmointi, datan asettelu ja
lohkominen, haarautumisen ennustus, vektorointi ja SIMD, kääntäjän
optimoinnit (tasot, LTO, PGO) sekä muistinvaraus ja I/O. Lopuksi kuvan
sumennus nopeutetaan vaihe vaiheelta kymmeniä kertoja.
Valmiit dokumentit:
[suorituskyky.pdf](https://saperant.github.io/tutoriaalit/materiaalit/suorituskyky.pdf)
ja pikaopas
[suorituskyky-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/suorituskyky-pikaopas.pdf).

Esitiedot: *Tietokonearkkitehtuuri* (välimuistit, liukuhihna,
haarautumisen ennustus) ja *Algoritmit* (vaativuusanalyysi).
Jatkotaidot: *C++:n suorituskyky*, *Rinnakkaisohjelmointi*,
*GPU-laskenta* ja *Arkkitehtuurin mallinnus ja suunnittelutilan
tutkiminen*.

## Sisältö

1. Johdanto – optimointisykli, piilotettu neliöllinen silmukka,
   esimerkkien kaksi tilaa
2. Mittaaminen – seinäkello ja prosessiaika, toistot, mediaani ja
   MAD, viiveen jakauma ja prosenttipisteet, lämmittely, kääntäjän
   poistama mitattava, regressiotestit
3. Mallit – Amdahlin laki, laskentaintensiteetti, roofline-malli ja
   oman koneen katto
4. Profilointi – gprof, Callgrind, oma ja kumulatiivinen kustannus,
   perf ja laitteistolaskurit, liekkikuvaajat, odottavan ohjelman
   tutkiminen (strace)
5. Välimuistit käytännössä – läpikäyntijärjestys, välimuistirivi,
   viive työjoukon koon mukaan, esihaku ja TLB
6. Datan asettelu ja lohkominen – AoS ja SoA, rakenteen täyte, väärä
   jakaminen, matriisitulo
7. Haarautuminen – lajiteltu ja lajittelematon data, haaraton muoto,
   kääntäjän ehdolliset siirrot
8. Vektorointi ja SIMD – vektorointiraportti, aliasing ja `restrict`,
   liukulukujen järjestys, SSE2- ja AVX2-intrinsicsit
9. Kääntäjän optimoinnit – tasot, `-march`, sisällyttäminen, LTO ja
   PGO
10. Muistinvaraus ja I/O – areena, sivuvirheet, järjestelmäkutsut ja
    puskurointi
11. Tapaustutkimus – laatikkosumennus neljässä vaiheessa
12. Lopuksi – menetelmä, nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`, ja ne toimivat kahdessa
tilassa. Ilman argumentteja ne ajavat toiminnallisen testin:
testaaja kääntää ne GCC 14- ja Clang 20 -kääntäjillä
(`-std=c23 -Wall -Wextra -Wpedantic -Werror`, AddressSanitizer ja
UndefinedBehaviorSanitizer) ja vertaa tulosteet `.odotettu`-tiedostoihin.
Jokainen optimoitu versio testataan perusversiota vastaan. Argumentilla
`--mittaa` ne mittaavat optimoidulla käännöksellä.

`esimerkit/Makefile` ajaa Valgrindin (Cachegrind, Callgrind), gprofin
ja kääntäjän raportit ja tarkistaa niiden deterministisistä luvuista
tekstin väitteet: hutien, väärien ennusteiden ja kutsujen määrät.
Ajoitukset tulostetaan mutta niitä ei verrata. Kirjassa näytetyt
mittaustulokset ovat hakemistossa `esimerkit/tulokset/`, ja kuvaajat
piirretään niistä (`make kuvat`, vaatii Matplotlibin; valmiit kuvat
ovat hakemistossa `kuvat/`). Luvun 4 kutsupuu tuotetaan Callgrindin
tallennetusta tulosteesta (`kaaviot/tee.py`), ja testi tarkistaa, että
kaavio vastaa sitä.

```text
make testaa                   # rakenne, esimerkit ja tarkistukset
make pdf                      # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit tarkista    # Valgrind- ja kääntäjätarkistukset
make -C esimerkit mittaa      # ajoitusmittaukset
make -C esimerkit tulokset    # kirjan tulosteet omalla koneella
make kuvat                    # kuvaajat tuloksista
```

Tarvittavat työkalut: GCC 14, Clang 20, Valgrind, strace, binutils
(gprof, objdump, size) ja Python 3. Kehityskontti:
`.devcontainer/suorituskyky`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
