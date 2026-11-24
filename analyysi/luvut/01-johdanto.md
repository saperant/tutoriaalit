# Johdanto {.runko-johdanto}

Differentiaali- ja integraalilaskenta tutkii muutosta. **Derivaatta**
kertoo, kuinka nopeasti jokin suure muuttuu: nopeus on paikan
derivaatta, virta varauksen derivaatta ja rajakustannus kustannuksen
derivaatta. **Integraali** on derivaatan vastakohta, joka kokoaa
pienistä muutoksista kokonaisuuden: nopeudesta kuljettu matka, tehosta
kulutettu energia ja tiheysfunktiosta todennäköisyys. Molemmat rakentuvat
**raja-arvon** varaan: mitä tapahtuu, kun jokin suure lähestyy rajattomasti
jotakin arvoa.

Tämä tutoriaali käy läpi insinöörimatematiikan analyysin ytimen yhden ja
usean muuttujan funktioille. Jokainen asia tehdään kolmella tavalla:

1. **Ajatuksen tasolla ja käsin**, koska työkalu on vain niin hyvä kuin
   käyttäjän käsitys siitä, mitä lasketaan.
2. **Symbolisesti** SymPyllä ja Maximalla, jotka antavat tarkan
   tuloksen ja tarkistavat käsinlaskun.
3. **Numeerisesti** NumPylla ja SciPyllä, koska käytännön data on
   mittauspisteitä eikä kaavoja, ja koska numeerisella laskulla on omat
   sudenkuoppansa.

Työkalujen perusteet (symbolit, tarkat luvut, sievennys, Maximan eräajo
ja kuvaajien piirtäminen) esitellään taidon *Matematiikan perusteet
ohjelmallisesti* luvussa 2. Tässä tutoriaalissa niitä käytetään
suoraan.

## Ensimmäinen esimerkki: paikka, nopeus ja matka

Kappale liikkuu suoraviivaisesti niin, että sen paikka hetkellä $t$
sekunteina on $s(t) = 5t^2 - \tfrac13 t^3$ metriä. Nopeus on paikan
muutosnopeus eli derivaatta $v(t) = s'(t)$, ja kiihtyvyys on nopeuden
derivaatta $a(t) = v'(t)$. SymPyn `diff` derivoi lausekkeen. Suurin
nopeus saavutetaan, kun kiihtyvyys on nolla.

```{.python tiedosto="esimerkit/01-nopeus.py" osa="symbolinen"}
```

Mittauksissa kaavaa ei yleensä ole, vaan paikka tunnetaan näytteinä.
Silloin derivaatta arvioidaan **erotusosamäärillä**: paikan muutos
jaettuna ajan muutoksella. NumPyn `gradient` laskee ne koko taulukolle
kerralla.

```{.python tiedosto="esimerkit/01-nopeus.py" osa="numeerinen"}
```

Integraali kulkee toiseen suuntaan: nopeuden integraali välin yli on
kappaleen kulkema matka. Se on sama kuin paikan muutos välin
päätepisteiden välillä, mikä on analyysin peruslauseen (luku 5) sisältö.

```{.python tiedosto="esimerkit/01-nopeus.py" osa="integraali"}
```

```{.tuloste tiedosto="esimerkit/01-nopeus.odotettu"}
```

Numeerinen derivaatta poikkeaa tarkasta arvosta neljännessä
merkitsevässä numerossa. Ero ei ole ohjelmointivirhe vaan menetelmän
ominaisuus, ja luvussa 3 lasketaan, mistä se syntyy ja miten se
pienennetään.

## Kenelle ja mitä tarvitaan

Tutoriaali on tarkoitettu insinööri- ja tietotekniikan opiskelijalle
sekä ohjelmoijalle, joka tarvitsee analyysia signaalinkäsittelyssä,
grafiikassa, optimoinnissa tai fysiikan mallinnuksessa. Lukion pitkän
matematiikan funktiot, yhtälöt, eksponentti- ja logaritmifunktiot,
trigonometria sekä jonot ja summat oletetaan tutuiksi (taito
*Matematiikan perusteet ohjelmallisesti*). Usean muuttujan luvuissa
käytetään vektoreita ja matriiseja (taito *Lineaarialgebra*).

Esimerkit tarvitsevat Python 3.12:n, SymPyn, NumPyn, SciPyn ja
Matplotlibin sekä Maximan. Paketin kehityskontissa kaikki on valmiina.
Jokainen esimerkki on testattu ohjelma, ja kirjassa näkyvät tulosteet
ovat ohjelmien todellisia tulosteita.

## Tutoriaalin rakenne

| Luku | Aihe | Työkalut |
|------|------|----------|
| 2 | Raja-arvo ja jatkuvuus | `limit`, liukulukujen sudenkuopat |
| 3 | Derivaatta | `diff`, `idiff`, erotusosamäärät |
| 4 | Derivaatan sovelluksia | optimointi, Newton, `brentq` |
| 5 | Integraali | `integrate`, `apart`, epäoleelliset integraalit |
| 6 | Integraalin sovelluksia | puolisuunnikas, Simpson, `quad` |
| 7 | Sarjat ja Taylorin polynomit | `series`, `summation`, jäännöstermi |
| 8 | Usean muuttujan derivaatat | gradientti, `hessian`, `minimize` |
| 9 | Moninkertaiset integraalit | napakoordinaatit, `dblquad`, Monte Carlo |

Jokaisen luvun lopussa samat laskut tehdään myös Maximalla. Kaksi
toisistaan riippumatonta ohjelmaa, jotka päätyvät samaan tulokseen, ovat
vahvempi todiste kuin yksi.
