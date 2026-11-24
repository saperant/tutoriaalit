# Transistorivahvistimet

Taidossa *Elektroniikan perusteet ja SPICE* transistori oli kytkin:
joko kyllästyksessä tai johtamatta. Vahvistimena se toimii näiden
välissä, *aktiivisella alueella*, jossa kollektorivirta seuraa kannan
jännitettä jatkuvasti. Vahvistimen suunnittelu jakautuu kahteen
vaiheeseen. Ensin asetetaan *toimintapiste* eli tasajännitteet ja
-virrat, joiden ympärillä signaali vaihtelee. Sitten lasketaan, miten
pienet vaihtelut toimintapisteen ympärillä vahvistuvat:
*piensignaalimalli*. Tämä kahtiajako on analogiasuunnittelun perusta, ja
sama ajatus toistuu operaatiovahvistimen sisällä, suodattimissa ja
muuntimissa.

## Toimintapiste

Yhteisemitterivahvistimessa kanta saa jännitteensä jännitteenjakajasta
R1–R2, ja emitterin ja maan välissä on vastus R_e. Kollektorivastus R_c
muuttaa kollektorivirran vaihtelun jännitteeksi.

![Yhteisemitterivahvistin. Jakaja R1–R2 ja emitterivastus Re asettavat
toimintapisteen; kondensaattorit erottavat tasajännitteen signaalista
ja ohittavat Re:n signaalitaajuuksilla.](kuvat/ce-vahvistin.png){width=62%}

Toimintapisteen laskussa kondensaattorit ovat katkoja. Kantaa ohjaava
jakaja korvataan Theveninin vastineella: jännite
$U_{th} = U_{cc} R_2 / (R_1 + R_2)$ ja sarjaresistanssi $R_1 \parallel
R_2$. Kanta–emitterijännite on noin 0,65 ... 0,7 V, ja emitterivastuksen
näkyy kannalle $(\beta + 1)$-kertaisena, koska sen läpi kulkee sekä kanta-
että kollektorivirta:

```{.python tiedosto="esimerkit/02-toimintapiste.py" osa="kasin"}
```

```{.spice tiedosto="esimerkit/02-toimintapiste.cir"}
```

```{.python tiedosto="esimerkit/02-toimintapiste.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/02-toimintapiste.odotettu"}
```

Laskussa on käytetty vahvistusta $\beta = 100$, vaikka mallin parametri
`BF` on 200. `BF` on vahvistuksen *huippuarvo*; pienillä virroilla
kanta–emitteriliitoksen rekombinaatio (mallin `ISE` ja `NE`) pienentää
sitä, ja tässä toimintapisteessä simuloitu $I_C/I_B$ on noin 106.
Datalehdetkin antavat $h_{FE}$:n vaihteluvälinä, esimerkiksi 100 ... 300,
ja kertovat, millä virralla se on mitattu. Hyvä toimintapiste ei
riipukaan tarkasta vahvistuksesta, kuten kohta nähdään.

Kollektori–emitterijännite 4,5 V on mukavasti keskellä: se jättää tilaa
signaalin heilahdukselle sekä alas (kyllästys noin 0,2 V:ssa) että ylös
(käyttöjännite 12 V miinus emitterin 1,3 V). Toimintapisteen sijainti
rajoittaa suurinta vääristymätöntä lähtösignaalia.

## Toimintapisteen herkkyys

Miksi emitterivastus ja jakaja, kun yksi kantavastus käyttöjännitteestä
riittäisi? Kiinteällä kantavastuksella kantavirta on vakio, ja
kollektorivirta on suoraan $\beta$ kertaa se. Vahvistus vaihtelee
yksilöittäin ja lämpötilan mukaan, joten toimintapiste vaeltaa.
Emitterivastus tekee piiristä *negatiivisen takaisinkytkennän*: jos
kollektorivirta kasvaa, emitterin jännite nousee, kanta–emitterijännite
pienenee ja virta palaa takaisin. Kun $(\beta + 1) R_e \gg R_1
\parallel R_2$, kollektorivirta on likimain
$(U_{th} - U_{BE})/R_e$ eikä riipu vahvistuksesta lainkaan.

Esimerkki simuloi molemmat piirit yhdeksällä yhdistelmällä: `BF` 100, 200
ja 400 sekä lämpötilat 0, 27 ja 85 °C. Netlist rakennetaan Pythonissa,
ja mallista vaihdetaan vain `BF`:

```{.python tiedosto="esimerkit/02-herkkyys.py" osa="piirit"}
```

```{.python tiedosto="esimerkit/02-herkkyys.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/02-herkkyys.odotettu"}
```

