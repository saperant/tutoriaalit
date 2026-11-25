# Hypoteesitestaus ja A/B-testit

Onko uusi versio parempi, vai onko ero sattumaa? *Hypoteesitestaus*
vastaa kysymykseen olettamalla ensin, ettei eroa ole (*nollahypoteesi*),
ja laskemalla, kuinka todennäköinen vähintään havaitun suuruinen ero
silloin olisi. Tämä todennäköisyys on *p-arvo*. Pieni p-arvo tarkoittaa,
että havainto sopii huonosti nollahypoteesiin.

## Kahden osuuden testi

Verkkokaupan versiolla A konvertoi 200 käyttäjää 2000:sta ja versiolla
B 240 käyttäjää 2000:sta.

```{.python tiedosto="esimerkit/13-ab-testi.py" osa="data"}
```

Jos versiot ovat yhtä hyviä, molempien osuus on yhdistetty $\hat p$, ja
osuuksien erotuksen keskivirhe on
$\sqrt{\hat p(1-\hat p)(1/n_A + 1/n_B)}$. Erotus jaettuna
keskivirheellä on likimain normaalijakautunut testisuure $z$:

```{.python tiedosto="esimerkit/13-ab-testi.py" osa="z"}
```

```{.tuloste tiedosto="esimerkit/13-ab-testi.odotettu" rivit="1-1"}
```

## Permutaatiotesti

Permutaatiotesti ei tarvitse jakaumaoletusta. Jos versioilla ei ole
eroa, käyttäjien ryhmänimet ovat merkityksettömiä, ja ne voi sekoittaa.
P-arvo on niiden sekoitusten osuus, joissa ero on vähintään havaitun
suuruinen:

```{.python tiedosto="esimerkit/13-ab-testi.py" osa="permutaatio"}
```

```{.tuloste tiedosto="esimerkit/13-ab-testi.odotettu" rivit="2-"}
```

Menetelmät antavat lähes saman p-arvon, mutta ne osuvat 0,05:n rajan
eri puolille. Tämä on hyödyllinen muistutus: 0,05 on sopimus, ei
luonnonvakio. Tulos, joka on lähellä rajaa, on heikko näyttö
kumpaankaan suuntaan. Ilmoita efektin koko ja sen luottamusväli
p-arvon rinnalla.

## Kaksi virhettä ja testin voima

Testi voi erehtyä kahdella tavalla. **Ensimmäisen lajin virhe** on
väärä löydös: eroa ei ole, mutta testi väittää sen löytyneen. Sen
todennäköisyys on merkitsevyystaso $\alpha$, tavallisesti 5 %.
**Toisen lajin virhe** on huti: ero on olemassa, mutta testi ei
havaitse sitä. Sen todennäköisyyttä merkitään $\beta$, ja
$1 - \beta$ on testin **voima** (*power*). Voima riippuu eron koosta,
hajonnasta ja otoskoosta, ja siksi otoskoko on päätettävä ennen
koetta: valitaan pienin ero, jolla on merkitystä, ja lasketaan, kuinka
monta havaintoa sen löytämiseen halutulla voimalla tarvitaan.

```{.python tiedosto="esimerkit/13-voima.py" osa="otoskoko"}
```

```{.tuloste tiedosto="esimerkit/13-voima.odotettu" rivit="1-1"}
```

Yhden prosenttiyksikön eron löytämiseen tarvitaan lähes 15 000
käyttäjää ryhmää kohti. Simulaatio vahvistaa laskelman ja näyttää,
mitä liian pieni koe tarkoittaa:

```{.python tiedosto="esimerkit/13-voima.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/13-voima.odotettu" rivit="2-"}
```

Kahdentuhannen käyttäjän koe löytäisi todellisen parannuksen vain
noin joka kuudennella kerralla. Alivoimaisen kokeen tulos "ei
merkitsevää eroa" ei siis kerro, ettei eroa ole. Tarvittava otoskoko
kasvaa kääntäen verrannollisesti eron neliöön: puolet pienempi ero
vaatii nelinkertaisen otoksen.

## Kahden keskiarvon vertailu

Kun mitattava suure on jatkuva (aika, muistinkulutus), verrataan
keskiarvoja. Testisuure on keskiarvojen erotus jaettuna sen
keskivirheellä; **Welchin** muoto ei oleta ryhmille samaa varianssia:

