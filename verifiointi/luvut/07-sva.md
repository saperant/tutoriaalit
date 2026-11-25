# SystemVerilogin väitteet

Tulostaulu tarkistaa lohkon käytöksen liitännästä käsin ja vain siinä
testipenkissä, johon se on kirjoitettu. *Väite* (assertion) on
suunnitelman sisään tai viereen kirjoitettu sääntö, joka tarkistetaan
jokaisella jaksolla kaikissa simulaatioissa, joissa lohko on mukana:
lohkotestissä, järjestelmätestissä ja formaalissa tarkistuksessa.
SystemVerilogin väitekieli (SystemVerilog Assertions, SVA) on osa
IEEE 1800 -standardia.

## Välittömät ja samanaikaiset väitteet

SystemVerilogissa on kaksi väitelajia:

| Laji | Kirjoitetaan | Tarkistetaan | Esimerkki |
|------|--------------|--------------|-----------|
| välitön (immediate) | proseduurin sisään | kun lause suoritetaan | `assert (maara <= 4);` |
| samanaikainen (concurrent) | moduulin tasolle | kellon reunalla näytteistetyistä arvoista | `assert property (@(posedge clk) a \|=> b);` |

Välitön väite on kuin ohjelmointikielen `assert`. Samanaikainen väite
on aikalogiikan lauseke: se näytteistää signaalit kellon reunalla,
kuten rekisteri, ja voi puhua useista peräkkäisistä jaksoista.
Näytteistys tekee siitä kilpatilanteista vapaan, joten se on
suositeltu muoto RTL:n väitteille.

## Ominaisuudet

Samanaikaisen väitteen runko on *ominaisuus* (property). Tärkeimmät
rakenteet ovat:

| Rakenne | Merkitys |
|---------|----------|
| `@(posedge clk)` | näytteistyskello |
| `disable iff (rst)` | väite ei ole voimassa nollauksen aikana |
| `a \|-> b` | jos `a`, niin `b` samalla jaksolla |
| `a \|=> b` | jos `a`, niin `b` seuraavalla jaksolla |
| `$past(x)` | `x`:n arvo edellisellä jaksolla |
| `$rose(x)`, `$fell(x)` | `x` nousi tai laski tällä jaksolla |
| `$stable(x)` | `x` on sama kuin edellisellä jaksolla |
| `$onehot(x)`, `$onehot0(x)` | tasan yksi tai korkeintaan yksi bitti ykkönen |
| `a ##1 b` | sekvenssi: `a`, ja jaksoa myöhemmin `b` |
| `a ##[1:3] b` | `b` 1–3 jaksoa `a`:n jälkeen |
| `b[*3]` | `b` kolmella peräkkäisellä jaksolla |

Kuvassa näkyy implikaatioiden ero. Kumpikin väite tarkistetaan
jokaisella nousevalla reunalla, ja kahdella alimmalla rivillä näkyy,
millä jaksoilla väite todella tarkistaa jotain (muualla esiehto ei
toteudu, ja väite on tyhjästi tosi): rivi `samalla` kuvaa `|->`-väitettä
ja rivi `seuraavalla` `|=>`-väitettä. Jakson 2 esiehto `a` velvoittaa
`|->`-väitteessä `b`:n samalla jaksolla 2 ja `|=>`-väitteessä
seuraavalla jaksolla 3. Jakso 5 täyttää `|->`-väitteen mutta rikkoo
`|=>`-väitteen, koska `b` on alhaalla jaksolla 6.

```{.ajoituskaavio otsikko="Implikaatiot `a |-> b` ja `a |=> b`: esiehto ja sen velvoittama jakso"}
{"signal": [
  {"name": "clk", "wave": "P.......", "period": 1},
  {"name": "jakso", "wave": "========", "data": ["0", "1", "2", "3", "4", "5", "6", "7"]},
  {"name": "a", "wave": "0.10.10."},
  {"name": "b", "wave": "0.1.010."},
  {},
  {"name": "samalla", "wave": "z.3z.3z.", "data": ["OK", "OK"]},
  {"name": "seuraavalla", "wave": "z..3z.5z", "data": ["OK", "VIRHE"]}
]}
```