Kiinteällä kantavastuksella kollektorivirta vaihtelee yli kaksinkertaisesti,
jolloin kollektorin jännite vaihtelee noin 3 ja 8 voltin välillä ja
signaalin heilahdusvara katoaa milloin ylhäältä, milloin alhaalta.
Jakaja ja emitterivastus pitävät vaihtelun 17 %:ssa, josta suurin osa
tulee kanta–emitterijännitteen lämpötilakertoimesta (noin −2 mV/K).
Tämä on analogiasuunnittelun perusperiaate: *piirin ominaisuuksien on
riiputtava passiivisista komponenteista, ei aktiivisten komponenttien
huonosti tunnetuista parametreista*. Takaisinkytkentä on tapa saavuttaa
se.

## Piensignaalimalli

Kun signaali on pieni verrattuna toimintapisteen arvoihin, transistoria
voi kuvata lineaarisella mallilla. Hybridi-π-mallissa kanta–emitteri on
resistanssi $r_\pi$, ja kollektorivirta on jänniteohjattu virtalähde
$g_m u_{be}$. Mallin parametrit lasketaan toimintapisteestä:

$$
g_m = \frac{I_C}{U_T}, \qquad r_\pi = \frac{\beta}{g_m}, \qquad
r_o = \frac{V_A}{I_C}.
$$

Transkonduktanssi $g_m$ riippuu vain kollektorivirrasta: 1 mA:lla se on
noin 39 mS huoneenlämmössä ($U_T = kT/q \approx 25{,}9$ mV). Tämä on
bipolaaritransistorin tärkein ominaisuus, ja se on suoraan
eksponentiaalisen virta–jännite-yhteyden derivaatta. Early-jännite $V_A$
kuvaa sitä, miten kollektorivirta kasvaa hieman
kollektori–emitterijännitteen mukana; siitä tulee lähtöresistanssi
$r_o$.

Yhteisemitterivahvistimessa emitteri on signaalitaajuuksilla maassa
ohituskondensaattorin $C_e$ kautta. Kannan jännitevaihtelu $u_{be}$
tuottaa kollektorivirran $g_m u_{be}$, joka kulkee rinnankytkettyjen
$R_c$:n, kuorman $R_L$:n ja $r_o$:n läpi. Jännitevahvistus on siis
$-g_m (R_c \parallel R_L \parallel r_o)$, ja tulon jännitteenjako
lähteen resistanssin kanssa pienentää sitä hieman:

```{.python tiedosto="esimerkit/02-ce-vahvistin.py" osa="piensignaali"}
```

```{.spice tiedosto="esimerkit/02-ce-vahvistin.cir"}
```

Alarajataajuuden määrää lähinnä ohituskondensaattori. Se näkee
emitteristä katsoen pienen resistanssin: $1/g_m$ plus kannan
lähdeimpedanssi jaettuna $(\beta + 1)$:llä, rinnan $R_e$:n kanssa.
Siksi ohituskondensaattorin on oltava suuri, tässä 100 µF:

```{.python tiedosto="esimerkit/02-ce-vahvistin.py" osa="alaraja"}
```

```{.tuloste tiedosto="esimerkit/02-ce-vahvistin.odotettu"}
```

Vahvistus 147 eli 43 dB on suuri, mutta se riippuu suoraan $g_m$:stä
ja siten kollektorivirrasta ja lämpötilasta. Lisäksi se on epälineaarinen:
suurilla signaaleilla $g_m$ muuttuu signaalin mukana, ja lähtö vääristyy.
Käytännössä osa emitterivastuksesta jätetään ohittamatta
(*emitterin degeneraatio*): vahvistus pienenee likimain arvoon
$-R_c/R_e'$, mutta se ei enää riipu transistorista, ja vääristymä
pienenee samassa suhteessa. Sama vaihtokauppa, vahvistusta vakaudesta ja
lineaarisuudesta, on koko operaatiovahvistintekniikan perusta.

Ylärajataajuuden, tässä 6,5 MHz, määräävät transistorin sisäiset
kapasitanssit. Kollektori–kantakapasitanssi näkyy tuloon
vahvistuksella kerrottuna (*Millerin ilmiö*), joten suuri vahvistus
kaventaa kaistaa. Taajuusvaste on laskettu tarkasti vain SPICEssä;
käsin laskettuna Millerin likiarvo antaisi suuruusluokan.

## Emitteriseuraaja

Kun lähtö otetaan emitteriltä, saadaan *emitteriseuraaja*
(yhteiskollektorikytkentä). Emitterin jännite seuraa kantaa noin
0,65 V:n erotuksella, joten jännitevahvistus on hieman alle yksi. Hyöty
on impedanssimuunnos: tuloresistanssi on suuri, $(\beta + 1)(r_e + R_e)$
rinnan jakajan kanssa, ja lähtöresistanssi pieni, $r_e = 1/g_m$ plus
lähteen resistanssi jaettuna $(\beta + 1)$:llä.

```{.spice tiedosto="esimerkit/02-seuraaja.cir"}
```

```{.python tiedosto="esimerkit/02-seuraaja.py" osa="kasin"}
```

