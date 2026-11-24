# Johdanto {.runko-johdanto}

Insinööri ja ohjelmoija laskevat harvoin pelkällä kynällä. Jarrutusmatka
lasketaan taulukkolaskennassa, piirin aikavakio Pythonilla, ja
korkolaskelma tehdään pankin laskurilla. Silti jokainen laskin on vain
niin hyvä kuin sen käyttäjän käsitys siitä, mitä lasketaan. Tämä
tutoriaali kertaa lukion pitkän matematiikan keskeiset sisällöt ja opettaa
samalla työkalut, joilla laskut tehdään ja tarkistetaan tietokoneella:

- **SymPy** on Pythonin kirjasto *symboliseen laskentaan*. Se sieventää
  lausekkeita, ratkaisee yhtälöitä tarkasti ja käsittelee lukuja kuten
  $\sqrt{2}$ ja $\tfrac13$ tarkkoina, ei likiarvoina.
- **NumPy** laskee *numeerisesti*: tuhansia funktion arvoja kerralla
  liukulukuina.
- **Matplotlib** piirtää kuvaajat tiedostoon.
- **Maxima** on itsenäinen, vuodesta 1982 kehitetty symbolisen laskennan
  ohjelma (alkujaan Macsyma). Se on hyvä vertailukohta SymPylle: kaksi
  eri ohjelmaa, jotka päätyvät samaan tulokseen, ovat vahvempi todiste
  kuin yksi.
- **GNU Octave** on numeerisen laskennan ympäristö, jonka kieli on lähes
  sama kuin MATLABin. Sitä käytetään jatkotaidoissa
  *Differentiaaliyhtälöt ja Laplace-muunnos* ja *Numeeriset menetelmät*.

Kaikki työkalut ovat avointa lähdekoodia ja ilmaisia. Ne toimivat samoin
Linuxissa, macOS:ssä ja Windowsissa, ja tämän paketin kehityskontissa ne
ovat valmiina.

## Ensimmäinen esimerkki: käsinlaskun tarkistus

Tärkein yksittäinen taito tässä tutoriaalissa on tarkistaa oma lasku
koneella. Laajennetaan $(2x + 3)^2$ käsin ja annetaan SymPyn todeta, onko
tulos oikein. Lausekkeet ovat samat, jos niiden erotus sievenee nollaksi.

```{.python tiedosto="esimerkit/01-tarkistus.py" osa="laajennus"}
```

Kiireessä on helppo kirjoittaa $(2x - 3)^2 = 4x^2 - 9$ eli unohtaa
ristitermi. Erotus ei ole nolla, ja sijoitus $x = 1$ antaa konkreettisen
kohdan, jossa väite ei päde:

```{.python tiedosto="esimerkit/01-tarkistus.py" osa="virhe"}
```

Yhtälön ratkaisu tarkistetaan sijoittamalla se alkuperäiseen yhtälöön.
`sp.Eq` luo yhtälön, ja `subs` sijoittaa arvon. Jos tulos on `True`,
ratkaisu toteuttaa yhtälön.

```{.python tiedosto="esimerkit/01-tarkistus.py" osa="yhtalo"}
```

```{.tuloste tiedosto="esimerkit/01-tarkistus.odotettu"}
```

Huomaa, että tarkistus kertoo vain, onko *tämä* tulos oikein. Se ei kerro,
miksi virhe syntyi, eikä se korvaa ymmärrystä. Siksi jokaisessa luvussa
lasketaan ensin ajatuksen tasolla ja vasta sitten koneella.

## Kenelle ja mitä tarvitaan

Tutoriaali on tarkoitettu insinööriopintoja aloittavalle, lukion
matematiikkaa kertaavalle ja ohjelmoijalle, joka tarvitsee matematiikkaa
työssään. Lukija osaa Pythonin perusteet: muuttujat, funktiot,
silmukat, listat ja sanakirjat (taito *Ohjelmoinnin perusteet
(Python)*). Muuta ohjelmointia ei oleteta. NumPyn ja Matplotlibin
käyttö opetetaan sen verran kuin tässä tarvitaan; laajemmin niitä käsittelee taito *Python
työkaluohjelmointiin*.

Diskreetin matematiikan aiheet, kuten logiikka, joukko-oppi ja
induktiotodistuksen periaate, ovat taidossa *Diskreetti matematiikka*.
Tässä tutoriaalissa induktiota käytetään lukujonojen yhteydessä, mutta
todistamisen perusteet opetetaan siellä. Vektorit ja matriisit
yleisessä muodossa kuuluvat taitoon *Lineaarialgebra*; tässä käsitellään
vain tason vektorit ja analyyttinen geometria.

## Rakenne

| Luku | Sisältö | Sovellus |
|------|---------|----------|
| 2 | SymPy, Maxima, NumPy ja Matplotlib | Työkalujen yhteinen käsikirja |
| 3 | Lausekkeet, yhtälöt ja epäyhtälöt | Pysähtymismatka |
| 4 | Funktiot ja kuvaajat | Porrastettu hinnoittelu, puolitushaku |
| 5 | Eksponentti- ja logaritmifunktiot | Kasvu, aikavakio, desibelit |
| 6 | Trigonometria | Vaihtojännite ja vaihe |
| 7 | Vektorit ja analyyttinen geometria | Törmäyksen tunnistus pelissä |
| 8 | Lukujonot, summat ja induktio | Laina ja algoritmin työmäärä |
| 9 | Lopuksi | Työkaluvertailu ja lähteet |

Luku 2 on kirjoitettu käsikirjaksi, johon muut tutoriaalit voivat
viitata: siellä on SymPyn ja Maximan peruskomennot, tarkkojen lukujen ja
liukulukujen ero sekä kuvaajan piirtäminen tiedostoon. Lukujen 3–8 aiheet
etenevät lukion kurssijärjestyksessä, ja jokainen päättyy pieneen
sovellukseen insinöörin tai ohjelmoijan työstä.

## Esimerkit ja niiden testaus

Jokainen tekstissä näkyvä koodinpätkä on otettu tiedostosta, joka ajetaan
paketin testeissä, ja jokainen tuloste on ohjelman todellinen tuloste.
Python-esimerkit tarkistetaan lisäksi työkaluilla `ruff` ja
`mypy --strict`. SymPyssä ei ole tyyppitietoja, joten paketin
`pyproject.toml` kertoo mypylle, että SymPyn oliot ovat tyypiltään
`Any`; muu koodi tarkistetaan tiukasti.

Maxima-skriptit ovat hakemistossa `esimerkit/maxima/`, ja
`esimerkit/Makefile` ajaa ne eräajona ja vertaa tulosteen odotettuun.
Kuvat piirtää skripti `kuvat/piirra.py` (`make kuvat`), ja niiden luvut
lasketaan samoin kuin testatuissa esimerkeissä.

```text
make testaa   # ruff, mypy --strict, esimerkkien ajot ja Maxima-skriptit
make pdf      # tämä dokumentti ja pikaopas
make kuvat    # piirtää kuvat uudelleen
```
