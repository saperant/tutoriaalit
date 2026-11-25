# Pinta-ala ja teho

Suorituskyky on vain yksi kolmesta tavoitteesta. Pinta-ala määrää
valmistuskustannuksen, ja teho määrää jäähdytyksen, akun keston ja
käyttökustannuksen. Usein teho on se rajoite, joka ratkaisee: siru, joka
olisi nopein, ei saa kuluttaa enempää kuin jäähdytys poistaa.
Toteutusvaiheessa teho mitataan synteesin ja sijoittelun tuloksista
(paketti *ASIC-toteutus*). Arkkitehtuurivaiheessa sitä ei ole, joten
käytetään malleja, jotka skaalaavat tunnettuja arvoja.

## Dynaaminen teho ja vuoto

CMOS-logiikan teho on kahta lajia. *Dynaaminen teho* kuluu, kun
kapasitanssi varataan ja puretaan:

$$P_{\text{dyn}} = \alpha C V^2 f,$$

missä $\alpha$ on kytkeytyvä osuus jaksossa, $C$ kytkettävä
kapasitanssi, $V$ jännite ja $f$ taajuus. *Vuototeho* kuluu aina, kun
virta on päällä, myös kun mitään ei lasketa. Vuotovirta kasvaa
jännitteen mukana eksponentiaalisesti, koska suurempi jännite madaltaa
transistorin kynnystä (*drain-induced barrier lowering*, DIBL).

Taajuus riippuu jännitteestä: transistori kytkee sitä nopeammin, mitä
enemmän jännite ylittää kynnysjännitteen $V_t$. Sakurain ja Newtonin
*alfa-potenssilaki* mallintaa tämän: $f \propto (V - V_t)^a / V$, missä
$a$ on nykyprosesseissa noin 1,3.

```{.python tiedosto="esimerkit/arkki/teho.py" osa="piiri"}
```

Kertoimet ovat havainnollisia. Oikeat arvot tulevat prosessin
piirikirjastoista ja ne kalibroidaan synteesin tai mittausten
perusteella.

## Jännitteen ja taajuuden skaalaus

DVFS (*dynamic voltage and frequency scaling*) laskee jännitettä ja
taajuutta yhdessä. Koska dynaaminen teho riippuu jännitteestä
toiseen potenssiin ja taajuudesta lineaarisesti, ja taajuus laskee
jännitteen mukana, teho laskee nopeammin kuin nopeus. Tehtävä, joka
vaatii 3 miljardia jaksoa, eri jännitteillä:

```{.python tiedosto="esimerkit/08-dvfs.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/08-dvfs.odotettu"}
```

![Vasemmalla koko tehtävän energia ja energia–viivetulo jännitteen
funktiona. Oikealla määräaikatehtävän energia: ilman alustan tehoa
matalin jännite voittaa, mutta 20 W:n alusta siirtää minimin noin
0,9 V:iin.](kuvat/dvfs.png){width=100%}

Jännitteen laskeminen 1,0 V:sta 0,7 V:iin pidentää ajoa 57 %, mutta
puolittaa energian. Tästä syystä tehorajoitteinen siru ajaa monta ydintä
matalalla jännitteellä mieluummin kuin vähän ytimiä korkealla.
*Energia–viivetulo* (EDP) yhdistää kaksi tavoitetta: sen minimi
painottaa sekä energiaa että nopeutta.

```{.python tiedosto="esimerkit/arkki/teho.py" osa="mittarit"}
```

Taulukon jälkimmäinen osa kysyy, kannattaako tehtävä, jolla on
määräaika, ajaa nopeasti ja levätä (*race to idle*) vai hitaasti
määräaikaan asti. Pelkän ytimen energialla hidas voittaa aina. Kun
mukana on *alustan teho*, eli muisti, väylät ja oheislaitteet, jotka
kuluttavat aina kun ydin on käynnissä, optimi siirtyy keskelle: nopeampi
ajo lyhentää aikaa, jonka alusta on päällä. Tällä 20 W:n alustalla
paras jännite on 0,9 V. Oikean järjestelmän optimi riippuu siitä, mitä
lepotilassa voi sammuttaa.

## Energia operaatiota kohden

Horowitz (2014) kokosi 45 nm:n prosessin energiat, joita käytetään yhä
suuruusluokkien vertailuun:

```{.python tiedosto="esimerkit/arkki/teho.py" osa="energia"}
```

Tärkein havainto on suhde: 64 bitin DRAM-luku maksaa satoja kertoja
enemmän kuin liukulukukertolasku. Kun luvun 2 ytimien energia lasketaan
hutikäyristä ja operaatiolaskureista, tulos on yksiselitteinen:

```{.python tiedosto="esimerkit/08-energia.py" osa="kertoimet"}
```

```{.python tiedosto="esimerkit/08-energia.py" osa="energia"}
```

```{.tuloste tiedosto="esimerkit/08-energia.odotettu"}
```

Laskenta on alle 2 % energiasta jokaisessa ytimessä. Lohkottu
matriisitulo kuluttaa kuudesosan naiivin energiasta saman tuloksen
laskemiseen, koska se hakee muistista vähemmän. Energiatehokkuus on siis
ennen kaikkea datan liikkumisen minimointia: paikallisuutta, suurempia
ja lähempiä muisteja, ja kiihdyttimissä tietovuota, joka käyttää
jokaisen haetun luvun monta kertaa. Timeloop ja Accelergy mallintavat
juuri tätä kiihdyttimille.

## Välimuistin koko

