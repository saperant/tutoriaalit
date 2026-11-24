# Predikaatit ja SAT

Propositiologiikka käsittelee kokonaisia väitteitä. Ohjelman
vaatimukset puhuvat kuitenkin olioista: ”jokaisella tilauksella on
asiakas”, ”jokin rivi ylittää rajan”. Predikaattilogiikka lisää
muuttujat, jotka viittaavat olioihin, ja kvanttorit, jotka sanovat
”kaikilla” ja ”jollakin”. Luvun toinen puoli kääntää näkökulman
toisin päin: annetaan kaava ja kysytään, voiko sen tehdä todeksi.
Tämä SAT-ongelma on laskennan vaikeuden kulmakivi ja samalla
yllättävän käyttökelpoinen työkalu.

## Predikaatit ja kvanttorit

**Predikaatti** $P(x)$ on väite, jonka totuusarvo riippuu muuttujasta
$x$: ”$x$:llä on vähintään yksi rivi”. Kun $x$ kiinnitetään, predikaatista
tulee propositio. **Kvanttorit** sitovat muuttujan
**perusjoukkoon** (*domain*):

- $\forall x\, P(x)$, ”kaikilla $x$ pätee $P(x)$”, vastaa Pythonin
  lauseketta `all(P(x) for x in joukko)`.
- $\exists x\, P(x)$, ”jollakin $x$ pätee $P(x)$”, vastaa lauseketta
  `any(P(x) for x in joukko)`.

```{.python tiedosto="esimerkit/03-kvanttorit.py" osa="kvanttorit"}
```

Kvanttorin negaatio vaihtaa kvanttorin ja vie negaation sisään:

$$\neg \forall x\, P(x) \equiv \exists x\, \neg P(x), \qquad
\neg \exists x\, P(x) \equiv \forall x\, \neg P(x).$$

Sääntö on De Morganin laki äärettömälle määrälle konjunktioita ja
disjunktioita. Käytännössä se kertoo, mitä virheilmoitukseen
kannattaa kirjoittaa: kun väite ”kaikilla tilauksilla on rivejä”
kaatuu, rikkova tapaus eli **vastaesimerkki** on tilaus ilman rivejä.

## Tyhjä perusjoukko

Kvanttorien käyttäytyminen tyhjällä joukolla yllättää: $\forall$ on
aina tosi ja $\exists$ aina epätosi. Väite ”kaikki tyhjän listan
tilaukset on maksettu” on tosi, koska vastaesimerkkiä ei ole.

```{.python tiedosto="esimerkit/03-kvanttorit.py" osa="tyhja"}
```

Tämä on matemaattisesti johdonmukaista mutta ohjelmassa usein bugi:
tarkistus ”kaikki maksettu, joten lähetä” lähettää tyhjän tilauksen.
Jos tyhjä kokoelma on virhe, se tarkistetaan erikseen.

## Sisäkkäiset kvanttorit

Kvanttorien järjestys muuttaa merkityksen. ”Jokaisella asiakkaalla on
jokin tilaus” ($\forall a\, \exists t$) on eri asia kuin ”on tilaus,
joka kuuluu jokaiselle asiakkaalle” ($\exists t\, \forall a$).
Ohjelmassa sisäkkäiset kvanttorit ovat sisäkkäisiä generaattoreita:

```{.python tiedosto="esimerkit/03-kvanttorit.py" osa="sisakkaiset"}
```

```{.tuloste tiedosto="esimerkit/03-kvanttorit.odotettu"}
```

Vaatimusmäärittelyt ja tietokantojen eheysehdot ovat
predikaattilogiikkaa. SQL:n `NOT EXISTS` on $\neg\exists$, ja
”jokaisella tilauksella on olemassa asiakas” on viite-eheysrajoite
(taito *SQL ja relaatiotietokannat*).

## SAT-ongelma

**Toteutuvuusongelma** (SAT) kysyy: onko propositiokaavalle sellaisia
muuttujien arvoja, että kaava on tosi? Totuustaulu ratkaisee sen,
mutta $2^n$ riviä kasvaa nopeasti mahdottomaksi: 100 muuttujaa antaa
enemmän rivejä kuin maailmankaikkeudessa on atomeja. SAT on ensimmäinen
NP-täydelliseksi todistettu ongelma (Cook 1971): mikä tahansa
ongelma, jonka ratkaisun voi tarkistaa nopeasti, voidaan muuntaa
SAT:ksi. Tehokasta yleistä algoritmia ei tunneta, eikä sitä luultavasti
ole.

