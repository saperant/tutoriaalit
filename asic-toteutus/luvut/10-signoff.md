# Sign-off

Ennen tapeoutia piiri tarkistetaan kerralla kaikilta osin. Sign-off-
työkalut ovat tarkempia ja hitaampia kuin toteutusvaiheen arviot, ja
niiden tulos on ehdoton: valmistaja ei hyväksy piiriä, joka rikkoo
sääntöjä, eikä fysiikka armahda ajoitusrikettä.

| Tarkistus | Kysymys |
|-----------|---------|
| STA | Täyttyvätkö ajoitusehdot kaikissa kulmissa mitatuilla johtimilla? |
| DRC | Noudattaako piirikuvio valmistajan geometriasääntöjä? |
| LVS | Vastaako piirikuvio netlistaa? |
| Antenni | Kestävätkö hilat valmistuksen aikana kertyvän varauksen? |
| IR-pudotus | Riittääkö syöttöjännite joka paikassa? |
| EM | Kestävätkö johtimet virrantiheyden koko käyttöiän? |

## Parasiittien poiminta

Luvun 4 analyysi arvioi johtimen kuorman haarautumasta, koska
johdinta ei vielä ollut. Reitityksen jälkeen jokainen johdin on joukko
suorakulmioita tunnetuilla kerroksilla, ja sen vastus ja kapasitanssi
voidaan laskea geometriasta. Tätä kutsutaan parasiittien poiminnaksi
(parasitic extraction):

- **Vastus** on kerroksen neliövastus kertaa pituuden ja leveyden
  suhde, ja jokainen läpivienti lisää oman vastuksensa. Alimmat
  kerrokset ovat ohuita ja resistiivisiä, ylimmät paksuja.
- **Kapasitanssi** syntyy johtimen pohjasta ja katosta ala- ja
  yläpuolisiin kerroksiin, reunoista sekä viereisistä johtimista.
  Pienissä prosesseissa naapureiden osuus on suurin, ja se on myös
  ylikuulumisen lähde (luku 8).

```{.python tiedosto="esimerkit/10-parasiitit.py" osa="kerrokset"}
```

```{.python tiedosto="esimerkit/10-parasiitit.py" osa="pala"}
```

Viive nieluille lasketaan Elmore-mallilla kuten kellopuussa: jokaisen
palan vastus kertaa kaikki sen takana oleva kapasitanssi.

```{.python tiedosto="esimerkit/10-parasiitit.py" osa="elmore"}
```

```{.python tiedosto="esimerkit/10-parasiitit.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/10-parasiitit.odotettu"}
```

Puolen millimetrin johdin on 48 fF, kun haarautumaan perustuva arvio
antoi 3 fF: arvio ei tiedä pituutta, ja pitkä johdin on kuormana
kuin 24 portin tulot. Heikolla ajurilla viive on 0,3 ns eli luvun 4
kertojan kolmen portin verran, ja lähes kaikki siitä on ajurin
vastusta eikä johtimen: korjaus on vahvempi ajuri tai puskuri, ei
leveämpi johdin. Viidesosa kapasitanssista on kytkentää yhteen
naapuriin.

Tulos kirjoitetaan SPEF-tiedostoon (Standard Parasitic Exchange
Format, IEEE 1481), jossa jokaisella johtimella on kapasitanssit
solmuittain ja vastukset solmujen välillä. Sign-off-STA lukee sen
netlistan rinnalle ja laskee viiveet tästä RC-verkosta arvion sijaan.
Poiminta tehdään erikseen jokaisessa johdinkulmassa, koska
metallin paksuus ja eristeiden mitat vaihtelevat valmistuksessa kuten
transistoritkin.

## DRC ja antennisääntö

Valmistajan sääntökirja sisältää satoja sääntöjä: vähimmäisleveydet,
-etäisyydet, läpivientien reunukset, metallin tiheys ja paljon muuta.
Säännöt ovat geometriaa suorakulmioilla:

```{.python tiedosto="esimerkit/10-drc.py" osa="kuvio"}
```

```{.python tiedosto="esimerkit/10-drc.py" osa="tarkistus"}
```

Antennisääntö on prosessin sivuvaikutus. Metallikerros kuvioidaan
plasmaetsauksella, ja sen aikana metalli kerää varausta. Jos pitkä
johdin on kytketty vain transistorin hilaan, eikä ylempi kerros vielä
yhdistä sitä ajurin diffuusioon, varaus purkautuu ohuen hilaoksidin
(luku 2) läpi ja rikkoo sen. Sääntö rajoittaa metallin ja hilan
pinta-alojen suhdetta; korjaus on diodi tai hyppy ylemmälle
kerrokselle lähellä hilaa.