Välimuistin koon valinta on klassinen kolmen tavoitteen kauppa.
CACTI-tyylinen malli skaalaa viiveen, energian ja pinta-alan koosta:
johtimet pitenevät kuten sivun pituus, joten viive ja energia kasvavat
kuten koon neliöjuuri, ja pinta-ala kasvaa koon mukana. Hutiosuus
pienenee kokemusperäisen neliöjuurisäännön mukaan (Hartstein ym. 2006):

```{.python tiedosto="esimerkit/arkki/teho.py" osa="pinta-ala"}
```

```{.python tiedosto="esimerkit/08-valimuisti.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/08-valimuisti.py" osa="laskenta"}
```

```{.tuloste tiedosto="esimerkit/08-valimuisti.odotettu"}
```

![Sama malli tiheämmällä ruudukolla: viiveen ja energian minimit ovat
eri kohdissa, yli kymmenkertaisen kokoeron päässä
toisistaan.](kuvat/valimuisti.png){width=100%}

Keskimääräinen muistiviive (AMAT) on pienin 128 KiB:llä, mutta energia
viittausta kohden on taulukon riveistä pienin 2 MiB:llä. Yksi välimuisti ei voi olla
optimaalinen molemmille, ja tämä on *muistihierarkian* perustelu: pieni
ja nopea L1 lähellä ydintä, suuri ja energiatehokas viimeisen tason
välimuisti sen takana. Neliöjuurisääntö on karkea keskiarvo monista
kuormista; luvun 2 hutikäyrät osoittavat, että yksittäisen kuorman käyrä
on portaittainen.

CACTI laskee samat suureet piirin rakenteesta: pankit, alijoukot,
johdotus ja lukuvahvistimet. McPAT kokoaa sen ja vastaavat mallit
ytimille, verkoille ja muistiohjaimille koko suorittimen tehoksi ja
pinta-alaksi. Molempien tulokset ovat suuntaa antavia, ja ne
kalibroidaan mittauksiin, kun mittauksia on.

## Pinta-alasta hinnaksi

Luvun alussa todettiin, että pinta-ala määrää valmistuskustannuksen.
Yhteys ei ole lineaarinen. Suuria piirejä mahtuu kiekolle vähemmän, ja
lisäksi suurempi osa niistä on viallisia, koska valmistusvirhe osuu
suureen piiriin todennäköisemmin. Saantomallit ja kiekon geometria ovat
taidon *ASIC-toteutus* aihetta; arkkitehtuurivaiheessa riittää niistä
johdettu hinta pinta-alan funktiona:

```{.python tiedosto="esimerkit/08-hinta.py" osa="malli"}
```

```{.python tiedosto="esimerkit/08-hinta.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/08-hinta.odotettu" asti="800"}
```

Neliömillimetrin hinta yli kaksinkertaistuu, kun piiri kasvaa 50:stä
800 neliömillimetriin: pinta-alan kaksinkertaistaminen maksaa enemmän
kuin kaksi kertaa. Siksi luvun 9 suunnittelutilassa pinta-ala on
rajoite eikä vapaa muuttuja, ja siksi suuri järjestelmä kannattaa
joskus jakaa pienempiin paloihin, jotka valmistetaan ja testataan
erikseen (*chiplet*):

```{.python tiedosto="esimerkit/08-hinta.py" osa="jako"}
```

```{.tuloste tiedosto="esimerkit/08-hinta.odotettu" alkaen="yksi 800"}
```

Neljä palaa maksavat tällä mallilla puolet yhden suuren piirin hinnasta.
Malli jättää pois kokoonpanon ja palojen väliset liitännät, jotka
maksavat pinta-alaa, tehoa ja viivettä, joten jako ei ole ilmainen;
laskelma kertoo, kuinka paljon niihin on varaa käyttää.

## Käytännössä

- **Pinta-alan hinta kasvaa alaa nopeammin.** Laske hinta saannon
  kanssa, ennen kuin lisäät välimuistia tai ytimiä "koska tilaa on".
- **Teho on usein rajoite, ei tavoite.** Maksimoi suorituskyky
  tehobudjetin sisällä. Budjetti tulee jäähdytyksestä tai
  virtalähteestä, ja se on kovempi raja kuin pinta-ala.
- **Energia on datan liikettä.** Laskentayksiköiden optimointi ei
  auta, jos muistiliikenne hallitsee. Laske energia muistitasoittain
  ennen kuin optimoit laskentaa.
- **DVFS ja alusta yhdessä.** Matalin jännite minimoi ytimen energian,
  mutta koko järjestelmän optimi riippuu siitä, mitä muuta on päällä.
- **Skaalaa tunnetusta.** Malli, joka skaalaa mitatusta tai
  syntetisoidusta lohkosta, on luotettavampi kuin malli tyhjästä.
  Kirjaa, mistä kertoimet ovat peräisin.

## Itsearviointi

- Osaat laskea dynaamisen tehon ja vuototehon ja selittää, miten ne
  riippuvat jännitteestä ja taajuudesta.
- Osaat arvioida DVFS:n vaikutuksen energiaan ja selittää, milloin
  nopea ajo ja lepo voittaa hitaan ajon.
- Osaat laskea kuorman energian muistitasoittain hutikäyristä ja
  energioista operaatiota kohden.
- Osaat perustella muistihierarkian välimuistin koon, viiveen,
  energian ja pinta-alan skaalaussäännöillä.
- Osaat arvioida piirin hinnan pinta-alasta saannon kanssa ja selittää,
  miksi hinta kasvaa pinta-alaa nopeammin.
