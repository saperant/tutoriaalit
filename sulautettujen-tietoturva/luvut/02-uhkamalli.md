# Laitteen uhkamalli

Uhkamallinnuksen menetelmät (tietovuokaaviot, STRIDE, hyökkäyspuut)
ovat samat kuin muissakin järjestelmissä. Laitteelle ominaista on
kolme asiaa: hyökkääjän **pääsy** voi olla fyysinen, laite kulkee
**toimitusketjun** läpi monen käsissä, ja sen **elinkaari** on pitkä.

## Pääsytasot

Hyökkääjät jaetaan sen mukaan, mihin he ulottuvat. Korkeampi taso
sisältää alemmat:

```{.python tiedosto="esimerkit/02-uhkamalli.py" osa="paasy"}
```

| Taso | Esimerkki | Tyypillinen hinta |
|------|-----------|-------------------|
| Etä | haavoittuvuus pilvirajapinnassa, botnetti | skaalautuu tuhansiin laitteisiin |
| Lähi | Bluetooth, Wi-Fi, Zigbee, paikallinen verkko | kantama ja aika |
| Fyysinen | UART-konsoli, SWD/JTAG, ulkoinen flash | laite ja juotin, tunteja |
| Invasiivinen | jännitehäiriöt, tehonkulutuksen mittaus, piirin avaus | laboratorio, päiviä tai viikkoja |

Laitteen hyökkäyspinnat luetellaan samalla jaolla:

```{.python tiedosto="esimerkit/02-uhkamalli.py" osa="pinnat"}
```

## Yhden laitteen murto ja koko kannan murto

Fyysinen hyökkäys on hidas ja kallis, mutta se kohdistuu yhteen
laitteeseen. Ratkaisevaa on, mitä yhdestä laitteesta saa: jos kaikissa
laitteissa on sama salaisuus, yhden laitteen avaus vaarantaa kaikki
(*class break*):

```{.python tiedosto="esimerkit/02-uhkamalli.py" osa="arvioi"}
```

```{.tuloste tiedosto="esimerkit/02-uhkamalli.odotettu"}
```

Tämä on sulautettujen järjestelmien tärkein suunnitteluperiaate:
**yhden laitteen murtamisen ei pidä helpottaa muiden murtamista.**
Siksi luvun 6 laitekohtaiset avaimet ovat perusvaatimus, eivät
lisäominaisuus. Esimerkkejä yhteisistä salaisuuksista, joita on löydetty
laitteista: kaikille laitteille sama TLS-yksityisavain, sama
pääkäyttäjän salasana, sama salausavain päivityksille ja
valmistajan allekirjoitusavain laiteohjelmistossa.

## Toimitusketju

Laite kulkee piirivalmistajalta, piirilevyn kokoonpanijalta ja
tehtaalta jakelijan kautta asiakkaalle ja huoltoon. Jokainen vaihe on
uhka:

- **Väärennetyt komponentit**: piiri, joka näyttää oikealta mutta jonka
  suojaukset puuttuvat tai jossa on takaovi.
- **Ohjelmointi tehtaalla**: avainten ja laiteohjelmiston syöttö on
  kohta, jossa salaisuudet ovat selväkielisinä. Tehtaan
  ohjelmointiaseman pitää saada avaimet HSM:stä laitekohtaisesti, ei
  tiedostona.
- **Ylituotanto**: alihankkija valmistaa ylimääräisiä laitteita omaan
  myyntiinsä. Laitekohtainen identiteetti, joka rekisteröidään
  taustajärjestelmään, paljastaa ne.
- **Jakelu ja palautukset**: laite voidaan muokata ja palauttaa
  myyntiin. Mittauskäynnistys (luku 5) paljastaa muutetun ohjelmiston.

## Elinkaari

Teollisuuslaitteen käyttöikä on 10–20 vuotta. Elinkaaren vaiheilla on
omat uhkansa:

| Vaihe | Uhka | Vastatoimi |
|-------|------|------------|
| Valmistus | avainten vuoto, ylituotanto | HSM, laitekohtaiset avaimet, rekisteröinti |
| Käyttöönotto | oletussalasana, omistajuuden kaappaus | laitekohtainen salasana, todennettu liittäminen |
| Käyttö | etähyökkäys, haavoittuvuus | päivitykset, hyökkäyspinnan minimointi |
| Huolto | debug-portti auki, huoltoavain vuotaa | todennettu debug (luku 8) |
| Käytöstä poisto | tiedot ja avaimet jäävät laitteeseen | tehdasasetukset, avainten kumoaminen |

Pitkä elinkaari tarkoittaa myös, että laitteessa on kryptografiaa, jota
pitää voida vaihtaa (*crypto agility*): allekirjoitusalgoritmi, joka
on turvallinen vuonna 2026, ei välttämättä ole sitä vuonna 2040.
Tärkein kohde on käynnistimen allekirjoitustarkistus, koska ROM:ia ei
voi päivittää. Jos riittävän suuri kvanttitietokone rakennetaan
laitteen elinaikana, se murtaa RSA:n ja elliptiset käyrät, myös
luvun 3 Ed25519:n. Siksi pitkäikäisten laitteiden käynnistimiin
suositellaan jo nyt tiivistepohjaisia allekirjoituksia (LMS ja XMSS,
NIST SP 800-208), joiden turvallisuus nojaa vain tiivistefunktioon,
tai vähintään paikkaa toiselle avaimelle ja algoritmille.

## Käytännössä

- **Aloita pääsytasoista.** Päätä, mitä hyökkääjäprofiileja vastaan
  tuote suojataan. Kuluttajalaitteen kohdalla invasiivinen hyökkääjä
  hyväksytään yleensä jäännösriskinä, maksupäätteen tai
  älykortin kohdalla ei.
- **Ei yhteisiä salaisuuksia.** Jokaisella laitteella on oma
  identiteetti ja omat avaimensa. Jos jokin on pakko jakaa (esim.
  julkinen allekirjoitusten tarkistusavain), sen on oltava julkinen.
- **Uhkamalli elää.** Päivitä se, kun laitteeseen lisätään rajapinta,
  kun sen käyttöympäristö muuttuu ja kun alalla julkaistaan uusi
  hyökkäystekniikka.
- **Hinta on suojauksen mitta.** Tavoite ei ole murtamaton laite vaan
  laite, jonka murtaminen maksaa enemmän kuin se tuottaa, eikä
  skaalaudu.

## Itsearviointi

- Osaat luokitella laitteen hyökkäyspinnat pääsytason mukaan.
- Osaat selittää, miksi yhteinen salaisuus tekee fyysisestä
  hyökkäyksestä koko laitekannan uhan.
- Osaat nimetä toimitusketjun ja elinkaaren vaiheiden tyypilliset uhat
  ja niiden vastatoimet.