$$t = \frac{\bar x_B - \bar x_A}{\sqrt{s_A^2/n_A + s_B^2/n_B}}.$$

Pienillä otoksilla $t$ noudattaa Studentin $t$-jakaumaa
(`scipy.stats.ttest_ind(..., equal_var=False)` laskee p-arvon siitä);
kun havaintoja on kymmeniä tai enemmän ryhmää kohti,
normaaliapproksimaatio riittää.

```{.python tiedosto="esimerkit/13-keskiarvot.py" osa="welch"}
```

```{.tuloste tiedosto="esimerkit/13-keskiarvot.odotettu" rivit="1-2"}
```

Permutaatiotesti toimii keskiarvoille samoin kuin osuuksille:

```{.python tiedosto="esimerkit/13-keskiarvot.py" osa="permutaatio"}
```

```{.tuloste tiedosto="esimerkit/13-keskiarvot.odotettu" rivit="3-"}
```

Keskiarvotesti olettaa, että keskiarvo on mielekäs tunnusluku. Vinoille
ja raskashäntäisille suureille, kuten vasteajoille, verrataan
mieluummin mediaaneja tai persentiilejä bootstrapilla (luku
*Suorituskykymittausten tulkinta*).

## Sudenkuopat

P-arvo pitää paikkansa vain, jos analyysi tehdään kerran ennalta
päätetyllä tavalla. Kaksi yleistä virhettä rikkoo tämän. Testataan
niitä *A/A-testillä*, jossa versiot ovat samat ja jokainen löydös on
väärä:

```{.python tiedosto="esimerkit/13-sudenkuopat.py" osa="apu"}
```

**Kurkkiminen.** Jos tulos tarkistetaan testin aikana ja testi
lopetetaan heti, kun p-arvo alittaa rajan, väärien löydösten osuus
moninkertaistuu:

```{.python tiedosto="esimerkit/13-sudenkuopat.py" osa="kurkkiminen"}
```

**Monivertailu.** Kun samasta kokeesta tarkastellaan montaa
mittaria, joku niistä on sattumalta ”merkitsevä”. Bonferronin korjaus
jakaa merkitsevyystason vertailujen määrällä:

```{.python tiedosto="esimerkit/13-sudenkuopat.py" osa="monivertailu"}
```

```{.tuloste tiedosto="esimerkit/13-sudenkuopat.odotettu"}
```

## Käytännössä

- **Laske otoskoko ennen koetta.** Valitse pienin merkityksellinen
  ero ja haluttu voima (tavallisesti 80 %) ja mitoita koe niiden
  mukaan. Liian pieni koe hukkaa todelliset parannukset.
- **Päätä analyysi etukäteen.** Kurkkiminen kasvattaa
  väärien löydösten osuuden 5 %:sta yli 20 %:iin. Jos tuloksia on pakko
  seurata kesken, käytä tähän suunniteltuja sekventiaalisia
  menetelmiä.
- **Valitse päämittari ennen koetta.** Muut mittarit ovat
  tutkivia, ja niiden löydökset vaativat uuden kokeen tai korjauksen.
- **Ilmoita efekti ja väli.** ”B konvertoi 2,0 prosenttiyksikköä
  paremmin (95 %: 0,1–3,9)” kertoo enemmän kuin ”p = 0,04”.
- **Tarkista menetelmä permutaatiotestillä.** Se ei oleta
  jakaumaa ja paljastaa approksimaation ongelmat.
- **Tee A/A-testi.** Kun testausjärjestelmä ajetaan kahdella samalla
  versiolla, väärien löydösten pitää olla noin 5 %. Muuten
  satunnaistuksessa tai analyysissä on vika.

## Itsearviointi

- Osaat muotoilla nollahypoteesin ja tulkita p-arvon oikein.
- Osaat tehdä kahden osuuden z-testin ja permutaatiotestin.
- Osaat selittää ensimmäisen ja toisen lajin virheen ja testin voiman
  ja mitoittaa A/B-testin otoskoon.
- Osaat verrata kahta keskiarvoa Welchin testisuureella ja tiedät,
  milloin mediaanien vertailu on parempi.
- Osaat selittää kurkkimisen ja monivertailun vaikutuksen ja välttää
  ne.
- Osaat raportoida tuloksen efektin kokona ja luottamusvälinä.
