# Predikaatit ja SAT

Propositiologiikka käsittelee kokonaisia väitteitä. Ohjelman
vaatimukset puhuvat kuitenkin olioista: ”jokaisella tilauksella on
asiakas”, ”jokin rivi ylittää rajan”. Predikaattilogiikka lisää
muuttujat, jotka viittaavat olioihin, ja kvanttorit, jotka sanovat
”kaikilla” ja ”jollakin”. Luvun toinen puoli kääntää näkökulman
toisin päin: sen sijaan, että tarkistettaisiin väite annetuilla
arvoilla, annetaan kaava ja kysytään, voiko sen tehdä todeksi.
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

```{.tuloste tiedosto="esimerkit/03-kvanttorit.odotettu" rivit="1-3"}
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

```{.tuloste tiedosto="esimerkit/03-kvanttorit.odotettu" rivit="4-5"}
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

```{.tuloste tiedosto="esimerkit/03-kvanttorit.odotettu" rivit="6-"}
```

Vaatimusmäärittelyt ja tietokantojen eheysehdot ovat
predikaattilogiikkaa. SQL:n `NOT EXISTS` on $\neg\exists$, ja
”jokaisella tilauksella on olemassa asiakas” on viite-eheysrajoite
(taito *SQL ja relaatiotietokannat*).

## SAT-ongelma

Äärellisessä perusjoukossa kvanttorit purkautuvat propositiologiikaksi:
$\forall x\, P(x)$ on konjunktio $P(x_1) \land \cdots \land P(x_n)$ ja
$\exists x\, P(x)$ disjunktio $P(x_1) \lor \cdots \lor P(x_n)$. Vaatimus
”jokaisella tentillä on jokin aikaväli” on siis pitkä propositiokaava,
jonka muuttujat ovat väitteitä ”tentti $t$ on aikavälissä $a$”. Tähän
asti kaavan arvo on laskettu annetuilla muuttujien arvoilla. Nyt
kysytään päinvastoin, millä arvoilla kaava toteutuu.

**Toteutuvuusongelma** (SAT) kysyy: onko propositiokaavalle sellaisia
muuttujien arvoja, että kaava on tosi? Totuustaulu ratkaisee sen,
mutta $2^n$ riviä kasvaa nopeasti mahdottomaksi. Jo 100 muuttujaa
antaa $2^{100} \approx 1{,}3 \cdot 10^{30}$ riviä: miljardi riviä
sekunnissa tarkistava kone käyttäisi niihin noin $4 \cdot 10^{13}$
vuotta, kolmisentuhatta kertaa maailmankaikkeuden iän. 300 muuttujalla
rivejä on enemmän kuin näkyvässä maailmankaikkeudessa atomeja (noin
$10^{80}$).

Ongelmien vaikeutta luokitellaan sen mukaan, miten ratkaisuun kuluva
aika kasvaa syötteen koon $n$ mukana. Luokkaan **P** kuuluvat
ongelmat, jotka voidaan *ratkaista* ajassa, joka on enintään jokin
$n$:n potenssi (polynominen aika). Luokkaan **NP** kuuluvat ongelmat,
joiden ehdotettu ratkaisu voidaan *tarkistaa* polynomisessa ajassa.
SAT kuuluu luokkaan NP: annetut muuttujien arvot tarkistetaan
laskemalla kaavan arvo kerran. Ongelma on **NP-vaikea**, jos jokainen
NP:n ongelma voidaan muuntaa siksi polynomisessa ajassa, ja
**NP-täydellinen**, jos se lisäksi itse kuuluu luokkaan NP. SAT on
ensimmäinen NP-täydelliseksi todistettu ongelma (Cook 1971).
NP-täydelliselle ongelmalle ei tunneta polynomista algoritmia, eikä
sellaista luultavasti ole; kysymys ”onko P = NP” on tietojenkäsittelyn
kuuluisin avoin ongelma. Luokat käsitellään tarkemmin taidossa
*Algoritmit*.

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
$3$ tarkoittaa muuttujaa $x_3$ ja $-3$ sen negaatiota, kuten
SAT-ratkaisijoiden DIMACS-tiedostomuodossa.

```{.python tiedosto="esimerkit/03-dpll.py" osa="dpll"}
```

## Ongelman koodaaminen SAT:ksi

SAT-ratkaisijan arvo on siinä, että moni ongelma koodautuu sille
luontevasti. Tenttiaikataulussa tentit, joilla on yhteisiä
opiskelijoita, eivät saa olla samassa aikavälissä. Tilanteen voi
piirtää verkoksi, jossa tentit ovat solmuja ja viiva yhdistää
ristiriitaiset tentit; tehtävä on antaa solmuille värit (aikavälit)
niin, että viivan päissä on eri värit. Tällaiseen graafin väritykseen
palataan luvussa *Graafit*. Jokaista paria (tentti, aikaväli) vastaa
muuttuja, ja ehdot ovat lausekkeita: jokaisella tentillä on vähintään
yksi ja enintään yksi aikaväli, eikä kahdella ristiriitaisella tentillä
ole samaa aikaväliä.

```{.python tiedosto="esimerkit/03-dpll.py" osa="varitys"}
```

```{.tuloste tiedosto="esimerkit/03-dpll.odotettu"}
```

```{.dot otsikko="Tenttien ristiriidat ja ratkaisijan löytämä aikataulu: numero ja sävy ovat aikaväli"}
graph {
  layout=neato; overlap=false;
  node [shape=box, style="rounded,filled"];
  matikka [label="matikka\n1", pos="0,1.2!", fillcolor="#FFFFFF"];
  fysiikka [label="fysiikka\n2", pos="1.7,2.0!", fillcolor="#DDE4E6"];
  ohjelmointi [label="ohjelmointi\n3", pos="1.7,0.4!", fillcolor="#9FB0B5"];
  kemia [label="kemia\n1", pos="3.6,2.0!", fillcolor="#FFFFFF"];
  tilastot [label="tilastot\n2", pos="3.6,0.4!", fillcolor="#DDE4E6"];
  matikka -- fysiikka; matikka -- ohjelmointi; fysiikka -- ohjelmointi;
  fysiikka -- kemia; ohjelmointi -- tilastot; kemia -- tilastot;
}
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
- Osaat selittää, mitä luokat P ja NP sekä sanat NP-vaikea ja
  NP-täydellinen tarkoittavat.
