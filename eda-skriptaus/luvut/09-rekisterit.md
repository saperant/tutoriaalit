# Rekisterikuvauksista generoitu koodi

Ohjelmisto ohjaa laitteistoa rekisterien kautta. Sama rekisterikartta
on kirjoitettava moneen paikkaan: RTL:n rekisterilohkoon, ajurin
C-otsakkeeseen, dokumentaatioon ja testeihin. Käsin kirjoitettuna
kopiot alkavat erota toisistaan heti ensimmäisessä muutoksessa.
Bittikenttä siirtyy RTL:ssä mutta ei otsakkeessa, ja ajuri kirjoittaa
väärään bittiin. Tällaisen virheen löytää vasta laboratoriossa.

Ratkaisu on yksi kuvaus, josta kaikki muu tuotetaan. Teollisuudessa
käytetään standardimuotoja, kuten SystemRDL:ää (Accellera) ja
IP-XACT:ia (IEEE 1685), ja niille on avoimia ja kaupallisia
generaattoreita. Periaate on sama kuin tässä luvussa, jossa kuvaus on
pieni TOML-tiedosto ja generaattori satakunta riviä Pythonia.
Taidossa *SoC-integraatio* samalla kuvausmuodolla tuotetut
rekisterilohkot kytketään väylään ja rekisterityypit käydään läpi
laitteiston kannalta. Taito *Laitteiston kuvausstandardit (SystemRDL,
IP-XACT)* tekee saman standardimuodoilla ja valmiilla
generaattoreilla. Tässä keskitytään siihen, miten generaattori
rakennetaan ja miten tuotettu koodi pidetään kuvauksen kanssa samassa
tahdissa.

```{.dot otsikko="Yksi kuvaus, neljä tuotetta. CI tuottaa tiedostot uudelleen ja vertaa niitä tallennettuihin (katkoviiva)."}
digraph {
  rankdir=LR;
  node [shape=box, fontsize=10];
  kuvaus [label="rekisterit.toml", shape=ellipse];
  malli [label="malli ja\ntarkistus"];
  sv [label="ajastin_regs.sv\n(RTL)", shape=ellipse];
  h [label="ajastin_regs.h\n(C-otsake)", shape=ellipse];
  md [label="ajastin_regs.md\n(dokumentti)", shape=ellipse];
  tb [label="ajastin_regs_tb.sv\n(testipenkki)", shape=ellipse];
  ci [label="CI: tuota ja vertaa"];
  kuvaus -> malli;
  malli -> sv; malli -> h; malli -> md; malli -> tb;
  sv -> ci [style=dashed]; h -> ci [style=dashed];
  md -> ci [style=dashed]; tb -> ci [style=dashed];
}
```

## Kuvaus

```{.toml tiedosto="esimerkit/asetukset/rekisterit.toml" osa="ctrl"}
```

Samaan tapaan kuvataan tilarekisteri `STATUS`, laskurin arvo `LASKURI`
ja vertailuarvo `VERTAA`.

Jokaisella kentällä on bitit (ylin ja alin), pääsy ja nollausarvo.
Pääsytapoja on kolme. `rw` on ohjelmiston kirjoitettava ja luettava
kenttä, jonka arvo menee laitteistolle. `ro` on laitteiston arvo, jonka
ohjelmisto voi vain lukea. `w1c` (*write one to clear*) on lippu,
jonka laitteisto asettaa ja ohjelmisto nollaa kirjoittamalla siihen
ykkösen. Muiden bittien kirjoittaminen nollaksi ei silloin vahingossa
nollaa lippua.

![Rekisterien CTRL ja STATUS bittikentät piirrettynä samasta
kuvauksesta (`kuvat/piirra.py`). Harmaat bitit ovat varattuja: ne
luetaan nollina, eikä niihin kirjoittaminen vaikuta
mihinkään.](kuvat/bittikentat.png){width=92%}

## Malli ja tarkistus

Kuvaus luetaan tietueiksi `Lohko`, `Rekisteri` ja `Kentta`. Kentän
tietueessa on ominaisuudet `leveys` ja `maski`, joita generaattorit ja
tarkistin käyttävät. Ennen kuin mitään tuotetaan, kuvaus tarkistetaan. Tarkistin kerää
kaikki virheet kerralla, jotta kuvauksen kirjoittaja voi korjata ne
yhdellä kierroksella.

Rekisteritasolla tarkistetaan nimet, osoitteiden tasaus ja
päällekkäiset osoitteet. Kentät tarkistetaan rekisteri kerrallaan:

```{.python tiedosto="esimerkit/vuo/rekisterit.py" osa="kentat"}
```

Bittikenttien päällekkäisyys tarkistetaan maskeilla: `varattu`
kerää rekisterin jo käytetyt bitit, ja jos uuden kentän maski osuu
niihin, kentät ovat päällekkäin. Tarkoituksella virheellisestä
kuvauksesta (`asetukset/rekisterit_rikki.toml`) tarkistin löytää
kahdeksan virhettä. Ne näkyvät esimerkin tulosteen alussa luvun
lopussa.

## Generaattorit

Jokainen tuote on funktio, joka saa lohkon ja palauttaa tekstin.
C-otsakkeeseen (`c_otsake`) tulee jokaiselle rekisterille siirtymä ja
jokaiselle kentälle siirto ja maski:


```{.c tiedosto="esimerkit/tuotettu/ajastin_regs.h"}
```

RTL-generaattori `sv_lohko` tuottaa rekisterilohkon, jossa on
kirjoituslogiikka nollauksineen ja lukumultipleksori. Generaattori on
pidempi, mutta rakenne on sama: kuvauksen jokaisesta kentästä tulee
portti ja rivi kirjoitus- ja lukulogiikkaan. Tuotos:

