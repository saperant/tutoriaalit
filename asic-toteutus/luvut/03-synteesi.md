# Logiikkasynteesi

Synteesi muuttaa RTL:n kohdekirjaston soluista kootuksi netlistaksi.
Se on kolmivaiheinen: RTL käännetään yleisiksi logiikka- ja
muistielementeiksi, logiikka optimoidaan teknologiasta riippumatta ja
lopuksi kuvataan kirjaston soluiksi (technology mapping). Yosysissa
vaiheet ovat:

```text
read_verilog -sv laskuri.v      # jäsennys
synth -top laskuri -flatten     # proc, opt, fsm, memory, alumacc, techmap
dfflibmap -liberty opetus.lib   # kiikut kirjaston kiikuiksi
abc -liberty opetus.lib         # logiikka kirjaston porteiksi
opt_clean -purge
write_verilog netlista.v
```

`synth` tunnistaa tilakoneet, muistit ja aritmetiikan ja kuvaa ne
yleisiksi porteiksi. `dfflibmap` valitsee kirjastosta kiikut ja lisää
nollauksen ja sallinnan logiikaksi, jos kirjastossa ei ole sopivaa
kiikkua. ABC (Berkeleyn logiikkasynteesityökalu) optimoi
kombinaatiologiikan and–inverter-graafina ja kuvaa sen soluiksi.

## Laskurista netlistaksi

```{.verilog tiedosto="esimerkit/laskuri.v" osa="laskuri"}
```

```{.python tiedosto="esimerkit/synteesi.py" osa="syntetisoi"}
```

```{.python tiedosto="esimerkit/synteesi.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/synteesi.odotettu"}
```

Kahdeksan kiikkua vievät yli puolet pinta-alasta. Tämä on tyypillistä:
kiikku on suurin tavallinen solu, ja rekisterien määrä ratkaisee usein
pinta-alan enemmän kuin logiikka. Nollaus ja sallinta ovat
NOR-, AOI- ja OAI-portteja kiikkujen edessä, koska opetuskirjastossa on
vain yksinkertainen D-kiikku.

## Rakenne ratkaisee

Optimoija ei keksi uutta arkkitehtuuria. Sama yhteenlasku voidaan
toteuttaa ripple-carry-summaimena, jossa muistibitti kulkee kaikkien
bittien läpi, tai etuliiteverkkona, jossa muistibitit lasketaan
logaritmisessa ajassa:

```{.verilog tiedosto="esimerkit/summaimet.v" osa="ripple"}
```

```{.verilog tiedosto="esimerkit/summaimet.v" osa="ks"}
```

Yosys kuvaa `+`-operaattorin Brent–Kung-verkoksi:

```{.verilog tiedosto="esimerkit/summaimet.v" osa="bk"}
```

Kaikki kolme syntetisoidaan ja analysoidaan samalla
ajoitusanalyysillä (luku 4):

```{.python tiedosto="esimerkit/03-arkkitehtuuri.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-arkkitehtuuri.odotettu"}
```

Kogge–Stone on kolme kertaa nopeampi kuin ripple, mutta kolmanneksen
suurempi; Brent–Kung on näiden välissä. Viimeinen rivi on opettavainen:
ABC:n oletusskripti optimoi pinta-alaa ja purkaa Brent–Kung-verkon
takaisin ripple-ketjuksi, koska sille ei ole kerrottu ajoitustavoitetta.
Kaupallinen synteesi lukee SDC-rajoitteet (luku 5) ja optimoi
ajoituksen ensin; Yosys+ABC-vuossa rakenne on joko kirjoitettava RTL:ään
tai valittava optimointiskripti, joka säilyttää sen.

## Onko netlista sama piiri?

Synteesityökalu voi olla väärässä, ja RTL:ssä voi olla rakenteita,
jotka simulaattori ja synteesi tulkitsevat eri tavoin. Netlista
tarkistetaan kahdella tavalla. Porttitason simulointi ajaa saman
testipenkin RTL:lle ja netlistalle; solujen toiminnalliset mallit
tulevat kirjaston mukana:

```{.verilog tiedosto="esimerkit/opetus_solut.v" osa="mallit"}
```

```{.python tiedosto="esimerkit/03-ekvivalenssi.py" osa="simuloi"}
```

```{.python tiedosto="esimerkit/03-ekvivalenssi.py" osa="simulointi"}
```

Simulointi kattaa vain testatut syötteet. Muodollinen
ekvivalenssintarkistus todistaa piirit samoiksi kaikilla syötteillä:
miter-piiri ajaa molempia samoilla tuloilla ja vertaa lähtöjä, ja
SAT-ratkaisija etsii syötettä, jolla jokin lähtö eroaa:

```{.python tiedosto="esimerkit/03-ekvivalenssi.py" osa="miter"}
```

```{.python tiedosto="esimerkit/03-ekvivalenssi.py" osa="todistus"}
```

Lopuksi klassinen sudenkuoppa: puutteellinen herkkyyslista. Synteesi
ei välitä herkkyyslistasta, mutta simulaattori laskee lohkon uudelleen
vain listan signaalien muuttuessa:

```{.verilog tiedosto="esimerkit/epasuhta.v" osa="epasuhta"}
```

```{.python tiedosto="esimerkit/03-ekvivalenssi.py" osa="epasuhta-ajo"}
```

```{.tuloste tiedosto="esimerkit/03-ekvivalenssi.odotettu"}
```

RTL-simulointi näyttää väärän tuloksen, joka ei vastaa piiriä.
SystemVerilogin `always_comb` estää virheen, ja lint-työkalut
huomauttavat siitä.

## Käytännössä

- **Synteesiraportti luetaan.** Odottamattomat salvat, poistetut
  rekisterit ("removing unused") ja vakioiksi sievennetyt lähdöt
  kertovat RTL:n virheistä ennen kuin piiri on edes simuloitu
  porttitasolla.
- **Ekvivalenssi jokaisen muunnoksen jälkeen.** Tuotantovuossa RTL
  todistetaan ekvivalentiksi synteesin, DFT:n ja jokaisen käsin tehdyn
  netlistamuutoksen (ECO) jälkeen.
- **Arkkitehtuuri ensin.** Työkalu ei korjaa väärää rakennetta.
  Kriittisen polun aritmetiikka valitaan tietoisesti, ja tarvittaessa
  kirjoitetaan rakenteena tai käytetään valmistajan aritmetiikka-IP:tä.
- **Hierarkia vai litistys.** Litistetty netlista optimoituu
  paremmin, mutta hierarkia helpottaa virheenetsintää, osittaista
  synteesiä ja ECO-muutoksia. Suuret piirit syntetisoidaan lohkoittain.

## Itsearviointi

- Osaat kuvata synteesin vaiheet ja ajaa Yosysin solukirjastoa vasten.
- Osaat selittää, miksi rakenteen valinta vaikuttaa enemmän kuin
  optimoija, ja mitä ajoitusrajoitteet muuttavat synteesissä.
- Osaat tarkistaa netlistan porttitason simuloinnilla ja muodollisella
  ekvivalenssilla ja kertoa niiden erot.
- Osaat tunnistaa simuloinnin ja synteesin välisen epäsuhdan
  aiheuttajia.
