# Etupää ja välikieli

HLS-työkalun ensimmäinen puolisko on tavallinen kääntäjä: se lukee
lähdekoodin, tarkistaa sen ja muuttaa sen välikieleksi. Ero
ohjelmistokääntäjään on kohteessa. Ohjelmistokääntäjä tuottaa käskyjä,
jotka suoritetaan järjestyksessä, ja sen välikieli kuvaa ohjausvuota.
HLS-työkalu tuottaa rinnakkaista laitteistoa, ja sen tärkein välikieli
on *tietovuograafi*, joka kertoo vain, mikä operaatio tarvitsee minkäkin
tuloksen. Järjestyksen päättää vasta ajoitus.

Taito *Kääntäjätekniikka* käsittelee jäsentämisen ja välikielet
yleisesti. Tässä luvussa katsotaan, mitä niistä tarvitaan laitteiston
tuottamiseen ja miksi lähdekielelle asetetaan rajoituksia.

## Mitä C++:sta voi syntetisoida

Laitteisto on kiinteä: sen rekisterien määrä, muistien koko ja johdot
päätetään synteesissä. Siksi syntetisoitava koodi ei saa tarvita mitään,
minkä koko selviää vasta ajon aikana:

| Rakenne | Miksi ongelma | Korvaava tapa |
|---------------------------|------------------------------|------------------------------|
| dynaaminen muisti (`new`, `malloc`) | muistin koko ei ole tiedossa | kiinteän kokoinen taulukko |
| rekursio | pinon syvyys ei ole tiedossa | silmukka ja oma pino taulukossa |
| osoittimet ja niiden aritmetiikka | osoite voi viitata mihin tahansa | taulukko ja indeksi |
| järjestelmäkutsut, tiedostot, `printf` | laitteistossa ei ole käyttöjärjestelmää | testipenkissä, ei ytimessä |
| virtuaalifunktiot | kutsun kohde selviää ajon aikana | mallit (*template*) |
| liukuluvut | sallittuja, mutta yksikkö on suuri ja hidas | kiinteä pilkku (`ap_fixed`) |
| jakolasku | sallittu, mutta vie kymmeniä jaksoja tai paljon logiikkaa | kertolasku käänteisluvulla, siirto |

Oikeat työkalut hyväksyvät enemmän kuin minihls, mutta samat periaatteet
pätevät niissäkin. Esimerkiksi Vitis HLS hyväksyy osoittimen
parametrina, mutta tulkitsee sen muistirajapinnaksi tai skalaariksi, ja
silmukan, jonka kierrosmäärä riippuu datasta, mutta raportoi silloin
latenssiksi kysymysmerkin. minihls on tiukempi, ja sen virheilmoitukset
kertovat syyn:

```{.cpp tiedosto="esimerkit/02-rajoitukset/while.cpp"}
```

```{.tuloste tiedosto="esimerkit/02-rajoitukset/odotettu"}
```

Viimeinen virhe on hyödyllinen myös oikeassa työkalussa: indeksi 8
on kahdeksan alkion taulukon ulkopuolella, ja koska indeksi on vakio,
työkalu huomaa sen jo käännösaikana. Muuttuvan indeksin ylitys jää
C-simulaation sanitoijien varaan (luku 10). Laitteistossa ylitys ei
kaadu, vaan lukee tai kirjoittaa jonkin muun osoitteen.

## Jäsennys lyhyesti

minihls:n etupää on tavallinen jäsennin, eikä siinä ole mitään
laitteistolle ominaista. `jasennin.py` pilkkoo lähteen merkeiksi ja
jäsentää ne rekursiivisesti etenevällä jäsentimellä puuksi, jonka
solmut ovat tiedostossa `puu.py`; menetelmät ovat taidon
*Kääntäjätekniikka* aihetta. Laitteiston kannalta jäsentimestä on hyvä
tietää kolme asiaa:

- `#pragma HLS` -rivi välitetään jäsentimelle omana merkkinään, jotta
  pragma voidaan liittää siihen silmukkaan, jonka rungossa se on.
- Yhdistetyt sijoitukset puretaan heti: `s += e` on puussa sama kuin
  `s = s + e`, joten myöhemmät vaiheet käsittelevät yhden sijoituksen
  muodon.
- Silmukan kierrosmäärä lasketaan jo jäsennyksessä. Alkuarvon, rajan ja
  askeleen on oltava vakioita; muuten jäsennin ilmoittaa virheestä.

## Tietovuograafi

Tietovuograafin solmut ovat operaatioita ja kaaret datariippuvuuksia.
Operandi on vakio, alueen aikana muuttumaton signaali (parametri tai
ulomman silmukan laskuri) tai viittaus toiseen solmuun:

```{.python tiedosto="esimerkit/minihls/dfg.py" osa="operandit"}
```

Graafi rakennetaan käymällä puu läpi ja pitämällä kirjaa muuttujien
nykyisistä arvoista. Sijoitus `y = e` ei tuota solmua: se vain sitoo
nimen `y` lausekkeen `e` arvoon. Jos `y` sijoitetaan uudelleen, nimi
sidotaan uuteen arvoon, ja vanha arvo säilyy niillä operaatioilla, jotka
jo käyttivät sitä. Tämä on *SSA-muoto* (*static single assignment*):
jokainen arvo syntyy täsmälleen kerran. Muuttujasta tulee rekisteri
vasta, jos sen arvoa tarvitaan alueen ulkopuolella tai silmukan
seuraavalla kierroksella.

