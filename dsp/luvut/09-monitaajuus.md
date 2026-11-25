# Monitaajuuskäsittely

Järjestelmän eri osat tarvitsevat eri näytetaajuuksia. Äänikortti
toimii 48 kHz:llä, CD-levyn ääni on 44,1 kHz:n näytteinä, ja
puheentunnistus tyytyy 16 kHz:iin. Radiovastaanotin näytteistää
kymmenillä megahertseillä ja laskee kaistan nopeasti alas. Tämä luku
näyttää, miten näytetaajuutta vaihdetaan aliasoimatta ja miten se
tehdään halvalla.

## Desimointi

Desimointi kertoimella $M$ säilyttää joka $M$:nnen näytteen. Uusi
Nyquistin taajuus on $f_s/(2M)$, ja kaikki sen yläpuolella oleva
**laskostuu** päästökaistalle. Siksi signaali alipäästösuodatetaan
ennen harvennusta. Signaalit ja järjestelmät -taidossa tämä tehtiin
`decimate`-funktiolla; tässä katsotaan, mitä suodin tekee.

```{.python tiedosto="esimerkit/09-desimointi.py" osa="taso"}
```

```{.python tiedosto="esimerkit/09-desimointi.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/09-desimointi.odotettu"}
```

7 kHz:n sini on 12 kHz:n näytetaajuudella yli Nyquistin taajuuden ja
laskostuu 5 kHz:iin täydellä voimakkuudellaan. Kun signaali suodatetaan
ensin, laskos on 90 dB alempana. Laskostunutta komponenttia ei voi
jälkikäteen erottaa oikeasta 5 kHz:n signaalista, joten suodatus on
tehtävä ennen harvennusta.

## Interpolointi

Interpoloinnissa kertoimella $L$ näytteiden väliin lisätään $L - 1$
nollaa. Spektri ei muutu, mutta uudella näytetaajuudella siinä näkyy
alkuperäisen spektrin $L - 1$ **peilikuvaa** taajuuksilla
$k f_s \pm f$. Alipäästösuodin poistaa peilit ja interpoloi nollat
oikeiksi arvoiksi. Suotimen vahvistuksen on oltava $L$, koska nollat
pienentävät keskimääräistä tasoa samalla kertoimella.

```{.python tiedosto="esimerkit/09-interpolointi.py" osa="nollat"}
```

```{.python tiedosto="esimerkit/09-interpolointi.py" osa="valmis"}
```

```{.tuloste tiedosto="esimerkit/09-interpolointi.odotettu"}
```

Nollien lisäyksen jälkeen 1 kHz:n komponentti on −12 dB, eli
$1/L$, ja peilit 11 ja 13 kHz:llä ovat yhtä voimakkaita. Suodatuksen
jälkeen signaali on oikealla tasolla, ja peilit ovat 103 dB alempana.

![Kahden edellisen esimerkin signaalit taajuustasossa. Ylhäällä
desimointi 48 kHz:stä 12 kHz:iin: ilman suodinta 7 kHz:n komponentti
laskostuu 5 kHz:iin. Alhaalla interpolointi 12 kHz:stä 48 kHz:iin:
nollien lisäys tuo peilikuvat, jotka suodin poistaa (kuvassa vahvistus
$L$ on jo mukana).](kuvat/monitaajuus.png){width=95%}

## Polyfaasirakenteet

Suora toteutus tuhlaa laskentaa. Desimoija laskee jokaisen ulostulon,
vaikka vain joka $M$:s säilytetään. Interpoloija kertoo nollia
kertoimilla. Molemmat korjataan **polyfaasihajotelmalla**: suodin
jaetaan $M$ (tai $L$) haaraan, joista haara $p$ sisältää kertoimet
$h[p], h[p+M], h[p+2M], \ldots$. Jokainen haara toimii matalalla
näytetaajuudella.

Desimoijassa riittää laskea vain säilytettävät ulostulot. Silloin
kertolaskuja on $N/M$ syötenäytettä kohti, ja tämä on laskennallisesti
sama asia kuin polyfaasirakenne.

```{.c tiedosto="esimerkit/09-polyfaasi/polyfaasi.h" osa="tyypit"}
```

```{.c tiedosto="esimerkit/09-polyfaasi/polyfaasi.c" osa="desimoi"}
```

Kenttä `vaihe` laskee, monta syötettä edellisestä ulostulosta on
kulunut, joten lohkon pituuden ei tarvitse olla $M$:n monikerta.
Interpoloijassa jokainen syötenäyte tuottaa $L$ ulostuloa, ja ulostulo
$p$ lasketaan haaran $p$ kertoimilla vain todellisista näytteistä.

```{.c tiedosto="esimerkit/09-polyfaasi/polyfaasi.c" osa="interpoloi"}
```

```{.c tiedosto="esimerkit/09-polyfaasi/main.c" osa="kaytto"}
```

```{.c tiedosto="esimerkit/09-polyfaasi/main.c" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/09-polyfaasi.odotettu"}
```

