# Avainten säilytys

Laite tarvitsee salaisuuksia: identiteetin pilvipalveluun, avaimen
tallennettujen tietojen salaukseen, todennusavaimen. Ongelma on, että
laite on hyökkääjän käsissä. Tavallinen flash on luettavissa
debug-portista, ulkoinen flash irrottamalla piiri. Tässä luvussa käydään
läpi, mihin avaimet laitetaan, miten jokainen laite saa omansa ja
miten avain voidaan johtaa piirin fysiikasta.

## Säilytyspaikat

| Paikka | Suojaa | Ei suojaa |
|--------|--------|-----------|
| Tavallinen flash | ei juuri mitään | debug, piirin irrotus |
| OTP/eFuse | muuttamiselta | lukemiselta, ellei piiri lukitse sitä |
| Mikrokontrollerin suojattu alue | ohjelmistolta, joka ei ole suojatussa tilassa | invasiivisilta hyökkäyksiltä |
| Turvaelementti | lukemiselta; avain ei koskaan poistu | väärinkäytöltä: piiri allekirjoittaa sen, mitä pyydetään |
| TPM 2.0 | lukemiselta; avain voidaan sitoa mittauksiin | väylän salakuuntelulta ilman salattua istuntoa |

**Turvaelementti** (*secure element*, esim. Microchip ATECC608,
NXP SE050, Infineon OPTIGA Trust M) on erillinen piiri, joka on
suunniteltu kestämään fyysisiä hyökkäyksiä. Avain luodaan piirissä ja
pysyy siellä: piiri allekirjoittaa ja johtaa avaimia, mutta ei koskaan
luovuta yksityisavainta.

**TrustZone** jakaa suorittimen turvalliseen ja tavalliseen tilaan.
Cortex-M33:n kaltaisissa Armv8-M-piireissä (TrustZone-M) muistialueet
merkitään turvallisiksi tai tavallisiksi (SAU), ja tavallinen koodi voi
kutsua turvallista vain sallittujen sisääntulokohtien kautta. Avaimet
ja kryptografia ovat turvallisella puolella (esim. Trusted
Firmware-M), ja haavoittuva sovellus tavallisella puolella ei pääse
niihin. Sovellusprosessoreissa (TrustZone-A) turvallisella puolella ajetaan
erillistä käyttöjärjestelmää (*trusted execution environment*, esim.
OP-TEE).

## Laitekohtaiset avaimet

Luvun 2 tärkein periaate oli, ettei laitteilla ole yhteisiä
salaisuuksia. Käytännössä jokaisella laitteella on oma juuriavain
(**HUK**, *hardware unique key*). Siitä johdetaan **jokaiseen
käyttöön oma avain** HKDF:llä, joten yhden käytön vuoto ei paljasta
muita. Valmistaja voi johtaa laitekohtaisen juuriavaimen pääavaimesta
ja sarjanumerosta (*key diversification*), jolloin taustajärjestelmä
saa saman avaimen ilman tietokantaa:

```{.python tiedosto="esimerkit/06-laiteavaimet.py" osa="johda"}
```

```{.tuloste tiedosto="esimerkit/06-laiteavaimet.odotettu"}
```

Johtaminen on yksisuuntaista: laitteen avaimesta ei saa pääavainta, eikä
yhden käytön avaimesta laitteen juuriavainta. Pääavain on HSM:ssä, eikä
sitä ole koskaan laitteessa. Käyttötarkoituksen nimessä on versio
(`/v1`), jotta avaimen voi kierrättää ilman, että johtamisen kaava
muuttuu.

## PUF: avain piirin fysiikasta

OTP:hen poltettu avain on olemassa myös silloin, kun laite on
sammutettu, ja sen voi periaatteessa lukea piiriä tutkimalla.
**PUF** (*physically unclonable function*) johtaa avaimen
valmistusvaihtelusta: jokainen SRAM-solu asettuu käynnistyksessä
tiettyyn arvoon, joka riippuu transistorien pienistä eroista. Avainta ei
ole tallennettu mihinkään, vaan se syntyy uudelleen jokaisella
käynnistyksellä.

```{.python tiedosto="esimerkit/06-puf.py" osa="puf"}
```

Lukema on kohinainen, joten siitä ei voi tiivistää avainta suoraan.
**Sumea poimija** (*fuzzy extractor*) tallentaa tehtaalla julkisen
apudatan: lukeman ja virheenkorjauskoodilla koodatun satunnaisen
salaisuuden XOR:n. Kentällä uusi lukema ja apudata antavat koodatun
salaisuuden kohinaisena, ja koodi korjaa virheet:

```{.python tiedosto="esimerkit/06-puf.py" osa="poimija"}
```

Epävakaat solut kannattaa jättää pois. Rekisteröinnissä luetaan monta
kertaa ja tallennetaan vakaiden solujen indeksit apudatan osana:

```{.python tiedosto="esimerkit/06-puf.py" osa="vakaat"}
```

```{.tuloste tiedosto="esimerkit/06-puf.odotettu"}
```

Tulos näyttää molemmat ominaisuudet: sama laite saa avaimen lähes
aina, toinen laite samalla apudatalla ei koskaan. Esimerkin
toistokoodi ei silti riitä tuotantoon. Laite, joka ei saa avaintaan
kerran sadasta käynnistyksestä, on rikki, ja toistokoodin apudata
paljastaa osan salaisuudesta. Kaupalliset PUF-toteutukset käyttävät
tehokkaampia koodeja ja testattuja parametreja.

## Avainten syöttö tehtaalla

Laitekohtaiset avaimet syntyvät joko laitteessa (turvaelementti ja PUF
luovat avaimen itse, ja tehdas varmentaa julkisen avaimen) tai
tehtaan HSM:ssä, josta ne syötetään laitteeseen. Ensimmäinen on
parempi: yksityisavain ei ole koskaan ollut laitteen ulkopuolella.
Molemmissa tapauksissa laitteen julkinen avain tai varmenne
rekisteröidään taustajärjestelmään, mikä paljastaa myös
ylituotetut laitteet.

## Käytännössä

- **Älä tallenna avaimia selväkielisinä flashiin.** Käytä
  turvaelementtiä, TPM:ää, piirin suojattua aluetta tai salaa avaimet
  laitekohtaisella avaimella (*key wrapping*).
- **Luo avain laitteessa**, jos laitteisto sen sallii, ja varmenna
  julkinen avain tehtaalla.
- **Yksi avain, yksi käyttö.** Johda avaimet juuriavaimesta
  käyttötarkoituksen mukaan ja versioi käyttötarkoitukset.
- **Turvaelementti ei estä väärinkäyttöä.** Jos sovellus on murrettu,
  hyökkääjä voi pyytää piiriä allekirjoittamaan; avain ei vuoda, mutta
  laitteen identiteettiä voidaan käyttää. Rajaa, mitä piiriltä voi
  pyytää, ja seuraa käyttöä taustajärjestelmässä.

## Itsearviointi

- Osaat vertailla avainten säilytyspaikkoja ja valita niistä tuotteen
  uhkamallin mukaan.
- Osaat johtaa laitekohtaiset ja käyttötarkoituskohtaiset avaimet
  HKDF:llä ja perustella, miksi johtaminen on yksisuuntaista.
- Osaat selittää PUF:n ja sumean poimijan toiminnan sekä sen, miksi
  epävakaat solut jätetään pois.
- Osaat kuvata TrustZonen roolin avainten suojaamisessa.
