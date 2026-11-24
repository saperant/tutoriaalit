# Osajonot ja editointietäisyys

Kahden merkkijonon vertailu on dynaamisen ohjelmoinnin tunnetuin
sovellus. Versionhallinta näyttää tiedostojen erot, oikoluku ehdottaa
lähintä oikein kirjoitettua sanaa, ja bioinformatiikka kohdistaa
DNA-jaksoja toisiinsa. Kaikissa osatehtävä on sama: kahden
merkkijonon alkuosat $a_0 \ldots a_{i-1}$ ja $b_0 \ldots b_{j-1}$.
Taulukossa on $(n + 1)(m + 1)$ alkiota, ja jokainen lasketaan
vakioajassa kolmesta naapuristaan.

## Pisin yhteinen osajono

*Osajono* saadaan merkkijonosta poistamalla merkkejä järjestystä
muuttamatta; toisin kuin alimerkkijonon, sen merkkien ei tarvitse olla
peräkkäin. *Pisin yhteinen osajono* (engl. longest common subsequence,
LCS) on pisin jono, joka on molempien osajono. Sanoilla ALGORITMI ja
LOGARITMI se on seitsemän merkkiä pitkä.

Olkoon `p[i][j]` alkuosien `a[0..i)` ja `b[0..j)` LCS:n pituus. Jos
viimeiset merkit ovat samat, ne kuuluvat johonkin pisimpään yhteiseen
osajonoon, ja `p[i][j] = p[i-1][j-1] + 1`. Muuten ainakin toinen
viimeisistä merkeistä ei ole mukana, ja vastaus on parempi kahdesta
vaihtoehdosta, joissa toinen merkki pudotetaan:

```{.c tiedosto="esimerkit/10-lcs.c" osa="lcs"}
```

Rekonstruktio alkaa taulukon oikeasta alakulmasta. Kun merkit ovat
samat, merkki kirjoitetaan tulokseen lopusta alkaen ja siirrytään
vinosti. Muuten siirrytään siihen naapuriin, josta arvo tuli.

```{.tuloste tiedosto="esimerkit/10-lcs.odotettu"}
```

Pisimpiä yhteisiä osajonoja voi olla useita: ALGORITMI ja LOGARITMI
jakavat myös jonon LORITMI. Rekonstruktio valitsee yhden, ja valinta
riippuu siitä, kumpi naapuri suositaan tasapelissä. Siksi testi ei
vertaa jonoa vaan tarkistaa sen ominaisuudet: pituus on sama kuin
raa'alla haulla, joka käy läpi $a$:n kaikki $2^n$ osajonoa, ja jono on
todella molempien osajono. Neljän merkin aakkosto tekee yhteisistä
merkeistä yleisiä, ja pituudet 0–12 tuovat mukaan tyhjät merkkijonot.

Aika ja muisti ovat $\Theta(nm)$. Jos tarvitaan vain pituus, kaksi
riviä riittää. Hirschbergin algoritmi rekonstruoi myös itse jonon
lineaarisella muistilla yhdistämällä dynaamisen ohjelmoinnin ja hajota
ja hallitse -menetelmän.

## Editointietäisyys

*Editointietäisyys* eli Levenshteinin etäisyys on pienin määrä yhden
merkin lisäyksiä, poistoja ja korvauksia, joilla $a$ muuttuu $b$:ksi.
Osatehtävä on sama kuin LCS:ssä, ja viimeiselle merkille on kolme
vaihtoehtoa: $a$:n viimeinen merkki poistetaan, $b$:n viimeinen
lisätään tai ne kohdistetaan toisiinsa, jolloin hinta on 0 samoille
merkeille ja 1 korvaukselle.

```{.c tiedosto="esimerkit/10-editointi.c" osa="etaisyys"}
```

Perustapaukset kertovat tyhjän merkkijonon etäisyyden: $i$ merkkiä
on poistettava tai $j$ lisättävä. Varsinainen muutos näkyy, kun
taulukko kuljetaan takaperin ja kullakin askeleella valitaan
vaihtoehto, joka selittää taulukon arvon:

```{.c tiedosto="esimerkit/10-editointi.c" osa="kohdistus"}
```

```{.tuloste tiedosto="esimerkit/10-editointi.odotettu"}
```

