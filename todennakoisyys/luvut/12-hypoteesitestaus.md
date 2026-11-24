# Hypoteesitestaus ja A/B-testit

Onko uusi versio parempi, vai onko ero sattumaa? *Hypoteesitestaus*
vastaa kysymykseen olettamalla ensin, ettei eroa ole (*nollahypoteesi*),
ja laskemalla, kuinka todennäköinen vähintään havaitun suuruinen ero
silloin olisi. Tämä todennäköisyys on *p-arvo*. Pieni p-arvo tarkoittaa,
että havainto sopii huonosti nollahypoteesiin.

## Kahden osuuden testi

Verkkokaupan versiolla A konvertoi 200 käyttäjää 2000:sta ja versiolla
B 240 käyttäjää 2000:sta.

```{.python tiedosto="esimerkit/12-ab-testi.py" osa="data"}
```

Jos versiot ovat yhtä hyviä, molempien osuus on yhdistetty $\hat p$, ja
osuuksien erotuksen keskivirhe on
$\sqrt{\hat p(1-\hat p)(1/n_A + 1/n_B)}$. Erotus jaettuna
keskivirheellä on likimain normaalijakautunut testisuure $z$:

```{.python tiedosto="esimerkit/12-ab-testi.py" osa="z"}
```

## Permutaatiotesti

Permutaatiotesti ei tarvitse jakaumaoletusta. Jos versioilla ei ole
eroa, käyttäjien ryhmänimet ovat merkityksettömiä, ja ne voi sekoittaa.
P-arvo on niiden sekoitusten osuus, joissa ero on vähintään havaitun
suuruinen:

```{.python tiedosto="esimerkit/12-ab-testi.py" osa="permutaatio"}
```

```{.tuloste tiedosto="esimerkit/12-ab-testi.odotettu"}
```

Menetelmät antavat lähes saman p-arvon, mutta ne osuvat 0,05:n rajan
eri puolille. Tämä on hyödyllinen muistutus: 0,05 on sopimus, ei
luonnonvakio. Tulos, joka on lähellä rajaa, on heikko näyttö
kumpaankaan suuntaan. Ilmoita efektin koko ja sen luottamusväli
p-arvon rinnalla.

## Sudenkuopat

P-arvo pitää paikkansa vain, jos analyysi tehdään kerran ennalta
päätetyllä tavalla. Kaksi yleistä virhettä rikkoo tämän. Testataan
niitä *A/A-testillä*, jossa versiot ovat samat ja jokainen löydös on
väärä:

```{.python tiedosto="esimerkit/12-sudenkuopat.py" osa="apu"}
```

**Kurkkiminen.** Jos tulos tarkistetaan testin aikana ja testi
lopetetaan heti, kun p-arvo alittaa rajan, väärien löydösten osuus
moninkertaistuu:

```{.python tiedosto="esimerkit/12-sudenkuopat.py" osa="kurkkiminen"}
```

**Monivertailu.** Kun samasta kokeesta tarkastellaan montaa
mittaria, joku niistä on sattumalta ”merkitsevä”. Bonferronin korjaus
jakaa merkitsevyystason vertailujen määrällä:

```{.python tiedosto="esimerkit/12-sudenkuopat.py" osa="monivertailu"}
```

```{.tuloste tiedosto="esimerkit/12-sudenkuopat.odotettu"}
```

## Käytännössä

- **Päätä otoskoko ja analyysi etukäteen.** Kurkkiminen kasvattaa
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
- Osaat selittää kurkkimisen ja monivertailun vaikutuksen ja välttää
  ne.
- Osaat raportoida tuloksen efektin kokona ja luottamusvälinä.
