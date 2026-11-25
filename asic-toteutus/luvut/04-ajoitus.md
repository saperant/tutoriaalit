# Staattinen ajoitusanalyysi

Digitaalitekniikassa ajoitusyhtälöt laskettiin kiinteillä viiveillä.
Oikeassa netlistassa jokaisen portin viive riippuu kuormasta ja tulon
siirtymäajasta (luku 2), ja kello saapuu kiikuille eri aikaan. Tämä
luku rakentaa ajoitusanalyysin, joka käyttää kirjaston taulukoita ja
Yosysin netlistaa, ja käyttää sitä asetus- ja pitorikkeiden
analysointiin.

## Ajoitusgraafi

Ajoitusanalyysi (static timing analysis, STA) näkee piirin graafina,
jonka solmuja ovat pinnit ja kaaria solujen ajoituskaaret ja johtimet.
Polku alkaa *alkupisteestä* (piirin tulo tai kiikun lähtö kellon
jälkeen) ja päättyy *loppupisteeseen* (kiikun datatulo tai piirin
lähtö). Analyysi laskee jokaiselle pisteelle saapumisajan ja vertaa
sitä vaadittuun aikaan; erotus on *marginaali* (slack). Negatiivinen
marginaali on rike. Kuvassa yhtenäiset nuolet ovat datapolku ja
katkoviivat kellopolut; niiden viive-ero on vinous.

```{.dot otsikko="Ajoituspolku: data kulkee lähettävältä kiikulta porttien läpi vastaanottavalle, ja kello saapuu kummallekin omaa polkuaan"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.3;
  node [width=0.6, height=0.35];
  kello [label="kello", shape=plaintext, style="", width=0.4];
  a [label="lähettävä\nkiikku"]; b [label="vastaan-\nottava kiikku"];
  g1 [label="portti"]; g2 [label="portti"]; g3 [label="portti"];
  a -> g1 -> g2 -> g3 -> b;
  edge [style=dashed, color="#546676", constraint=false];
  kello -> a;
  kello -> b;
}
```

Ensin tarvitaan jokaisen johtimen kuorma: nielujen pinnikapasitanssit
ja arvio johtimen omasta kapasitanssista. Ennen sijoittelua johdinta
ei ole, joten pituus arvioidaan haarautumasta (wire load model);
sijoittelun jälkeen käytetään todellisia pituuksia ja reitityksen
jälkeen mitattuja (parasiittien poiminta, luku 10):

```{.python tiedosto="esimerkit/sta.py" osa="kuorma"}
```

Saapumisajat edetään graafissa: portin lähdön aika on tulon aika plus
taulukosta luettu viive, ja lähdön siirtymäaika luetaan omasta
taulukostaan seuraavan portin tuloksi. Myöhäinen analyysi (asetus)
käyttää suurinta, aikainen (pito) pienintä aikaa:

```{.python tiedosto="esimerkit/sta.py" osa="eteneminen"}
```

Loppupisteessä verrataan. Asetusehdossa data on ehdittävä ennen
seuraavaa reunaa vastaanottavan kiikun kellon viive huomioiden;
pitoehdossa data ei saa muuttua ennen kuin samaan reunaan kuuluva
pitoaika on kulunut:

$$t_{saapuminen,max} \leq T + t_{kello,vast} - t_{asetus} - t_{\text{epävarmuus}}$$

$$t_{saapuminen,min} \geq t_{kello,vast} + t_{pito} + t_{\text{epävarmuus}}$$

Asetusehto ajoituskaaviona; yksi merkki on neljännes kellojaksosta.
Data lähtee reunalla 1 ja vakiintuu vastaanottajan tulossa yhden
merkin ennen asetusikkunaa, joka edeltää reunaa 2. Tuo väli on
marginaali. Hitaampi logiikka siirtäisi datan muutoksen ikkunan
sisään, ja marginaali olisi negatiivinen. Samat ehdot kiinteillä
viiveillä ovat taidossa *Digitaalitekniikka*.

```{.ajoituskaavio otsikko="Asetusehto: data vakiintuu ennen asetusikkunaa, ja väliin jää marginaali"}
{"signal": [
  {"name": "kello", "wave": "l.h.l.h.l."},
  {"name": "reuna", "wave": "z.=...=...", "data": ["1", "2"]},
  {"name": "lähettäjän Q", "wave": "=..=......", "data": ["vanha", "uusi"]},
  {"name": "vastaanottajan D", "wave": "=...=.....", "data": ["vanha", "uusi"]},
  {"name": "asetusikkuna", "wave": "0....10..."},
  {"name": "marginaali", "wave": "z...3z....", "data": ["+"]}
]}
```

```{.python tiedosto="esimerkit/sta.py" osa="tarkistukset"}
```

Sama silmukka tarkistaa myös kiikun asynkronisen nollaustulon: taulukko
`ASYNKRONISET` vaihtaa sille kirjastosta luettavat rajoitteet. Siihen
palataan luvussa 5.

## Kriittinen polku

Rekisteröity 8×8-kertoja 500 MHz:n kellolla (2 ns):

```{.verilog tiedosto="esimerkit/kertoja.v" osa="kertoja"}
```

```{.python tiedosto="esimerkit/sta.py" osa="raportti"}
```

