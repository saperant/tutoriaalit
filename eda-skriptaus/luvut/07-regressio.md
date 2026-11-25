# Regressioajot

Regressio ajaa koko testijoukon, tyypillisesti öisin tai ennen
yhdistämistä päähaaraan, ja kertoo, rikkoiko jokin muutos jotain, mikä
toimi ennen. Satunnaistetuissa testeissä sama testi ajetaan monella
*siemenellä*, koska jokainen siemen tuottaa eri ärsykkeet. Vika voi
näkyä vain osalla siemenistä. Suuressa projektissa regressiossa on
tuhansia ajoja, ja niiden tuloksista on saatava nopeasti selville,
montako eri vikaa on ja mitkä ajot toistavat ne.

Työnjako taidon *Laitteiston verifiointi* kanssa on tämä: siellä
käsitellään, mitä regressiossa ajetaan ja miksi (testisuunnitelma,
ärsykkeet, kattavuusmalli). Tässä luvussa ja seuraavassa käsitellään,
miten ajot ajetaan, ryhmitellään ja tallennetaan.

## Testilista

Testit kuvataan tiedostossa, ei koodissa:

```{.toml tiedosto="esimerkit/asetukset/regressio.toml"}
```

Jokaisella testillä on nimi, siemenet (luettelona tai määränä),
testipenkin parametrit, makrot ja aikaraja. `alu_vika` kääntää ALU:n
makrolla `VIKA`, joka lisää tarkoituksellisen virheen XOR-operaatioon.
Virhe näkyy vain, kun kummankin operandin ylin bitti on yksi. `alu_jumi`
testaa aikakatkaisun käsittelyä. Lista luetaan `Testi`-
tietueiksi, ja päällekkäiset nimet ovat virhe, koska tulokset
tunnistetaan nimestä.

## Käännä kerran, aja monesti

Testipenkki käännetään kerran kutakin makroyhdistelmää kohden. Kaikki
siemenet ajavat samaa ohjelmaa ja eroavat vain plusargumenteista:

```{.python tiedosto="esimerkit/vuo/regressio.py" osa="kaanna"}
```

Tämä on regressioiden tärkein yksittäinen nopeutus. Verilatorin
käännös kestää sekunteja tai minuutteja, ja pieni simulointi
millisekunteja. Jos jokainen ajo kääntäisi itse, regressio kuluttaisi
suurimman osan ajastaan kääntäjässä.

## Rinnakkaiset ajot

```{.python tiedosto="esimerkit/vuo/regressio.py" osa="regressio"}
```

Käännökset ajetaan ensin rinnakkain, sitten kaikki ajot. Jokainen ajo
kirjoittaa oman lokinsa, jonka nimessä ovat testi ja siemen, joten
yhtään tulosta ei tarvitse etsiä yhteisestä lokista. Tulokset
järjestetään lopuksi testin ja siemenen mukaan: valmistumisjärjestys
riippuu koneen kuormasta, mutta raportin järjestyksen ei pidä riippua.

Säiepooli riittää, koska jokainen ajo on oma prosessinsa. Yhden koneen
ytimet loppuvat kuitenkin nopeasti. Suuret regressiot ajetaan
laskentaklusterissa työjonon kautta (esimerkiksi Slurm tai LSF), ja
`aja_yksi` lähettää ajon jonoon sen sijaan, että käynnistäisi
prosessin itse. Muu koodi pysyy samana: testilista, lokit, jäsentäminen
ja allekirjoitukset eivät riipu siitä, missä ajo tapahtui.

## Siemenet ja toistettavuus

Testipenkki käyttää omaa satunnaislukugeneraattoriaan (xorshift), jonka
tila alustetaan plusargumentilla `+siemen=N`:

```{.systemverilog tiedosto="esimerkit/tb/alu_tb.sv" osa="siemen"}
```

