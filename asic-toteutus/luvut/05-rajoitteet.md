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
tulot ladataan parillisella ja tulos parittomalla jaksolla.

```{.verilog tiedosto="esimerkit/kertoja2.v" osa="kertoja2"}
```

```{.text tiedosto="esimerkit/kertoja2_mc.sdc" osa="monisykli"}
```

Monisyklipolku siirtää asetustarkistuksen kahden jakson päähän.
Pitotarkistus siirtyisi SDC:n sääntöjen mukaan samalla, joten se
palautetaan alkuperäiselle reunalle komennolla `-hold 1`; tämän
luvun analyysi tekee saman oletuksena. Väärä polku (false path)
poistaa polun analyysista kokonaan, esimerkiksi käynnistyksessä
pitkään pidettävän nollauksen. Pieni jäsennin lukee SDC:n osajoukon
analyysin asetuksiksi:

```{.python tiedosto="esimerkit/sta.py" osa="rajoitteet"}
```

```{.python tiedosto="esimerkit/05-sdc.py" osa="jasennin"}
```

```{.python tiedosto="esimerkit/05-sdc.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/05-sdc.odotettu"}
```

Monisyklipolku korjaa kertojan, mutta seuraavaksi pahin polku tulee
näkyviin: `vaihe` ohjaa kaikkien rekisterien sallintaa, ja sen
haarautuma on niin suuri, että yksittäinen invertteri on 0,57 ns.
Sijoittelun jälkeinen optimointi korjaa tällaiset johtimet
puskuripuulla. Ajoituksen korjaaminen on tällaista: jokainen korjaus
paljastaa seuraavan polun.

Monisykli- ja väärä polku ovat *lupauksia*, joita työkalu ei
tarkista. Väärin asetettu poikkeus piilottaa todellisen rikkeen, ja
piiri toimii simuloinnissa mutta ei piikissä. Poikkeukset
katselmoidaan ja niille kirjoitetaan väitteet (assertions), jotka
tarkistavat RTL-simuloinnissa, että lupaus pitää.

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
  `set_clock_groups -asynchronous` ja tarkistetaan CDC-työkalulla.
- **Ulkoiset viiveet budjetoidaan.** Lohkon tulo- ja lähtöviiveet
  sovitaan lohkojen kesken; tavallinen lähtökohta on, että kumpikin
  puoli saa noin puolet jaksosta.
- **Kulmamarginaalit eivät ole ilmaisia.** Pessimismi (OCV, suuri
  epävarmuus) kasvattaa piiriä ja tehoa. Edistyneet menetelmät
  (AOCV, POCV) arvioivat vaihtelun tilastollisesti ja vähentävät
  turhaa varmuutta.

## Itsearviointi

- Osaat kirjoittaa SDC:n kellolle, tulo- ja lähtöviiveille ja kuormalle.
- Osaat käyttää monisyklipolkua ja väärää polkua oikein ja tiedät,
  mitä tapahtuu, jos lupaus ei pidä.
- Osaat selittää PVT-kulmat ja OCV:n ja sen, miksi asetus ja pito
  tarkistetaan eri kulmissa.
- Osaat jäljittää korjauksen jälkeen paljastuvan seuraavan pahimman
  polun syyn.
