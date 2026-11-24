# Kellopuu ja reititys

Kello on piirin suurin ja tärkein johdin: se ajaa jokaista kiikkua,
vaihtaa tilaa joka jaksolla ja sen ajoitus määrää kaikkien muiden
polkujen ajoituksen. Siksi kellopuu rakennetaan omassa vaiheessaan
(clock tree synthesis, CTS) ennen tavallista reititystä.

## Kellopuu

Kellopuun tavoitteet ovat pieni vinous (skew), kohtuullinen latenssi
ja jyrkät reunat. Johtimen viive arvioidaan Elmore-mallilla: kunkin
johdinpalan vastus kertaa kaikki sen alapuolinen kapasitanssi.

```{.python tiedosto="esimerkit/08-kellopuu.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/08-kellopuu.py" osa="elmore"}
```

Verrataan kolmea tapaa viedä kello 16 kiikulle millimetrin neliössä:
ketjuna kiikusta toiseen, H-puuna, jossa jokaisen kiikun polku on yhtä
pitkä, ja H-puuna, jonka haarautumiskohdissa on puskurit.

```{.python tiedosto="esimerkit/08-kellopuu.py" osa="rakenteet"}
```

```{.python tiedosto="esimerkit/08-kellopuu.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-kellopuu.odotettu"}
```

Kuvassa on puskuroidun H-puun rakenne kahdella tasolla. Jokaisen
kiikkuryhmän polku juuresta on yhtä pitkä ja kulkee yhtä monen
puskurin läpi, joten viiveet ovat samat.

```{.dot otsikko="Puskuroitu H-puu: symmetriset polut kellolähteestä 16 kiikulle"}
digraph {
  rankdir=TB; nodesep=0.2; ranksep=0.3;
  lahde [label="kellolähde\n(PLL)"];
  node [shape=invtriangle, label="", width=0.3, height=0.25];
  p1; p2a; p2b; p3a; p3b; p3c; p3d;
  node [shape=box, style="rounded,filled", width=0.6, height=0.3,
        fontsize=9];
  k1 [label="4 kiikkua"]; k2 [label="4 kiikkua"];
  k3 [label="4 kiikkua"]; k4 [label="4 kiikkua"];
  lahde -> p1; p1 -> p2a; p1 -> p2b;
  p2a -> p3a; p2a -> p3b; p2b -> p3c; p2b -> p3d;
  p3a -> k1; p3b -> k2; p3c -> k3; p3d -> k4;
}
```

Ketju on lyhin, mutta sen vinous on 119 ps, mikä syö suoraan
pitomarginaalia (luku 4). H-puun symmetria poistaa vinouden, mutta
pitkä, kuormitettu johdin on hidas. Puskurit erottavat alapuolisen
kapasitanssin ja puolittavat latenssin. Oikeat kellopuut ovat
epäsymmetrisiä, koska kiikut eivät ole ruudukossa; CTS-algoritmi
tasapainottaa viiveet puskureilla ja johdinpituuksilla. Kellon
johtimille annetaan yleensä leveämmät johtimet ja tuplaetäisyys
naapureista ylikuulumisen vähentämiseksi.

## Reititys

Reititys tehdään kahdessa vaiheessa. *Globaali reititys* jakaa piirin
ruutuihin ja päättää, minkä ruutujen kautta kukin johdin kulkee, ja
arvioi ruuhkan. *Yksityiskohtainen reititys* piirtää johtimet
metallikerroksille suunnittelusääntöjä noudattaen. Kerroksia on
tyypillisesti 5–15; alimmat ovat ohuita paikallisia johtimia, ylimmät
paksuja ja nopeita pitkille johtimille ja tehoverkolle. Kerrokset
vuorottelevat vaaka- ja pystysuuntaa, ja niiden välillä kuljetaan
läpivienneillä (via).

Klassinen yksityiskohtainen reititin on Leen sokkeloreititin:
leveyshaku etenee lähteestä aaltorintamana, kunnes kohde löytyy, ja
reitti jäljitetään takaisin. Haku löytää lyhimmän reitin, jos sellainen
on.

```{.python tiedosto="esimerkit/08-reititys.py" osa="alue"}
```

```{.python tiedosto="esimerkit/08-reititys.py" osa="lee"}
```

```{.python tiedosto="esimerkit/08-reititys.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/08-reititys.odotettu"}
```

Yhdellä kerroksella ristikkäiset johtimet B ja C eivät mahdu, ja
ensimmäinen reitti (A) varaa tilaa, jota myöhemmät tarvitsevat. Toinen
kerros ratkaisee ristiriidan: B ja C vaihtavat kerrosta läpivienneillä.
Tuotannon reitittimet purkavat ja reitittävät uudelleen ristiriitaiset
johtimet (rip-up and reroute) iteratiivisesti, kunnes kaikki on
reititetty ilman sääntörikkeitä.

## Ylikuuluminen

Rinnakkaiset johtimet ovat kondensaattori: naapurin reuna kytkeytyy
johtimeen. Jos naapurit vaihtavat tilaa samaan aikaan vastakkaisiin
suuntiin, viive kasvaa; samaan suuntaan se pienenee. Sign-off-STA
huomioi tämän (signal integrity, SI), ja kriittiset johtimet
suojataan maajohtimilla tai etäisyydellä.

## Käytännössä

- **CTS ennen pitokorjausta.** Todellinen vinous tiedetään vasta
  kellopuun jälkeen, joten pitorikkeet korjataan vasta silloin.
- **Kellon portitus kellopuussa.** Portituslohkot (luku 9) sijoitetaan
  puun haaroihin; CTS tasapainottaa myös niiden läpi kulkevat polut.
- **Reititystila on resurssi.** Jos reititys ei suppene, vika on
  yleensä pohjapiirroksessa tai sijoittelun tiheydessä, ei
  reitittimessä.
- **Johdin on kallis.** Pienissä prosesseissa johtimen RC-viive on
  pituuden neliössä; pitkät johtimet puskuroidaan säännöllisin
  välein ja viedään ylemmille kerroksille.

## Itsearviointi

- Osaat laskea Elmore-viiveen yksinkertaiselle RC-puulle.
- Osaat vertailla kellopuun rakenteita vinouden, latenssin ja
  johdinpituuden kannalta.
- Osaat kuvata globaalin ja yksityiskohtaisen reitityksen sekä Leen
  algoritmin periaatteen.
- Osaat selittää, miksi reititysjärjestys ja kerrosten määrä
  vaikuttavat reitittyvyyteen.