Silti nykyiset SAT-ratkaisijat ratkaisevat käytännössä kaavoja, joissa
on miljoonia muuttujia. Niitä käytetään laitteiston verifioinnissa,
pakettienhallinnan riippuvuuksien ratkaisemisessa (esim. openSUSEn
zypper ja sen libsolv-kirjasto) ja aikataulutuksessa. Perusta on
**DPLL-algoritmi** (Davis–Putnam–Logemann–Loveland, 1962):

1. **Yksikköpropagointi**: jos lausekkeessa on vain yksi literaali,
   sen on oltava tosi. Arvo sijoitetaan, ja kaava sievenee.
2. **Haarautuminen**: valitaan muuttuja ja kokeillaan ensin arvoa tosi
   ja sitten epätosi. Jos molemmat johtavat ristiriitaan, palataan.

Kaava esitetään CNF:ssä lausekelistana. Literaali on kokonaisluku:
$3$ tarkoittaa muuttujaa $x_3$ ja $-3$ sen negaatiota, kuten SAT-
ratkaisijoiden DIMACS-tiedostomuodossa.

```{.python tiedosto="esimerkit/03-dpll.py" osa="dpll"}
```

## Ongelman koodaaminen SAT:ksi

SAT-ratkaisijan arvo on siinä, että moni ongelma koodautuu sille
luontevasti. Tenttiaikataulussa tentit, joilla on yhteisiä
opiskelijoita, eivät saa olla samassa aikavälissä. Tämä on graafin
väritys (luku *Graafit*). Jokaista paria (tentti, aikaväli) vastaa
muuttuja, ja ehdot ovat lausekkeita: jokaisella tentillä on vähintään
yksi ja enintään yksi aikaväli, eikä kahdella ristiriitaisella tentillä
ole samaa aikaväliä.

```{.python tiedosto="esimerkit/03-dpll.py" osa="varitys"}
```

```{.tuloste tiedosto="esimerkit/03-dpll.odotettu"}
```

Kaksi aikaväliä ei riitä, koska matikka, fysiikka ja ohjelmointi ovat
pareittain ristiriidassa (kolmio), ja ratkaisija toteaa sen muutamalla
kutsulla. Kolmella aikavälillä ratkaisu löytyy. Oikeissa
ratkaisijoissa (MiniSat, CaDiCaL, Kissat) on lisäksi opittavat
lausekkeet (*conflict-driven clause learning*), älykäs muuttujan valinta
ja uudelleenaloitukset, mutta perusrakenne on sama.

## Käytännössä

- **Kirjoita vaatimus kvanttoreilla ennen koodia.** ”Jokaisella
  tilauksella on vähintään yksi rivi” on suoraan `all(...)`.
  Kvanttorien järjestys paljastaa epäselvyydet ennen kuin ne päätyvät
  koodiin.
- **Raportoi vastaesimerkki.** Kun $\forall$-tarkistus kaatuu, kerro
  mikä alkio rikkoi sen. `all()` palauttaa vain totuusarvon; listan
  `[x for x in ... if not P(x)]` saa virheilmoitukseen.
- **Päätä, onko tyhjä kokoelma sallittu.** `all([])` on tosi.
  Validoinnissa tyhjä syöte vaatii usein oman tarkistuksen.
- **Tunnista SAT-muotoiset ongelmat.** Riippuvuuksien ratkaisu,
  aikataulut ja konfiguraatioiden yhteensopivuus ovat kombinatorisia
  rajoiteongelmia. Valmis ratkaisija (SAT, SMT kuten Z3, tai
  rajoiteohjelmointi kuten OR-Tools) on lähes aina parempi kuin itse
  kirjoitettu haku.
- **Odota eksponentiaalista pahinta tapausta.** SAT-ratkaisijat ovat
  käytännössä nopeita, mutta mikään ei takaa sitä. Aseta aikaraja.

## Itsearviointi

- Osaat kirjoittaa vaatimuksen kvanttoreilla ja kääntää sen
  Pythonin `all`- ja `any`-lausekkeiksi.
- Osaat negoida kvanttoreita sisältävän väitteen ja muodostaa siitä
  vastaesimerkin etsivän koodin.
- Osaat selittää, miksi $\forall$ on tyhjällä joukolla tosi ja milloin
  se on ohjelmassa bugi.
- Osaat kuvata SAT-ongelman, DPLL-algoritmin periaatteen ja koodata
  pienen ongelman CNF-muotoon.