![Antennisääntö periaatepiirroksena. Vasemmalla metalli 1 on jo tehty
mutta metalli 2 ei: pitkä johdin on kiinni vain hilassa. Oikealla
johdin kulkee metalli 2:lla, jolloin hilaan kytketty metalli 1 jää
lyhyeksi, ja valmis johdin yhdistyy samalla
diffuusioon.](kuvat/antenni.png){width=95%}

```{.python tiedosto="esimerkit/10-drc.py" osa="antenni"}
```

```{.python tiedosto="esimerkit/10-drc.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/10-drc.odotettu"}
```

![Tarkistettu kuvio ja sen kolme rikettä: johtimien A ja B väli,
johtimen C leveys ja läpiviennin E reunus johtimessa
D.](kuvat/drc.png){width=88%}

LVS (layout versus schematic) poimii piirikuviosta transistorit ja
niiden kytkennät ja vertaa niitä netlistaan graafien
isomorfiana. Tyypillisiä LVS-virheitä ovat oikosulut (kaksi
nimettyä signaalia samaa metallia) ja katkokset.

## IR-pudotus ja sähkömigraatio

Tehoverkko on vastusverkko. Kun solut ottavat virtaa, jännite laskee
kauempana syöttönastoista, ja solut hidastuvat tai lakkaavat
toimimasta. Pudotus lasketaan ratkaisemalla verkon solmujännitteet:

```{.python tiedosto="esimerkit/10-ir.py" osa="ratkaisu"}
```

```{.python tiedosto="esimerkit/10-ir.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-ir.odotettu"}
```

![Jännitteen pudotus ytimen alueella kolmella tehoverkolla. Siniset
neliöt ovat syöttönastat. Pudotus on suurin kauimpana
nastoista.](kuvat/ir.png){width=95%}

Neljä kulmanastaa ei riitä: keskellä jännite on 5,7 % matalampi, ja
ajoitusanalyysin kirjasto oletti täyden jännitteen. Syöttörengas ja
leveämmät liuskat pudottavat häviön alle prosenttiin. Flip-chip-
koteloinnissa syöttö tulee koko piirin pinnalta, mikä pienentää
pudotusta entisestään (luku 11).

Sähkömigraatio (electromigration, EM) on pitkän aikavälin vika:
suuri virrantiheys siirtää metalliatomeja, ja johtimeen syntyy
vuosien käytössä katkos tai oikosulku. Valmistaja antaa suurimman
virrantiheyden kerroksittain ja lämpötilan mukaan; tehoverkon ja
kellopuun johtimet mitoitetaan sen mukaan.

## ECO

Sign-offin löytämät viimeiset rikkeet korjataan muuttamalla netlistaa
ja piirikuviota paikallisesti (engineering change order, ECO):
lisätään puskuri, vaihdetaan solun koko tai siirretään johdin. Myös
myöhäiset toiminnalliset korjaukset tehdään ECO:na, usein varalle
sijoitettujen solujen (spare cells) avulla, jotta vain muutama
metallimaski vaihtuu.

## Käytännössä

- **Sign-off ei ole viimeinen viikko.** DRC-, IR- ja ajoitus-
  ongelmat ratkaistaan pohjapiirroksessa; sign-off vain vahvistaa.
- **Puhdas on ainoa hyväksyttävä tila.** Jokainen DRC- ja LVS-poikkeus
  vaatii valmistajan kirjallisen hyväksynnän (waiver).
- **IR-pudotus ajoitukseen.** Dynaaminen IR-pudotus hidastaa soluja
  juuri silloin, kun niitä eniten tarvitaan; nykyaikainen STA
  huomioi jännitepudotuksen solukohtaisesti.
- **Avoimet työkalut.** Magic ja KLayout tekevät DRC:n ja LVS:n
  (Netgen) avoimille PDK:ille, ja OpenROAD poimii parasiitit (OpenRCX)
  ja analysoi IR-pudotuksen.

## Itsearviointi

- Osaat luetella sign-off-tarkistukset ja niiden tarkoituksen.
- Osaat laskea johdinpalan vastuksen ja kapasitanssin geometriasta,
  kertoa SPEF-tiedoston tehtävän ja perustella, miksi haarautumaan
  perustuva arvio pettää pitkillä johtimilla.
- Osaat tarkistaa suunnittelusääntöjä geometrisesti ja selittää
  antennisäännön syyn ja korjauksen.
- Osaat mallintaa tehoverkon vastusverkkona ja arvioida syöttönastojen
  ja liuskojen vaikutuksen IR-pudotukseen.
- Osaat kertoa, mitä ECO tarkoittaa ja miksi varasoluja käytetään.