Desimoija antaa bitilleen saman tuloksen kuin suora suodatus ja
harvennus neljäsosalla laskennasta. Interpoloija tarvitsee neljäsosan
suoran toteutuksen kertolaskuista. Tulokset eroavat suorasta vain
pyöristyksen verran, koska nollilla kertominen jää pois mutta
summausjärjestys on sama. Vertailuohjelma tarkistaa molemmat SciPyn
`upfirdn`-funktiota vastaan.

## Rationaalinen muunnos

Muunnos 44,1 kHz:stä 48 kHz:iin on interpolointi kertoimella $L$ ja
desimointi kertoimella $M$, kun $L/M = 48\,000/44\,100 = 160/147$.
Välitaajuus olisi 7,056 MHz, mutta polyfaasirakenteessa sitä ei koskaan
lasketa: jokainen ulostulo tarvitsee vain yhden haaran.

```{.python tiedosto="esimerkit/09-rationaalinen.py" osa="suhde"}
```

Suotimen on poistettava sekä interpoloinnin peilit että desimoinnin
laskokset, joten sen raja on alemman Nyquistin taajuuden mukaan,
tässä 22,05 kHz. SciPyn `resample_poly` suunnittelee suotimen itse,
mutta oletussuodin on kompromissi. Audiossa halutaan tasainen
päästökaista 20 kHz:iin ja suuri vaimennus 22,05 kHz:stä ylöspäin,
joten suodin suunnitellaan itse.

```{.python tiedosto="esimerkit/09-rationaalinen.py" osa="muunna"}
```

```{.tuloste tiedosto="esimerkit/09-rationaalinen.odotettu"}
```

Oletussuotimella 19 kHz:n sävy tuottaa 22,9 kHz:n peilin vain 36 dB
signaalin alapuolelle. Oma suodin vie peilin yli 100 dB alemmas ja
maksaa 123 kertolaskua ulostulonäytettä kohti. Suoraan
7,056 MHz:llä laskettuna sama suodin vaatisi lähes 20 000.

## CIC: suodin ilman kertolaskuja

Kun desimointikerroin on suuri, esimerkiksi radiossa 64 tai 1024,
FIR-suodinkin on kallis. **CIC-suodin** (*cascaded
integrator–comb*) laskee $N$-kertaisen liukuvan summan ilman
kertolaskuja: $N$ integraattoria täydellä nopeudella, harvennus ja
$N$ kampaa (erotus edelliseen) matalalla nopeudella. Sen vaste on
$\left|\sin(\pi f R)/\sin(\pi f)\right|^N$, ja tasavahvistus $R^N$.

```{.python tiedosto="esimerkit/09-cic.py" osa="cic"}
```

Integraattorit ylivuotavat väistämättä, kun syötteessä on tasajännitettä.
Kahden komplementin aritmetiikassa ylivuoto ei haittaa, kunhan
sanaleveys riittää lopputulokselle: kammat laskevat erotuksia, ja
kiertävät ylivuodot kumoutuvat. Hogenauerin kaava antaa tarvittavan
leveyden: $B_{\text{ulos}} = B_{\text{sisään}} + N\log_2 R$.

```{.python tiedosto="esimerkit/09-cic.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/09-cic.odotettu"}
```

21 bitillä tulos on sama kuin kolminkertainen laatikkosuodin, vaikka
integraattori ylivuotaa. Yksi bitti vähemmän ja täyden tasajännitteen
syöte tuottavat väärän tuloksen. CIC:n vaste ei ole tasainen, vaan
laskee jo päästökaistalla. Siksi sen perään tulee lyhyt FIR, joka
korjaa vasteen ja desimoi viimeisen kertoimen (yleensä 2).

## Käytännössä

- **Suodata ennen harvennusta.** Laskostunutta signaalia ei voi korjata
  jälkikäteen.
- **Anna interpolointisuotimelle vahvistus $L$**, muuten taso putoaa
  $1/L$:ään.
- **Käytä polyfaasirakennetta** (`upfirdn`, `resample_poly`, C:ssä
  vain tarvittavat ulostulot). Älä koskaan kerro lisättyjä nollia.
- **Suunnittele rationaalisen muunnoksen suodin itse**, kun
  päästökaistan tasaisuudella tai peilien tasolla on vaatimus.
- **Käytä CIC-suodinta suurille desimointikertoimille** ja korjaa
  sen vaste lyhyellä FIR-suotimella. Laske sanaleveys Hogenauerin
  kaavalla.

## Itsearviointi

- Osaat selittää laskostumisen desimoinnissa ja peilikuvat
  interpoloinnissa sekä suotimen tehtävän molemmissa.
- Osaat toteuttaa desimoijan ja polyfaasi-interpoloijan C:llä ja laskea
  niiden kertolaskut näytettä kohti.
- Osaat muuntaa näytetaajuuden rationaalisella kertoimella ja
  suunnitella sen suotimen vaatimuksesta.
- Osaat selittää CIC-suotimen rakenteen, sen vasteen ja sen, miksi
  integraattorien ylivuoto ei haittaa.