```{.systemverilog tiedosto="esimerkit/tuotettu/ajastin_regs.sv"}
```

Tuotettu koodi on luettavaa ja sisennettyä. Sitä luetaan
virheenetsinnässä ja katselmoinnissa, ja simulaattorin virheilmoitus
viittaa sen riveille. Tiedoston alun kommentti kertoo, mistä se on
tuotettu ja ettei sitä muokata käsin. Datatulon käyttämättömät bitit
on hyväksytty lint-kommentilla, koska ne ovat rakenteellisesti aina
käyttämättä (luku 6).

Dokumentaatio (`dokumentti`) tuotetaan Markdownina samasta mallista,
yksi taulukko rekisteriä kohden. Dokumentin bittikentät ovat siksi
aina samat kuin RTL:n ja otsakkeen.

## Tuotetut testit

Neljäs tuote on testipenkki, joka tarkistaa rekisterilohkon väylän
kautta: nollausarvot sekä väylältä että laitteiston puolelta, rw-
kenttien kirjoituksen ja luvun, ro-kenttien suojauksen kirjoitukselta
ja w1c-lippujen asetuksen ja nollauksen. Testipenkki syöttää
vain luku -kenttiin tunnetun bittikuvion (`0101...`), jotta lukupolun
virheellinen kytkentä näkyy. Generaattori `sv_testi` kirjoittaa
jokaisesta tarkistuksesta yhden rivin, esimerkiksi
`lue(8'h00, 32'h00000100, 32'h0000FF03, "CTRL nollausarvo");`, joka
lukee rekisterin osoitteesta 0, peittää kuvaamattomat bitit maskilla ja
vertaa nollausarvoon. Tuotettu testipenkki on tiedostossa
`tuotettu/ajastin_regs_tb.sv`.

Tuotettu testi tarkistaa, että RTL vastaa kuvausta ja että
generaattori toimii. Se ei tarkista, onko kuvaus oikein. Jos
kuvauksessa on väärä nollausarvo, sekä RTL että testi ovat yhtä mieltä
väärästä arvosta. Kuvauksen oikeellisuus tarkistetaan katselmoinnissa
ja järjestelmätason testeissä, joissa ajuri käyttää lohkoa.

Ajuri käyttää otsakkeen nimiä eikä omia vakioitaan:

```{.c tiedosto="esimerkit/c/ajuri.c" osa="kentta"}
```

## Tahdissa pysyminen

Tuotetut tiedostot voi joko tuottaa joka käännöksessä tai tallentaa
versionhallintaan. Tallentamisen etu on, että tuotettu koodi näkyy
katselmoinnissa, ja muutos kuvaukseen näyttää diffissä, mitä RTL:ssä ja
otsakkeessa muuttui. Haittana on, että tallennettu tiedosto voi jäädä
jälkeen kuvauksesta tai joku voi muokata sitä käsin. Siksi CI
tarkistaa, että tallennetut tiedostot ovat täsmälleen ne, jotka
kuvauksesta nyt tuotettaisiin:

```{.python tiedosto="esimerkit/vuo/rekisterit.py" osa="tuota"}
```

`tuota` ei kirjoita mitään. Kutsuja päättää, kirjoitetaanko
(`--kirjoita`) vai verrataanko:

```{.python tiedosto="esimerkit/09-rekisterit.py" osa="tahdissa"}
```

Esimerkki ajaa tuotetut testit kahdesti: ensin tallennetuille
tiedostoille ja sitten kopiolle, jossa joku on muuttanut nollausarvoa
käsin:

```{.python tiedosto="esimerkit/09-rekisterit.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/09-rekisterit.odotettu"}
```

Käsin tehty muutos jää kiinni kahdesti. Vertailu kertoo, että tiedosto
poikkeaa kuvauksesta, ja tuotettu testi löytää väärän nollausarvon
sekä laitteiston lähdöstä että väylältä luettuna. Lopuksi ajuri
käännetään tuotetulla otsakkeella varoitukset virheinä, ja se laskee
rekisteriarvot otsakkeen maskeilla.

## Käytännössä

- **Yksi kuvaus, kaikki muu tuotetaan.** RTL, otsake, dokumentaatio ja
  testit. Myös laitteiston ja ohjelmiston rajapintadokumentti tuotetaan,
  ei kirjoiteta.
- **Tarkista kuvaus ennen tuottamista.** Kaikki virheet kerralla,
  selkeät viestit ja kentän nimi viestissä.
- **Tuotettu koodi on luettavaa.** Sisennys, kommentit ja
  alkuperätieto, koska sitä luetaan virheenetsinnässä.
- **CI tarkistaa tahdin.** Tallennettu tuotettu koodi verrataan
  tuoreeseen tuotokseen, ja ero kaataa putken.
- **Generaattorilla on omat testinsä.** Tarkistimen virheet ja
  tuotetun koodin kääntyminen testataan, ja tuotettu testipenkki
  ajetaan joka kerta.

## Itsearviointi

- Osaat kuvata rekisterikartan koneluettavana tiedostona ja tarkistaa
  sen päällekkäisyyksien, leveyksien ja osoitteiden osalta.
- Osaat tuottaa kuvauksesta RTL:n, C-otsakkeen, dokumentaation ja
  testipenkin.
- Osaat selittää, mitä tuotettu testi tarkistaa ja mitä se ei voi
  tarkistaa.
- Osaat rakentaa CI-tarkistuksen, joka huomaa vanhentuneen tai käsin
  muokatun tuotetun tiedoston.
