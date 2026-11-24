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
marginaali on rike.

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

```{.python tiedosto="esimerkit/sta.py" osa="tarkistukset"}
```

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

## Kellon vinous ja pitoaika

Kello ei saavu kaikille kiikuille yhtä aikaa: kellopuun viiveet
eroavat (luku 8). Jos vastaanottavan kiikun kello myöhästyy, data
ehtii vaihtua ennen sen pitoaikaa. Siirtorekisterissä kiikkujen välissä
ei ole logiikkaa, joten pitoaika on tiukimmillaan:

```{.verilog tiedosto="esimerkit/siirto.v" osa="siirto"}
```

```{.python tiedosto="esimerkit/04-pito.py" osa="vinous"}
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
- **Kaikki ajoitus ei ole synkronista.** Kellotusalueiden välit ja
  asynkroniset nollaukset eivät kuulu STA:n piiriin; ne käsitellään
  tahdistimilla ja omilla tarkistuksillaan (CDC, RDC).

## Itsearviointi

- Osaat laskea saapumisajan, vaaditun ajan ja marginaalin sekä
  asetus- että pitoehdolle.
- Osaat lukea ajoitusraportin ja päätellä siitä hitauden syyn.
- Osaat selittää, miten kellon vinous vaikuttaa asetus- ja
  pitomarginaaliin, ja korjata pitorikkeen.
- Osaat kertoa, miksi johtimen kuorma arvioidaan eri tavoin eri
  vaiheissa.