Kohdistuksen rivit ovat lähtö- ja kohdesana sekä operaatiot: `=`
pitää merkin, `~` korvaa, `x` poistaa ja `+` lisää. Viiva tarkoittaa
puuttuvaa merkkiä. Lauantai muuttuu sunnuntaiksi lisäämällä alkuun
s:n ja korvaamalla neljä merkkiä; loppuosa "ntai" on yhteinen.
Testi vertaa taulukon arvoa suoraan rekursiivisen määritelmän arvoon,
joka käy kaikki kohdistukset läpi eksponentiaalisessa ajassa ja on
siksi rajattu seitsemän merkin sanoihin.

Editointietäisyys on oikoluvun ja sumean haun perusta: sana, jonka
etäisyys kirjoitettuun on pienin, on todennäköisin tarkoitettu.
Painotetussa versiossa operaatioilla on eri hinnat, esimerkiksi
näppäimistöllä vierekkäisten kirjainten korvaus on halvempi.
Bioinformatiikassa sama algoritmi tunnetaan Needlemanin–Wunschin
kohdistuksena. Kun tarvitaan vain tieto siitä, onko etäisyys
enintään $k$, riittää laskea taulukosta $2k + 1$ alkion levyinen
kaista lävistäjän ympäriltä, ja aika on $O(k \cdot n)$.

## Diff-työkalun ydin

`diff` ja versionhallinnan erotusnäkymä vertaavat tiedostoja riveittäin.
Kun rivit ovat merkkejä, LCS kertoo, mitkä rivit pysyivät ennallaan.
Muut vanhan version rivit on poistettu ja muut uuden version rivit
lisätty. Jotta muutokset voidaan tulostaa tiedoston alusta loppuun,
taulukko lasketaan *loppuosille*: `p[i][j]` on loppuosien `a[i..n)` ja
`b[j..m)` LCS:n pituus. Silloin rekonstruktio kulkee eteenpäin.

```{.c tiedosto="esimerkit/10-diff.c" osa="diff"}
```

```{.tuloste tiedosto="esimerkit/10-diff.odotettu"}
```

Esimerkissä palvelimen asetustiedostoon on vaihdettu portti, lisätty
TLS ja aikakatkaisu ja kasvatettu yhteyksien määrää. Muutettu rivi
näkyy poistona ja lisäyksenä, kuten `diff -u`:n tulosteessa.
Tasapelissä poisto tulostetaan ennen lisäystä, mikä on tavallinen
käytäntö.

Rivien vertailu `strcmp`:llä on yksinkertaistus. Todellinen diff
hajauttaa jokaisen rivin kerran kokonaisluvuksi ja vertaa lukuja.
Lisäksi $\Theta(nm)$-taulukko on liian suuri kymmenien tuhansien rivien
tiedostoille. Gitin oletusalgoritmi on Myersin algoritmi, joka etsii
lyhimmän muutosjonon ajassa $O((n + m) D)$, missä $D$ on muutosten
määrä. Samankaltaisille tiedostoille $D$ on pieni, ja algoritmi on
lähes lineaarinen. Patience diff ja histogram diff tuottavat
ihmiselle luettavampia eroja kohdistamalla ensin rivit, jotka
esiintyvät molemmissa tiedostoissa vain kerran.

## Käytännössä

- **Kaksi alkuosaa on merkkijonojen osatehtävä.** LCS, editointietäisyys
  ja kohdistus ovat saman taulukon muunnelmia; vain rekursion
  vaihtoehdot ja hinnat vaihtelevat.
- **Testaa ominaisuudet, älä yhtä vastausta.** Optimiratkaisuja on
  usein monta, joten tarkista, että ratkaisu on sallittu ja optimaalinen.
- **Valitse täyttösuunta tulostuksen mukaan.** Loppuosien taulukosta
  ratkaisun voi tulostaa eteenpäin ilman kääntämistä.
- **Rajoita muistia.** Kaksi riviä riittää arvoon; kaista riittää, kun
  etäisyys on pieni; Hirschberg rekonstruoi lineaarisella muistilla.
- **Suurille tiedostoille Myers.** $\Theta(nm)$ ei skaalaudu, mutta
  muutosten määrästä riippuva algoritmi skaalautuu.

## Itsearviointi

- Osaat kirjoittaa LCS:n rekursion ja rekonstruoida yhteisen osajonon
  taulukosta.
- Osaat laskea editointietäisyyden ja tulostaa operaatiot, jotka
  muuttavat sanan toiseksi.
- Osaat rakentaa rivipohjaisen diffin LCS:n avulla ja selittää, miksi
  taulukko lasketaan loppuosille.
- Osaat testata merkkijonoalgoritmin, jolla on monta yhtä hyvää
  vastausta.
