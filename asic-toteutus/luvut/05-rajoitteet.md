# SDC-rajoitteet ja kulmat

Ajoitusanalyysi ei tiedä, mitä piiriltä halutaan. Suunnittelija kertoo
sen rajoitteilla: kellojen jaksot, tulojen ja lähtöjen viiveet
ympäröivään maailmaan nähden sekä poikkeukset, kuten polut, jotka
saavat kestää useamman jakson. Rajoitteet kirjoitetaan SDC-muodossa
(Synopsys Design Constraints), joka on Tcl-kieltä ja alan yhteinen
standardi: samat rajoitteet ohjaavat synteesiä, sijoittelua ja
sign-off-analyysia.

## Perusrajoitteet

```{.text tiedosto="esimerkit/kertoja2.sdc" osa="perus"}
```

- `create_clock` määrittelee kellon ja sen jakson.
- `set_clock_uncertainty` varaa marginaalin kellon värinälle ja
  arvioimattomalle vinoudelle.
- `set_input_delay` kertoo, kuinka kauan ulkoinen logiikka käyttää
  jaksosta ennen kuin tulo on vakaa; `set_output_delay` vastaavasti,
  paljonko jaksosta ulkoinen vastaanottaja tarvitsee.
- `set_load` ja `set_input_transition` kuvaavat piirin ympäristön
  sähköisesti.

Rajoitteiden puuttuminen on vaarallisempaa kuin väärä rajoite:
rajoittamaton polku ei näy raportissa lainkaan.

## Monisykli- ja väärät polut

Kertoja voi toimia kahdella jaksolla, jos RTL varmistaa sen: tässä
tulot ja tulos ladataan samalla, joka toisella reunalla, joten tulos
lasketaan tuloparista, joka on ollut rekistereissä kaksi jaksoa.

```{.verilog tiedosto="esimerkit/kertoja2.v" osa="kertoja2"}
```

```{.text tiedosto="esimerkit/kertoja2_mc.sdc" osa="monisykli"}
```

Monisyklipolku siirtää asetustarkistuksen kahden jakson päähän.
Pitotarkistus tehdään SDC:n sääntöjen mukaan aina yhtä reunaa ennen
asetustarkistusta, joten se siirtyisi samalla reunalle 1: data ei
saisi muuttua ennen kuin yksi kokonainen jakso on kulunut, mikä
vaatisi jakson verran viivettä jokaiselle lyhyelle polulle. Komento
`-hold 1` palauttaa pitotarkistuksen lähtöreunalle; tämän luvun
analyysi tekee saman oletuksena.

```{.ajoituskaavio otsikko="Monisyklipolku: tarkistusreunat lähtöreunaan 0 nähden kolmella rajoitteella"}
{"signal": [
  {"name": "kello", "wave": "p...."},
  {"name": "reuna", "wave": "=====", "data": ["0", "1", "2", "3", "4"]},
  {"name": "a_r, b_r", "wave": "=.=.=", "data": ["pari 1", "pari 2", "pari 3"]},
  {"name": "tulo", "wave": "x.=.=", "data": ["tulo 1", "tulo 2"]},
  {"name": "oletus", "wave": "45z..", "data": ["pito", "asetus"]},
  {"name": "-setup 2", "wave": "z45z.", "data": ["pito", "asetus"]},
  {"name": "-setup 2, -hold 1", "wave": "4z5z.", "data": ["pito", "asetus"]}
]}
```

Kaaviossa merkintä on sen jakson kohdalla, jonka alkureunalla
tarkistus tehdään. Alin rivi on se, mitä kertoja tarvitsee: asetus
reunalla 2 ja pito reunalla 0.

Väärä polku (false path) poistaa polun analyysista kokonaan,
esimerkiksi käynnistyksessä pitkään pidettävän nollauksen. Pieni
jäsennin lukee SDC:n osajoukon analyysin asetuksiksi:

```{.python tiedosto="esimerkit/sta.py" osa="rajoitteet"}
```

```{.python tiedosto="esimerkit/sdc.py" osa="jasennin"}
```

Jäsennin tulkitsee monisyklitiedoston näin; solujen nimimallit
verrataan rekisterien nimiin:

```{.tuloste tiedosto="esimerkit/sdc.odotettu"}
```

