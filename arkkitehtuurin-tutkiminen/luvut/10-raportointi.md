# Validointi, toistettavuus ja raportointi

Mallin tulos on väite, ja väite tarvitsee perustelun. Kolme kysymystä
erottaa luotettavan tutkimuksen tulosten kokoelmasta: kuinka epävarma
tulos on, kuinka hyvin malli vastaa todellisuutta ja voiko joku muu
toistaa tuloksen. Tämä luku käsittelee jokaisen. Tilastolliset perusteet,
kuten luottamusvälit ja hypoteesitestit, ovat paketissa *Todennäköisyys
ja tilastot*; tässä niitä sovelletaan simulointeihin.

## Toistot ja luottamusväli

Simulointi satunnaisella kuormalla antaa satunnaisen tuloksen. Yksi
ajo on yksi otos, eikä yksi otos kerro, kuinka paljon tulos vaihtelee.
Ratkaisu on ajaa sama koe eri siemenillä ja laskea keskiarvo ja
luottamusväli. Toistot ovat riippumattomia, joten Studentin
t-jakaumaan perustuva väli on oikea, vaikka yksittäisen ajon sisällä
peräkkäiset havainnot korreloivat (luku 4).

```{.python tiedosto="esimerkit/arkki/tilasto.py" osa="t"}
```

Luvun 4 M/M/1-jono 90 %:n kuormalla, kymmenen toistoa 20 000
asiakkaalla:

```{.python tiedosto="esimerkit/10-toistot.py" osa="koe"}
```

```{.python tiedosto="esimerkit/10-toistot.py" osa="toistot"}
```

```{.tuloste tiedosto="esimerkit/10-toistot.odotettu"}
```

Yksittäiset ajot vaihtelevat 82 ns:stä 129 ns:iin, eli ±25 %
keskiarvosta. Jos tutkimus vertaisi kahta suunnitelmaa yhdellä ajolla
kummastakin, 20 %:n ero voisi olla pelkkää kohinaa. Kymmenen toiston
keskiarvo on 102 ± 12,5 ns, ja analyyttinen 100 ns on välin sisällä.
Kahden prosentin tarkkuuteen tarvittaisiin lähes 300 toistoa, tai
pidempiä ajoja: välin leveys pienenee kuten $1/\sqrt{n}$.

Kun kahta suunnitelmaa verrataan, varianssia voi pienentää *yhteisillä
satunnaisluvuilla* (*common random numbers*): kumpikin ajetaan samalla
siemenellä, jolloin ne näkevät saman kuorman, ja ero johtuu
suunnitelmasta eikä kuormasta. Luvun 5 mallit tekivät juuri näin.

## Validointi ja kalibrointi

*Validointi* kysyy, vastaako malli todellisuutta: mittausta, tarkempaa
mallia tai toteutusta. *Kalibrointi* säätää mallin parametreja, jotta se
vastaisi viitettä paremmin. Ne on tehtävä eri datalla. Malli, jota on
säädetty juuri niihin pisteisiin, joilla sitä arvioidaan, näyttää aina
hyvältä.

Validointivirhe raportoidaan keskimääräisenä suhteellisena virheenä
(*mean absolute percentage error*, MAPE) ja suurimpana virheenä.
Keskiarvo kertoo tyypillisen tarkkuuden, maksimi pahimman tapauksen:

```{.python tiedosto="esimerkit/arkki/tilasto.py" osa="virheet"}
```

Luvun 6 intervallimallissa väärän ennustuksen hinta, 18 jaksoa, oli
arvio. Sen voi sovittaa yksityiskohtaiseen malliin. Sovitus tehdään
ikkunoilla 16 ja 64, ja mallia testataan ikkunalla 128, jota sovitus ei
nähnyt:

```{.python tiedosto="esimerkit/10-validointi.py" osa="data"}
```

```{.python tiedosto="esimerkit/10-validointi.py" osa="kalibrointi"}
```

```{.tuloste tiedosto="esimerkit/10-validointi.odotettu"}
```

Sovitus parantaa sekä sovitus- että testivirhettä: testivirhe putoaa
9,2 %:sta 3,3 %:iin, joten kalibrointi yleistyy. Sovitettu arvo on
kuitenkin nolla: mallin mukaan väärä ennustus ei maksa mitään. Se on
fysikaalisesti väärin, koska ydin todella odottaa 8 jakson palautuksen.
Parametri on kompensoinut toisen virheen: malli yliarvioi suoritusajan
muutenkin (luku 6: +2…+9 %), ja haaran hinnan pienentäminen kumoaa
yliarvion.