Ajo riippuu siksi vain siemenestä, ei simulaattorista eikä sen
versiosta. Nolla on xorshiftin kiintopiste, josta tila ei koskaan
muutu, joten se korvataan ykkösellä. Toistettavuus on
regression perusvaatimus. Hylätty ajo toistetaan samalla siemenellä
kehittäjän koneella, ja lokin ensimmäinen rivi kertoo täsmälleen,
millä komennolla.

SystemVerilogin `$urandom` ja luokkien satunnaistus ovat myös
toistettavia samalla siemenellä, mutta vain saman simulaattorin
samassa versiossa. Simulaattorin päivitys voi muuttaa jokaisen ajon
ärsykkeet. Siksi siemenen lisäksi tallennetaan simulaattorin versio,
ja kriittiset viat kirjataan suunnattuina testeinä, jotka eivät riipu
satunnaisuudesta.

## Virheallekirjoitukset

Kun 7 ajoa 12:sta epäonnistuu, kehittäjä haluaa tietää, onko kyseessä
yksi vika vai seitsemän. Virheviestistä tehdään *allekirjoitus*
(*failure signature*; taidossa *Laitteiston verifiointi* samaa
kutsutaan virheen tunnisteeksi), jossa ajosta toiseen vaihtelevat
arvot on korvattu merkinnällä:

```{.python tiedosto="esimerkit/vuo/regressio.py" osa="allekirjoitus"}
```

Normalisointi on tasapainoilua. Jos mitään ei korvata, jokainen ajo on
oma ryhmänsä. Jos kaikki numerot korvataan, eri viat sulautuvat yhteen.
Tässä säilytetään operaatio, koska se kertoo, missä ALU:n osassa vika
on. Data-arvot korvataan, koska ne riippuvat vain siemenestä. Oikeissa
lokeissa normalisoidaan lisäksi simulointiajat, polut, osoitteet ja
heksadesimaaliluvut.

```{.python tiedosto="esimerkit/07-regressio.py" osa="tulokset"}
```

Lopuksi yhdistetään läpäisseen testin kattavuus kaikilta siemeniltä:

```{.python tiedosto="esimerkit/07-regressio.py" osa="kattavuus"}
```

```{.tuloste tiedosto="esimerkit/07-regressio.odotettu"}
```

Seitsemän hylättyä ajoa ovat yksi vika, ja se on XOR-operaatiossa
(`op=3`). Jumi on oma ryhmänsä. Neljä siementä riittää kattamaan kaikki
16 lokeroa, ja harvimmin osuttua lokeroa on ajettu 40 kertaa.
Kattavuuden yhdistäminen kertoo, milloin uusia siemeniä ei enää
tarvita: kun kaikki lokerot on katettu riittävän monta kertaa, lisäajot
eivät tuo uutta tietoa ilman uusia ärsykemalleja.

## Käytännössä

- **Testilista tiedostossa.** Testejä lisätään muokkaamatta
  regressiokoodia, ja listan muutokset näkyvät versionhallinnassa.
- **Käännös kerran.** Ajot jakavat käännöksen. Käännöksen
  epäonnistuminen on oma virheensä, joka pysäyttää regression heti.
- **Loki jokaiselle ajolle.** Nimessä testi ja siemen, ensimmäisellä
  rivillä komento.
- **Ryhmittele ennen kuin luet.** Kehittäjä lukee ryhmän ensimmäisen
  lokin, ei jokaista. Ryhmän koko kertoo vian yleisyyden.
- **Aikakatkaisu on oma tilansa.** Se kertoo jumista tai liian
  pienestä aikarajasta, ei väärästä tuloksesta.

## Itsearviointi

- Osaat kuvata regression testilistana ja ajaa sen rinnakkain niin,
  että jokainen makroyhdistelmä käännetään vain kerran.
- Osaat selittää, miksi satunnaistettu testi on toistettava ja mitä
  siemenen lisäksi on tallennettava.
- Osaat muodostaa virheallekirjoitukset ja perustella, mitkä arvot
  normalisoidaan.
- Osaat yhdistää kattavuuden useasta ajosta ja tulkita tuloksen.