```{.python tiedosto="esimerkit/sta.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/sta.odotettu"}
```

Raportti on STA-työkalun tärkein tuloste: se näyttää jokaisen portin
osuuden. Kiikun lähtö on hidas (0,35 ns), koska rekisteri `a_r[7]`
ajaa monta kertojan porttia. Sen jälkeen XOR-ketju laskee osittais-
tulojen summaa ja AOI/OAI-ketju kuljettaa muistibittiä: kertoja on
käytännössä summainketju. Marginaali on −0,49 ns, joten piiri toimii
noin 400 MHz:n taajuudella mutta ei 500 MHz:n.

Kriittinen polku on vain pahin tapaus. Sama analyysi antaa jokaiselle
loppupisteelle sen pahimman marginaalin, ja jakauma kertoo, kuinka
suuri korjaus tarvitaan:

![Tulorekisterin jokaisen bitin pahin asetusmarginaali 2 ns:n
jaksolla. Seitsemän ylintä bittiä rikkoo ehdon, ja marginaali pienenee
bitti bitiltä: muistibitin ketju pitenee. Yhden polun korjaaminen ei
riitä, vaan koko ylempää puoliskoa on
nopeutettava.](kuvat/marginaalit.png){width=88%}

## Kellon vinous ja pitoaika

Kello ei saavu kaikille kiikuille yhtä aikaa: kellopuun viiveet
eroavat (luku 8). Jos vastaanottavan kiikun kello myöhästyy, data
ehtii vaihtua ennen sen pitoaikaa. Siirtorekisterissä kiikkujen välissä
ei ole logiikkaa, joten pitoaika on tiukimmillaan:

```{.verilog tiedosto="esimerkit/siirto.v" osa="siirto"}
```

```{.python tiedosto="esimerkit/04-pito.py" osa="vinous"}
```

Kuvassa kiikku A lähettää ja kiikku B vastaanottaa. B:n kello
saapuu vinouden verran myöhemmin. A:n uusi arvo ehtii B:n tuloon ennen
kuin B:n pitoaika omalla, myöhästyneellä reunallaan on ohi, joten B
näytteistää väärän arvon. Yksi merkki on neljännes kellojaksosta.

```{.ajoituskaavio otsikko="Pitorike: vastaanottajan kello myöhästyy vinouden verran"}
{"signal": [
  {"name": "kello A", "wave": "l.h.l.h."},
  {"name": "kello B", "wave": "l..h.l.h"},
  {"name": "A:n Q", "wave": "=..=....", "data": ["vanha", "uusi"]},
  {"name": "B:n D", "wave": "=..=....", "data": ["vanha", "uusi"]},
  {"name": "B:n pito", "wave": "0..10..."},
  {"name": "rike", "wave": "z..5z...", "data": ["!"]}
]}
```

Vinous siirtää aikaa: asetusmarginaali kasvaa täsmälleen sen verran
kuin pitomarginaali pienenee. Positiivista vinousta käytetään
tarkoituksella pitkien polkujen nopeuttamiseen (useful skew), kun
pitomarginaalia on varaa. Pitorike korjataan lisäämällä datapolulle
viivettä:

```{.python tiedosto="esimerkit/04-pito.py" osa="puskurit"}
```

```{.python tiedosto="esimerkit/04-pito.py" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/04-pito.odotettu"}
```

## Käytännössä

- **Asetus hitaimmassa, pito nopeimmassa.** Asetusrike riippuu
  kellojaksosta ja korjataan hidastamalla kelloa tai nopeuttamalla
  polkua; pitorike ei riipu jaksosta ja rikkoo piirin kaikilla
  taajuuksilla. Pito korjataan vasta kellopuun jälkeen, kun vinous on
  tiedossa.
- **Raportin alku kertoo syyn.** Suuri ensimmäinen viive on
  haarautumaongelma (puskuroi tai monista rekisteri), pitkä ketju
  samanlaisia soluja on arkkitehtuuriongelma (luku 3), yksittäinen
  hidas solu on kokovalintaongelma.
- **Opetusanalyysin rajat.** Tuotannon STA erottaa nousevan ja
  laskevan reunan ja portin unateness-tiedon, laskee johtimen viiveen
  RC-verkosta, ja käyttää tilastollisia OCV-malleja. Periaate on sama
  kuin tässä.
- **Kaikki ajoitus ei ole synkronista.** Kellotusalueiden välit
  eivät kuulu STA:n piiriin; ne käsitellään tahdistimilla ja omilla
  tarkistuksillaan (CDC, RDC). Asynkronisen nollauksen alkua ei
  ajoiteta, mutta sen vapautus ajoitetaan (luku 5).

## Itsearviointi

- Osaat laskea saapumisajan, vaaditun ajan ja marginaalin sekä
  asetus- että pitoehdolle.
- Osaat lukea ajoitusraportin ja loppupisteiden marginaalijakauman ja
  päätellä niistä hitauden syyn.
- Osaat selittää, miten kellon vinous vaikuttaa asetus- ja
  pitomarginaaliin, ja korjata pitorikkeen.
- Osaat kertoa, miksi johtimen kuorma arvioidaan eri tavoin eri
  vaiheissa.