Tämä on kalibroinnin vaara. Kalibroitu parametri ei ole enää mitattu
suure, vaan se kantaa mallin muut virheet. Malli toimii niin kauan kuin
kuorma muistuttaa kalibrointikuormaa. Jos haaroja olisi enemmän ja
hutia vähemmän, se menisi pahasti pieleen. Siksi kalibroidaan
mieluummin parametreja, joilla on fysikaalinen merkitys ja tunnettu
vaihteluväli, ja tarkistetaan, että sovitettu arvo on välin sisällä. Jos
se ei ole, malli tarvitsee korjausta, ei kalibrointia.

## Toistettavuus

Tulos, jota ei voi toistaa, on vaikea tarkistaa, eikä sitä voi
käyttää uudelleen, kun malli muuttuu. Toistettavuus vaatii, että kaikki
tuloksen syötteet on kirjattu:

- mallin versio (versionhallinnan tunniste)
- kaikki parametrit, myös oletusarvot
- kuorma ja sen versio
- siemenet
- työkalujen versiot (kääntäjä, SystemC, Python-kirjastot)

Esimerkki kokoaa kokeen parametrit tietueeksi ja tallentaa ne yhdessä
tuloksen kanssa. Tiedoston nimi on sisällön tiiviste, joten sama koe
samalla tuloksella saa aina saman nimen, ja eri tulos eri nimen:

```{.python tiedosto="esimerkit/10-toistot.py" osa="tiedosto"}
```

Tulos pyöristetään ennen tiivistämistä. Liukulukulaskennan viimeinen
bitti voi vaihdella matematiikkakirjaston version mukaan, ja ilman
pyöristystä tiiviste muuttuisi, vaikka tulos ei olennaisesti muutu.
Saman periaatteen vuoksi tämän paketin esimerkkien tulosteet ovat
pyöristettyjä ja kaikki satunnaisuus tulee kiinteistä siemenistä.

Tunnetut työnkulun työkalut, kuten Snakemake, DVC ja MLflow, hoitavat
saman kirjanpidon laajemmin: ne muistavat, mikä tulos tuotettiin millä
syötteillä, ja ajavat uudelleen vain sen, mikä muuttui.

## Raportointi

Hyvä tulosraportti antaa lukijalle mahdollisuuden arvioida itse, kuinka
paljon tulokseen voi luottaa:

| Raportoi | Miksi |
|----------|-------|
| kysymys ja päätös, johon tulos vaikuttaa | lukija tietää, mikä tarkkuus riittää |
| malli, sen tarkkuustaso ja validointi | lukija tietää, mitä malli näkee ja mitä ei |
| kuormat ja niiden valinta | tulos koskee vain näitä kuormia |
| parametrit ja oletukset | tulos voidaan toistaa ja kyseenalaistaa |
| epävarmuus: luottamusvälit, validointivirhe | erot voidaan erottaa kohinasta |
| herkkyys: oletukset, joista päätös riippuu | päätöksentekijä tietää, mitä tarkistaa |

Kuvissa samat periaatteet: akselit nimetään yksiköineen, kaikki
vertailtavat kuvaajat samalla asteikolla, ja kun pisteissä on hajontaa,
virhepalkit tai luottamusvälit näkyviin. Keskiarvoja eri kuormien yli
laskettaessa käytetään nopeutuksille geometristä keskiarvoa, koska
aritmeettinen keskiarvo painottaa suuria suhdelukuja ja riippuu siitä,
kumpaa suunnitelmaa käytetään vertailukohtana.

## Käytännössä

- **Toista eri siemenillä.** Yksi ajo ei kerro epävarmuutta. Raportoi
  keskiarvo ja luottamusväli, ja vertaa suunnitelmia samoilla
  siemenillä.
- **Kalibroi ja validoi eri datalla.** Sovitus samoihin pisteisiin,
  joilla arvioidaan, näyttää aina hyvältä.
- **Epäile kalibroitua parametria**, joka on fysikaalisesti
  mahdoton. Se kompensoi mallin rakenteellista virhettä.
- **Kirjaa kaikki syötteet.** Parametrit, siemenet ja versiot yhdessä
  tuloksen kanssa; mieluiten koneellisesti ja tiivisteellä tunnistettuna.
- **Raportoi oletukset, joista päätös riippuu.** Ne ovat raportin
  arvokkain osa, koska niiden tarkistaminen on seuraava työ.

## Itsearviointi

- Osaat laskea toistetuista simuloinneista keskiarvon ja 95 %:n
  luottamusvälin ja arvioida tarvittavien toistojen määrän.
- Osaat erottaa validoinnin ja kalibroinnin ja tehdä ne eri datalla.
- Osaat tunnistaa kalibroinnin, joka kompensoi mallin rakenteellista
  virhettä.
- Osaat kirjata kokeen niin, että tuloksen voi toistaa, ja koota
  raportin, josta tuloksen luotettavuuden voi arvioida.