Kirkkauden laskeva ydin näyttää, mitä graafiin päätyy:

```{.cpp tiedosto="esimerkit/02-etupaa/luma.cpp" osa="ydin"}
```

Valitsin `--dfg` tulostaa graafin:

```{.tuloste tiedosto="esimerkit/02-etupaa/odotettu"}
```

Sama graafi kuvana, valitsimen `--dot` tuottamana ja jo ajoitettuna
kellojaksoille (ajoitus on luvun 3 aihe):

```{.dot tiedosto="esimerkit/kaaviot/luma-lohko1.dot" otsikko="Kirkkausytimen tietovuograafi. Kolme kertolaskua eivät riipu toisistaan; summat ja valinnat muodostavat ketjun niiden perään."}
```

Muuttujaa `y` ei näy: sen kolme arvoa ovat solmut `t5`, `t8` ja `t11`.
Ehtolauseet ovat muuttuneet valinnoiksi (`?:`), jotka ovat laitteistossa
multipleksereitä. Graafista näkyy myös rinnakkaisuus: kolme kertolaskua
eivät riipu toisistaan, joten ne voidaan laskea yhtä aikaa.

## Optimoinnit rakennettaessa

Graafia rakentava funktio `op` tekee kolme optimointia jokaiselle
binäärioperaatiolle:

```{.python tiedosto="esimerkit/minihls/dfg.py" osa="op"}
```

- **Vakioiden laskostus** (*constant folding*): jos molemmat operandit
  ovat vakioita, tulos lasketaan heti. Avatuissa silmukoissa indeksit
  muuttuvat vakioiksi, ja laskostus poistaa niiden osoitelaskut.
- **Yksinkertaistus ja voimakkuuden vähennys** (*strength reduction*):
  `x + 0` on `x`, ja kertolasku kahden potenssilla on siirto, joka
  laitteistossa on pelkkää johdotusta. Siksi `77 * r` on kertolasku
  mutta `64 * r` ei olisi.
- **Yhteisten alilausekkeiden poisto** (*common subexpression
  elimination*): sama operaatio samoilla operandeilla tuottaa saman
  solmun. Muistista lukemiselle tehdään sama, kunnes samaan taulukkoon
  kirjoitetaan.

Oikeat työkalut tekevät lisäksi vakiokertolaskun muuttamisen siirroiksi
ja yhteenlaskuiksi (`77 * r = 64r + 8r + 4r + r`), bittileveyksien
pienentämisen arvoalueiden perusteella ja kymmeniä muita LLVM:n
optimointeja ennen kuin ajoitus alkaa.

## Ehtolauseet valinnoiksi

Laitteistossa ei ole hyppyjä: molemmat haarat ovat olemassa ja laskevat
koko ajan. Siksi ehtolause muutetaan *if-conversion*-muunnoksella.
Molemmat haarat käsitellään, ja haaran jälkeen jokaisen muuttuneen
muuttujan arvo valitaan ehdon mukaan. Muistiin tallentaminen ei voi
olla valinta, joten tallennus saa *predikaatin*, ehdon, jonka on oltava
tosi, jotta kirjoitus tehdään:

```{.python tiedosto="esimerkit/minihls/dfg.py" osa="jos"}
```

If-conversion tekee haaroista rinnakkaisia, mikä on nopeaa, jos haarat
ovat lyhyitä. Jos toisessa haarassa on paljon laskentaa, molempien
haarojen logiikka on silti olemassa. Siksi laitteistoa ajatteleva
suunnittelija välttää raskaita haaroja tai siirtää ne omaan alueeseensa.

## Käytännössä

- **Kirjoita kiinteän kokoista koodia.** Taulukkojen koot ja silmukoiden
  rajat vakioina; `#define` tai `constexpr` tekee niistä myös
  testipenkissä samat.
- **Erota ydin ja testipenkki.** Ytimessä ei tulosteta eikä lueta
  tiedostoja. Testipenkki saa käyttää koko standardikirjastoa.
- **Lue työkalun varoitukset.** Kun oikea työkalu ei ymmärrä
  rakennetta, se ilmoittaa usein vain varoituksen ja tuottaa jotain
  muuta kuin odotit, esimerkiksi muistirajapinnan osoittimesta.
- **Muuttuja ei ole rekisteri.** C++:n muuttuja on nimi arvolle. Siitä
  tulee rekisteri vain, jos arvo on säilytettävä jaksosta toiseen.
- **Ehtolauseen hinta on molempien haarojen logiikka**, ei hyppy kuten
  ohjelmistossa.

## Itsearviointi

- Osaat kertoa, miksi dynaaminen muisti, rekursio ja osoittimet eivät
  sovi syntetisoitavaan koodiin, ja miten ne korvataan.
- Osaat piirtää lyhyen lausekesarjan tietovuograafin ja tunnistaa
  siitä rinnakkain laskettavat operaatiot.
- Osaat selittää SSA-muodon ja sen, milloin muuttujasta tulee rekisteri.
- Osaat kertoa, mitä vakioiden laskostus, voimakkuuden vähennys ja
  yhteisten alilausekkeiden poisto tekevät laitteistolle.
- Osaat selittää if-conversion-muunnoksen ja predikaatin merkityksen
  muistiin kirjoittamisessa.
