# Moduulit ja hierarkia

Moduuli on SystemVerilogin rakennuspalikka: sillä on nimi, parametrit,
portit ja sisältö. Suuri suunnitelma on moduulien hierarkia, jossa
ylempi moduuli kytkee alempien *instanssit* yhteen. Hierarkia on sama
kuin piirikaaviossa: jokainen instanssi on oma laatikkonsa, jonka
portit on kytketty johtimilla.

## Portit

Portit esitellään moduulin otsikossa niin sanotulla ANSI-tyylillä:
suunta, tyyppi, leveys ja nimi samalla rivillä.

| Suunta | Merkitys |
|--------|----------|
| `input` | moduuli lukee; ajaja on moduulin ulkopuolella |
| `output` | moduuli ajaa; ulkopuoli lukee |
| `inout` | kaksisuuntainen, vain piirin ulkoisille nastoille |

Porttien tyyppi on lähes aina `logic`. Leveys kirjoitetaan muodossa
`[ylin:alin]`, ja käytäntö on, että alin bitti on 0. Moduulin sisällä
ei voi ajaa `input`-porttia, ja jokaista `output`-porttia on ajettava
täsmälleen yhdestä paikasta.

Täysisummain on yhden bitin summain, josta suuremmat rakennetaan:

```{.systemverilog tiedosto="esimerkit/02-summain/taysisummain.sv"}
```

`assign` on *jatkuva sijoitus*: se kuvaa johtimen, jota oikean puolen
lauseke ajaa koko ajan. Synteesi tekee lausekkeista portteja.

## Instanssit ja kytkennät

Instanssi luodaan kirjoittamalla moduulin nimi, mahdolliset parametrit,
instanssin nimi ja kytkennät. Kytkennät kirjoitetaan nimettyinä:
`.portti(signaali)`. Jos portti ja signaali ovat samannimisiä, riittää
`.portti`. Paikkasidonnaista kytkentää (`taysisummain u (x, y, z, ...)`)
ei kannata käyttää: porttien järjestyksen muutos kytkee hiljaa väärät
signaalit.

## Parametrit ja generate

Parametri on käännösaikainen vakio, jonka ylempi taso voi asettaa
instanssikohtaisesti. Sillä tehdään yleiskäyttöisiä moduuleja:
leveydet, syvyydet ja ajoitusvakiot. `localparam` on johdettu vakio,
jota ylempi taso ei voi muuttaa.

Toistuva rakenne tehdään `generate`-silmukalla. Silmukka avautuu
käännöksessä: jokainen kierros luo oman laitteistonsa, ja `genvar` on
käännösaikainen indeksi. Nimetty lohko (`begin : g_bitti`) antaa
instansseille hierarkkiset nimet `g_bitti[0].u_ts`, `g_bitti[1].u_ts`
ja niin edelleen. Seuraava summain kytkee N täysisummainta ketjuksi
(ripple-carry):

```{.systemverilog tiedosto="esimerkit/02-summain/summain.sv"}
```

Muistibittiketju `muisti` on yhtä bittiä leveämpi kuin summa, jotta
sekä sisään tuleva että ulos lähtevä muistibitti mahtuvat samaan
vektoriin.

Testipenkki kokeilee kaikki 512 syöteyhdistelmää ja vertaa tulosta
malliin, joka laskee saman asian SystemVerilogin `+`-operaattorilla:

```{.systemverilog tiedosto="esimerkit/02-summain/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/02-summain.odotettu"}
```

Kattava testaus on mahdollista vain pienillä syöteavaruuksilla. Siksi
testipenkki käyttää parametria `N = 4`, vaikka moduulin oletusleveys
on 8: parametroitu moduuli testataan pienellä koolla ja käytetään
suuremmalla. Tässä esimerkissä testipenkki on omassa tiedostossaan.
Käännöskomennossa luetellaan kaikki tiedostot, ja `--top-module`
valitsee ylimmän tason.

## Leveydet porttikytkennöissä

Verilog salli alun perin kytkeä eri levyisen signaalin porttiin: liian
leveä signaali katkaistiin ja liian kapea täytettiin nollilla.
Kirjoitusvirhe leveydessä voi siis mennä huomaamatta läpi. Verilator
varoittaa leveyserosta, ja koska varoitukset ovat virheitä, seuraava ei
käänny:

```{.systemverilog tiedosto="esimerkit/02-leveys.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/02-leveys.odotettu"}
```

## Käytännössä

- **Yksi moduuli, yksi tiedosto, sama nimi.** Tuotantokoodissa
  moduuli `uart_tx` on tiedostossa `uart_tx.sv`. Työkalut ja ihmiset
  löytävät sen ilman hakua. Tämän tutoriaalin lyhyissä esimerkeissä
  sääntöä rikotaan tarkoituksella.
- **Nimetyt kytkennät aina.** `.portti(signaali)` ja `.portti` ovat
  itsedokumentoivia ja kestävät porttien uudelleenjärjestelyn.
  Jokerikytkentää `.*` kannattaa välttää: se kytkee kaikki
  samannimiset signaalit, myös ne, joita ei tarkoitettu.
- **Nimeämiskäytännöt.** Yleinen tapa on etuliite `u_` instansseille,
  `g_` generate-lohkoille ja jälkiliite `_n` aktiivisille
  nollasignaaleille (`rst_n`). Isot kirjaimet varataan parametreille ja
  vakioille. Johdonmukaisuus on tärkeämpää kuin yksittäinen sääntö.
- **Parametroi vain tarvittava.** Jokainen parametri on uusi
  konfiguraatio, joka pitäisi testata. Leveys ja syvyys ovat
  luonnollisia parametreja, mutta parametri, jota kukaan ei muuta,
  vain monimutkaistaa koodia.
- **Hierarkia ei maksa piirissä mitään.** Synteesi litistää
  hierarkian, eikä moduulirajasta synny laitteistoa. Moduuleihin
  jakaminen on puhtaasti luettavuus-, uudelleenkäyttö- ja
  testattavuuskysymys.
- **Ripple-carry on hidas.** N-bittisen ketjun viive kasvaa lineaarisesti
  bittimäärän mukana. Käytännössä summain kirjoitetaan `a + b`, ja
  synteesityökalu valitsee rakenteen (FPGA:ssa erillinen nopea
  muistibittiketju, ASIC:ssa ajoitusrajoitteiden mukaan).

## Itsearviointi

- Osaat kirjoittaa moduulin ANSI-tyylisillä porteilla ja parametreilla.
- Osaat luoda instanssin nimetyillä kytkennöillä ja asettaa sen
  parametrit.
- Osaat toistaa rakenteen `generate`-silmukalla ja nimetä lohkon.
- Osaat selittää, miksi leveysero porttikytkennässä on vaarallinen ja
  miten lint löytää sen.
- Osaat kirjoittaa testipenkin, joka käy pienen moduulin kaikki syötteet
  läpi ja vertaa tulosta malliin.