```{.python tiedosto="esimerkit/05-sdc.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/05-sdc.odotettu"}
```

Monisyklipolku korjaa kertojan, mutta seuraavaksi pahin polku tulee
näkyviin: `vaihe` ohjaa kaikkien rekisterien sallintaa, ja sen
haarautuma on niin suuri, että kiikun lähtö vie 0,73 ns ja sitä
seuraava invertteri 0,49 ns. Sijoittelun jälkeinen optimointi korjaa
tällaiset johtimet puskuripuulla. Ajoituksen korjaaminen on tällaista:
jokainen korjaus paljastaa seuraavan polun.

Monisykli- ja väärä polku ovat *lupauksia*, joita ajoitusanalyysi ei
tarkista. Väärin asetettu poikkeus piilottaa todellisen rikkeen, ja
piiri toimii simuloinnissa mutta ei piillä. Virhe syntyy helposti:
jos tämän kertojan tulot ladattaisiin parillisella ja tulos
parittomalla reunalla, laskennalle jäisi vain yksi jakso, vaikka
koodi näyttää kaksivaiheiselta. Siksi lupaus tarkistetaan RTL:stä.
Tulosteen viimeinen rivi tulee testipenkistä, joka mittaa jokaisella
tuloksen latauksella, montako jaksoa tulorekisterit ovat olleet
vakaina:

```{.verilog tiedosto="esimerkit/tp_kertoja2.v" osa="lupaus"}
```

Tuotannossa sama ehto kirjoitetaan väitteeksi (assertion), joka on
mukana jokaisessa simuloinnissa ja formaalissa tarkistuksessa, ja
poikkeukset katselmoidaan.

## Johdetut kellot, kelloryhmät ja nollauksen vapautus

Kolme rajoitetta kuuluu lähes jokaiseen oikeaan SDC-tiedostoon, vaikka
yhden kellon esimerkki ei niitä tarvitse. Opetusanalyysi tuntee vain
yhden kellon, joten kahta ensimmäistä ei ajeta tässä:

```text
# Jakajan lähtö on uusi kello, jonka jakso johdetaan lähteestä.
create_generated_clock -name clk_puoli -source [get_ports clk] \
    -divide_by 2 [get_pins jakaja_reg/Q]
# Kellot, joiden välillä ei ole vaihesuhdetta: polkuja ei ajoiteta.
set_clock_groups -asynchronous -group {clk clk_puoli} -group {clk_usb}
```

- **Johdettu kello.** Kun kello syntyy piirin sisällä (jakaja, PLL:n
  lähtö, kellon portitus), analyysi ei tunnista sitä kelloksi ilman
  komentoa `create_generated_clock`. Sen takana olevat kiikut jäisivät
  rajoittamatta, tai ne ajoitettaisiin väärällä jaksolla.
- **Kelloryhmät.** Oletuksena analyysi ajoittaa jokaisen polun
  kaikkien kellojen välillä. Toisistaan riippumattomien kellojen
  välillä tulos on merkityksetön, ja `set_clock_groups -asynchronous`
  poistaa nämä polut. Ylitys tehdään tahdistimella ja tarkistetaan
  CDC-työkalulla; rajoite ei tee ylityksestä turvallista.
- **Nollauksen vapautus.** Asynkroninen nollaus saa alkaa milloin
  tahansa, mutta jos se vapautuu lähellä kellon reunaa, osa kiikuista
  ehtii samaan reunaan ja osa vasta seuraavaan, tai kiikku jää
  metastabiiliksi. Kirjasto antaa nollaustulolle kaksi rajoitetta:
  *recovery* on nollauksen asetusaika (vapautuksen on ehdittävä ennen
  reunaa) ja *removal* sen pitoaika (vapautus ei saa tulla heti
  reunan jälkeen).

Opetuskirjaston nollattavan kiikun `DFFR_X1` nollaustulo:

```{.text tiedosto="esimerkit/opetus.lib" osa="dffr"}
```

Taidon *RTL-suunnittelu SystemVerilogilla* nollauksen tahdistin tuo
vapautuksen kellon tahtiin. Tässä se nollaa 16-bittisen laskurin:

```{.verilog tiedosto="esimerkit/nollaus.v" osa="nollaus"}
```

```{.text tiedosto="esimerkit/nollaus.sdc" osa="nollaus"}
```