Lähtöresistanssi mitataan kuten laboratoriossa: vahvistus kuormittamatta
ja tunnetulla kuormalla, ja niiden suhteesta ratkaistaan sisäinen
resistanssi. Netlist tekee molemmat ajot `alterparam`-komennolla.

```{.python tiedosto="esimerkit/02-seuraaja.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/02-seuraaja.odotettu"}
```

Noin 18 ohmin lähtöresistanssi tarkoittaa, että seuraaja pystyy
ohjaamaan pieniä kuormia, joita yhteisemitterivahvistimen 4,7 kohmin
lähtö ei pystyisi. Siksi vahvistimissa on usein lähtöaste, jossa
seuraaja tai kaksi vastakkaista seuraajaa (*push-pull*) syöttää
kuorman. Operaatiovahvistimen lähtöaste on juuri tällainen.

## MOSFET vahvistimena

MOSFET toimii vahvistimena *kyllästysalueella* (nimi on harhaanjohtava:
se vastaa bipolaaritransistorin aktiivista aluetta), jossa nieluvirta
on likimain $\frac{K}{2}(U_{GS} - U_T)^2$. Transkonduktanssi on
$g_m = 2 I_D / (U_{GS} - U_T)$, ja samalla virralla se on yleensä
pienempi kuin bipolaaritransistorilla, koska $U_{GS} - U_T$ on
tyypillisesti 0,1 ... 0,5 V eikä 26 mV. MOSFETin etuja ovat
ääretön tasavirtatuloresistanssi (hila on eristetty) ja se, että
CMOS-prosessissa transistorit ovat halpoja ja pieniä. Siksi integroitujen
piirien vahvistimet, myös useimmat operaatiovahvistimet nykyään, ovat
MOSFET-rakenteisia. Biasoinnin periaatteet ovat samat: jakaja hilalle ja
lähdevastus takaisinkytkentänä.

Yhteislähdevahvistimen toimintapiste ratkeaa neliölaista. Koska
lähdevastuksen jännite riippuu nieluvirrasta, hila–lähdejännitteelle
saadaan toisen asteen yhtälö. Mallin `LAMBDA`-parametri (kanavan pituuden
modulaatio, MOSFETin vastine Early-ilmiölle) kasvattaa virtaa hieman
nielujännitteen mukana, ja se otetaan mukaan iteroimalla:

```{.spice tiedosto="esimerkit/02-mosfet.cir"}
```

```{.python tiedosto="esimerkit/02-mosfet.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/02-mosfet.odotettu"}
```

Vahvistus 13,8 on samalla virralla paljon pienempi kuin bipolaari-
transistorilla: 0,49 mA:n virralla bipolaaritransistorin $g_m$ olisi
19 mS, MOSFETin 1,4 mS. Ensimmäinen vertailu ilman `LAMBDA`-termiä erosi
5 %, mikä on hyvä muistutus siitä, että pienikin malliparametri näkyy,
kun sitä vertaa tarkkaan simulointiin.

## Käytännössä

- Aseta toimintapiste niin, että se ei riipu transistorin
  vahvistuksesta: jakaja kannalle ja emitterivastus, jonka yli on
  vähintään 1 V. Tarkista simuloimalla vahvistuksen ja lämpötilan
  ääripäillä.
- Laske vahvistus piensignaalimallista, mutta tarkista simuloimalla.
  Käsilasku kertoo, *mikä* määrää vahvistuksen; simulaattori kertoo
  tarkemman arvon ja kaistanleveyden.
- Valitse degeneroitu (osittain ohittamaton) emitterivastus, kun
  tarvitset toistettavan vahvistuksen ja pienen vääristymän. Suuri
  vahvistus ilman degeneraatiota on herkkä kaikelle.
- Erillisistä transistoreista rakennettuja vahvistimia käytetään nykyään
  lähinnä radiotaajuuksilla, pienikohinaisissa tuloasteissa ja
  tehoasteissa. Muuhun operaatiovahvistin on halvempi ja parempi; sen
  sisällä ovat kuitenkin samat rakenteet.
- Lue datalehdestä $h_{FE}$:n vaihteluväli ja mittausvirta. Mallin `BF`
  on huippuarvo, ei tyypillinen arvo kaikilla virroilla.

## Itsearviointi

- Osaat laskea bipolaaritransistorivahvistimen toimintapisteen
  Theveninin vastineen avulla ja tarkistaa sen simuloimalla.
- Osaat selittää, miksi emitterivastus vakauttaa toimintapisteen, ja
  osoittaa sen simuloimalla vahvistuksen ja lämpötilan vaihtelun.
- Osaat laskea piensignaalimallin parametrit $g_m$, $r_\pi$ ja $r_o$
  toimintapisteestä ja niistä yhteisemitterivahvistimen vahvistuksen.
- Osaat arvioida ohituskondensaattorin määräämän alarajataajuuden.
- Osaat selittää emitteriseuraajan impedanssimuunnoksen ja mitata
  lähtöresistanssin kuormitusmenetelmällä.
