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

## DRC ja antennisääntö

Valmistajan sääntökirja sisältää satoja sääntöjä: vähimmäisleveydet,
-etäisyydet, läpivientien reunukset, metallin tiheys ja paljon muuta.
Säännöt ovat geometriaa suorakulmioilla:

```{.python tiedosto="esimerkit/10-drc.py" osa="kuvio"}
```

```{.python tiedosto="esimerkit/10-drc.py" osa="tarkistus"}
```

Antennisääntö on prosessin sivuvaikutus. Plasmaetsauksen aikana
metalli kerää varausta. Jos pitkä johdin on kytketty vain transistorin
hilaan, eikä ylempi kerros vielä yhdistä sitä diffuusioon, varaus
purkautuu ohuen hilaoksidin läpi ja rikkoo sen. Sääntö rajoittaa
metallin ja hilan pinta-alojen suhdetta; korjaus on diodi tai
hyppy ylemmälle kerrokselle lähellä hilaa.

```{.python tiedosto="esimerkit/10-drc.py" osa="antenni"}
```

```{.python tiedosto="esimerkit/10-drc.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/10-drc.odotettu"}
```

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
  (Netgen) avoimille PDK:ille, ja OpenROAD analysoi IR-pudotuksen.

## Itsearviointi

- Osaat luetella sign-off-tarkistukset ja niiden tarkoituksen.
- Osaat tarkistaa suunnittelusääntöjä geometrisesti ja selittää
  antennisäännön syyn ja korjauksen.
- Osaat mallintaa tehoverkon vastusverkkona ja arvioida syöttönastojen
  ja liuskojen vaikutuksen IR-pudotukseen.
- Osaat kertoa, mitä ECO tarkoittaa ja miksi varasoluja käytetään.