Ulkoinen nollaus on väärä polku, koska sen alkua ei ajoiteta. Polku
tahdistimen kiikulta `t2` laskurin nollaustuloihin on tavallinen
synkroninen polku, ja analyysi tarkistaa sen samalla koodilla kuin
datan; vain kirjastosta luettavat rajoitteet vaihtuvat:

```{.python tiedosto="esimerkit/05-nollaus.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/05-nollaus.odotettu"}
```

Nollausjohdin on suuren haarautuman johdin kuten kello, ja vinous
vaikuttaa siihen samoin kuin dataan: recovery-marginaali kasvaa ja
removal-marginaali pienenee. Kun laskurin kello on 0,4 ns myöhässä
tahdistimeen nähden, vapautus ehtii osalle kiikuista jo samalla
reunalla, jolla tahdistin vaihtui, ja laskuri voi lähteä liikkeelle
rikkinäisestä tilasta. Suurissa piireissä nollaus jaetaan
puskuripuulla ja tasapainotetaan kuten kellopuu (luku 8).

## Kulmat ja paikallinen vaihtelu

Transistorien nopeus vaihtelee valmistuserän (prosessi), käyttö-
jännitteen ja lämpötilan mukaan. Kirjasto karakterisoidaan näiden
ääripäissä (PVT-kulmat): hidas kulma (ss, matala jännite, kuuma) ja
nopea (ff, korkea jännite, kylmä). Asetus tarkistetaan hitaassa ja pito
nopeassa kulmassa. Lisäksi saman piirin sisällä viiveet vaihtelevat
paikasta toiseen (on-chip variation, OCV): myöhäisiä polkuja
hidastetaan ja aikaisia nopeutetaan muutamalla prosentilla.

```{.python tiedosto="esimerkit/05-kulmat.py" osa="kulmat"}
```

```{.python tiedosto="esimerkit/05-kulmat.py" osa="analyysi"}
```

```{.tuloste tiedosto="esimerkit/05-kulmat.odotettu"}
```

Kertoja toimii 333 MHz:n taajuudella tyypillisessä kulmassa, mutta ei
hitaassa, ja OCV syö marginaalista vielä 0,26 ns. Siirtorekisterin
pitomarginaali on hyvä hitaassa kulmassa mutta negatiivinen nopeassa.
Sign-off vaatii, että piiri läpäisee *kaikki* kulmat ja toimintatilat
(multi-corner multi-mode, MCMM).

## Käytännössä

- **SDC on osa suunnittelua.** Rajoitteet versioidaan RTL:n rinnalla,
  katselmoidaan ja testataan. Rajoitteeton polku on yleisin
  sign-off-yllätys.
- **Poikkeuksia mahdollisimman vähän.** Jokainen `set_false_path`
  on aukko analyysissa. Kellotusalueiden välit merkitään
  kelloryhmillä eikä yksittäisillä väärillä poluilla, ja ylitykset
  tarkistetaan CDC-työkalulla.
- **Ulkoiset viiveet budjetoidaan.** Lohkon tulo- ja lähtöviiveet
  sovitaan lohkojen kesken; tavallinen lähtökohta on, että kumpikin
  puoli saa noin puolet jaksosta.
- **Kulmamarginaalit eivät ole ilmaisia.** Pessimismi (OCV, suuri
  epävarmuus) kasvattaa piiriä ja tehoa. Edistyneet menetelmät
  (AOCV, POCV) arvioivat vaihtelun tilastollisesti ja vähentävät
  turhaa varmuutta.

## Itsearviointi

- Osaat kirjoittaa SDC:n kellolle, tulo- ja lähtöviiveille ja kuormalle.
- Osaat käyttää monisyklipolkua ja väärää polkua oikein, tiedät,
  mihin reunoihin `-setup` ja `-hold` siirtävät tarkistukset, ja osaat
  tarkistaa lupauksen RTL-simuloinnilla.
- Osaat kertoa, milloin tarvitaan johdettu kello ja kelloryhmät, ja
  selittää recovery- ja removal-tarkistuksen nollauksen vapautuksessa.
- Osaat selittää PVT-kulmat ja OCV:n ja sen, miksi asetus ja pito
  tarkistetaan eri kulmissa.
- Osaat jäljittää korjauksen jälkeen paljastuvan seuraavan pahimman
  polun syyn.