Implikaation vasen puoli on *esiehto* (antecedent). Kun esiehto ei
toteudu, ominaisuus on tyhjästi tosi (vacuous). Väite, jonka esiehto
ei toteudu koskaan, ei siis koskaan epäonnistu, mutta ei myöskään
tarkista mitään. Siksi jokaiselle tärkeälle esiehdolle kirjoitetaan
kattavuuskohde `cover property`.

## FIFOn väitteet

FIFOn väitteet ovat omassa moduulissaan, joka liitetään FIFOon
`bind`-lauseella. Lause instansioi väitemoduulin jokaisen
`fifo`-instanssin sisälle ja kytkee sen portit samannimisiin
signaaleihin (`.*`). FIFOn lähdettä ei tarvitse muuttaa, ja samat
väitteet voi liittää myös lohkoon, jonka lähdettä ei saa muuttaa,
kuten ostettuun IP:hen.

```{.systemverilog tiedosto="esimerkit/07-sva/fifo_sva.sv" osa="sva"}
```

Väitteillä on nimet (`a_liput`, `a_raja`), jotka näkyvät
virheilmoituksessa ja kattavuusraportissa. Toimintolohko `else
$error(...)` kertoo, mitä tapahtui; ilman sitä simulaattori ilmoittaa
vain väitteen nimen.

Testipenkissä ei ole tulostaulua eikä mallia. Se syöttää FIFOlle
satunnaisia toimenpiteitä, ja väitteet tekevät kaiken tarkistamisen:

```{.systemverilog tiedosto="esimerkit/07-sva/testipenkki.sv"}
```

Verilator tarkistaa väitteet, kun se ajetaan valitsimella `--assert`.
Ehjä FIFO läpäisee 2000 jaksoa:

```{.tuloste tiedosto="esimerkit/odotetut/sva.odotettu"}
```

Jokainen istutettu vika rikkoo eri väitteen. Alivuoto näkyy rajana:

```{.tuloste tiedosto="esimerkit/odotetut/sva-tyhja.odotettu"}
```

Samanaikainen kirjoitus ja luku muuttaa määrää:

```{.tuloste tiedosto="esimerkit/odotetut/sva-samanaikainen.odotettu"}
```

Liput eivät vastaa määrää:

```{.tuloste tiedosto="esimerkit/odotetut/sva-taysi.odotettu"}
```

Väitteet löysivät viat ilman referenssimallia, ja virheilmoitus
osoittaa suoraan rikotun säännön ja sen jakson, jolla vika näkyi
ensimmäisen kerran. Tulostaulu olisi ilmoittanut saman vian
myöhemmin ja epäsuorasti, esimerkiksi väärinä luettuina arvoina.
Väitteet eivät kuitenkaan korvaa tulostaulua: datan eheyttä ja
järjestystä on vaikea ilmaista paikallisina sääntöinä.

## Verilatorin tuki

Verilator 5.020 tukee väitekielestä osaa. Esimerkkien väitteet on
kirjoitettu tuetulla osajoukolla:

| Tuettu | Ei tuettu |
|--------|-----------|
| `assert`, `assume` ja `cover property` | `sequence`-määrittelyt |
| `property`-määrittelyt argumentteineen | viive `##n` ja väli `##[m:n]` |
| `\|->` ja `\|=>` | toistot `[*n]`, `[->n]`, `[=n]` |
| `disable iff` | sekvenssioperaattorit `and`, `or`, `intersect`, `throughout`, `within` |
| `$past`, `$rose`, `$fell`, `$stable`, `$onehot`, `$onehot0` | |
| välittömät väitteet | |

Ei-tuettu rakenne on käännösvirhe, ei hiljainen ohitus, joten
rajoitus ei piilota mitään:

```{.systemverilog tiedosto="esimerkit/07-sva/ei_tuettu.sv"}
```

```{.tuloste tiedosto="esimerkit/odotetut/sva-ei-tuettu.odotettu"}
```

Monijaksoiset säännöt voi kirjoittaa tuetulla osajoukolla
*apulogiikan* avulla. Sääntö "kuittaus tulee 1–3 jakson kuluessa
pyynnöstä" muuttuu laskuriksi, joka kasvaa, kun pyyntö odottaa, ja
väitteeksi, että laskuri ei ylitä kolmea. Luvun 8 arbiterin
reiluusominaisuus on kirjoitettu juuri näin. Apulogiikka on usein
selkeämpää kuin pitkä sekvenssi, ja se toimii kaikissa työkaluissa.
Kaupallisilla simulaattoreilla ja formaaleilla työkaluilla koko
väitekieli on käytettävissä.

## Väitteet suunnitelmassa ja testipenkissä

Väitteitä kirjoittavat sekä suunnittelija että verifioija, mutta eri
tarkoituksiin:

- **Suunnittelijan väitteet** ovat RTL:n sisällä ja dokumentoivat
  oletuksia: "tämä tilakone ei koskaan ole tilassa X, kun Y",
  "osoitin ei ylitä syvyyttä". Ne ovat valkoisen laatikon
  tarkistuksia ja löytävät vian lähellä syytä.
- **Verifioijan väitteet** ovat liitännän sääntöjä, kuten
  kättelyprotokolla. Ne kirjoitetaan erilliseen moduuliin ja
  liitetään `bind`-lauseella jokaiseen liitännän ilmentymään.
  Taidon *SoC-integraatio* AXI-tarkistin on tällainen.

Synteesityökalut jättävät väitteet huomiotta, joten ne eivät maksa
piirissä mitään. Ne voi myös suojata `ifdef`-lohkoon, jos jokin
työkalu ei ymmärrä niitä.

## Käytännössä

- **Väite jokaisesta oletuksesta.** Jos suunnittelija ajattelee "tätä
  ei voi tapahtua", sen voi kirjoittaa väitteeksi samassa ajassa kuin
  kommentin. Kommentti ei tarkista mitään.
- **Nimet ja viestit.** Nimetty väite viestillä, joka kertoo arvot,
  säästää vianetsinnässä enemmän aikaa kuin sen kirjoittaminen vie.
- **Jokaiselle esiehdolle kattavuus.** Tyhjästi tosi väite on
  yleisin väitteiden sudenkuoppa; `cover property` samasta
  esiehdosta paljastaa sen.
- **`disable iff` nollaukselle.** Ilman sitä väite voi epäonnistua
  nollauksen aikana tai heti sen jälkeen, kun `$past` katsoo
  nollausta edeltävää tilaa.
- **Protokollatarkistimet uudelleenkäyttöön.** Liitännän säännöt
  kirjoitetaan kerran, liitetään `bind`-lauseella kaikkialle ja
  testataan negatiivisella testillä, jossa sääntöä rikotaan
  tarkoituksella.
- **Työkalun osajoukko tiedoksi.** Kun testit ajetaan usealla
  simulaattorilla, väitteet kirjoitetaan niiden yhteisellä
  osajoukolla tai apulogiikalla.

## Itsearviointi

- Osaat erottaa välittömän ja samanaikaisen väitteen ja valita niistä.
- Osaat kirjoittaa ominaisuuden implikaatioilla `|->` ja `|=>` sekä
  funktioilla `$past`, `$stable` ja `$onehot0`.
- Osaat liittää väitemoduulin lohkoon `bind`-lauseella muuttamatta
  lohkon lähdettä.
- Osaat selittää tyhjästi toden väitteen ja estää sen kattavuuskohteella.
- Osaat kirjoittaa monijaksoisen säännön apulogiikalla, kun
  työkalu ei tue sekvenssejä.
