# Näytteistys ja kohinan vähentäminen

Polunseurannan kuva on harhaton mutta kohinainen, ja kohina pienenee
hitaasti: puolet pienempi kohina vaatii nelinkertaisen ajan. Tässä
luvussa käsitellään kolme tapaa saada kuva valmiiksi nopeammin:
näytteiden parempi sijoittelu, kohinan poisto kuvasta ja lopuksi
sävykuvaus, joka muuntaa radianssin näytettäväksi kuvaksi.

## Ositettu näytteistys

Riippumattomat satunnaiset näytteet kasautuvat sattumalta ja jättävät
aukkoja. *Ositettu näytteistys* (stratified sampling) jakaa alueen
$\sqrt{N} \times \sqrt{N}$ ruutuun ja ottaa yhden satunnaisen näytteen
kustakin. Näytteet ovat edelleen satunnaisia, joten estimaatti on
harhaton, mutta ne peittävät alueen tasaisesti. Varianssi ei koskaan
kasva, ja epäjatkuvalle integrandille kuten kappaleen reunalle virhe
pienenee nopeammin kuin $1/\sqrt{N}$: vain reunan leikkaamat ruudut
vaihtelevat.

*Matalan diskrepanssin jonot* menevät pidemmälle. Haltonin jonon
$i$:s piste saadaan kirjoittamalla $i$ kannassa $b$ ja peilaamalla
numerot desimaalipilkun toiselle puolelle: kannassa 2 luvut 1, 2, 3,
4 ovat 0,1, 0,01, 0,11 ja 0,001 binäärisinä eli 0,5, 0,25, 0,75 ja
0,125. Jokainen uusi piste täyttää suurimman aukon. Kaksiulotteinen
jono käyttää kantoja 2 ja 3:

```{.cpp tiedosto="esimerkit/yhteinen/satunnainen.hpp" osa="halton"}
```

Haltonin jono on deterministinen, joten toistetut estimaatit olisivat
samoja. Cranleyn ja Pattersonin kierto siirtää kaikkia pisteitä samalla
satunnaisella vektorilla modulo 1, jolloin toistot ovat
riippumattomia ja estimaatti harhaton, mutta pisteiden tasaisuus
säilyy.

```{.cpp tiedosto="esimerkit/10-naytteistys.cpp" osa="integrandi"}
```

```{.cpp tiedosto="esimerkit/10-naytteistys.cpp" osa="sijoittelu"}
```

```{.cpp tiedosto="esimerkit/10-naytteistys.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/10-naytteistys.odotettu"}
```

Kun näytteitä on 64 kertaa enemmän, satunnaisten näytteiden virhe
pienenee kahdeksasosaan, kuten $1/\sqrt{N}$ ennustaa. Ositettujen ja
Haltonin näytteiden virhe pienenee 25-osaan. Reunalle teoreettinen
nopeus on $N^{-3/4}$, ja 1 024 näytteellä ositettu näytteistys on
jo yhtä hyvä kuin noin 45 000 satunnaista näytettä.

Polunseurannassa sama periaate koskee jokaista ulottuvuutta:
pikselin aluetta, linssiä, valon pintaa ja jokaisen pompun suuntaa.
Ositus ei skaalaudu moneen ulottuvuuteen, koska $\sqrt[d]{N}$
ruutua akselia kohden vaatii valtavan $N$:n. Siksi tuotantorenderöijät
käyttävät matalan diskrepanssin jonoja kuten Sobolin jonoa, joissa
jokainen ulottuvuus on hyvin jakautunut ja pareittaiset projektiot
myös. Tämän tutoriaalin polunseuranta käyttää yksinkertaisuuden
vuoksi riippumattomia näytteitä.

## Kohinan poisto

Kohina on pikselistä toiseen riippumatonta, mutta kuva itse on
naapuripikseleissä samanlainen. Kohinan poisto käyttää tätä:
keskiarvo naapureista vähentää kohinaa samoin kuin lisänäytteet,
mutta laskentaa tarvitaan murto-osa. Hinta on harha: suodatin
sumentaa reunat ja yksityiskohdat.

Reunat säilyttävä suodatin käyttää *apupuskureita*. Ensimmäisen
osuman normaali, syvyys ja materiaali ovat kohinattomia, koska ne
saadaan yhdellä säteellä pikselin keskeltä. Suodatin ottaa mukaan vain
naapurit, joiden apupuskurin arvot ovat lähellä omia. Kappaleen
reunan yli ei silloin keskiarvoisteta.

```{.cpp tiedosto="esimerkit/10-kohina.cpp" osa="apupuskuri"}
```

```{.cpp tiedosto="esimerkit/10-kohina.cpp" osa="suodin"}
```

```{.cpp tiedosto="esimerkit/10-kohina.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/10-kohina.odotettu"}
```

![Kaksi näytettä pikselissä, laatikkosuodin, reunat säilyttävä
suodin ja 1 024 näytteen vertailukuva. Valo on piirretty
mustana.](kuvat/10-kohina.png){width=100%}

Laatikkosuodin pienentää virhettä, mutta pallot ja seinien reunat
sumenevat, ja punainen ja vihreä valuvat valkoiselle seinälle.
Reunat säilyttävä suodin pitää rajat terävinä ja pienentää virhettä
lisää. Kummallekin jää kohinaa, josta tulee läikikästä: suodatettu
kohina on matalataajuista, ja silmä huomaa sen helpommin kuin
pikselikohinan.

Tuotannossa suodattimia on kahta tyyppiä. Reaaliaikaiset suodattimet
(SVGF, Schied ym. 2017) yhdistävät naapuripikselit ja edelliset
kuvat liikevektorien avulla ja säätävät suodattimen leveyttä
kohinan arvioidun varianssin mukaan. Elokuvarenderöijät ja monet
pelit käyttävät neuroverkkoa, joka on opetettu kohinaisten ja
vertailukuvien pareilla. Kummassakin apupuskurit ovat keskeinen syöte.

## Kirkkaat pisteet

Harvinaiset polut, joiden paino on suuri, tuottavat yksittäisiä
erittäin kirkkaita pikseleitä (englanniksi *fireflies*). Edellisen
luvun kiiltävät pallot ja niiden ympäristö olivat tällaisia. Ne
ovat harhattomia, mutta niiden varianssi on niin suuri, että ne eivät
katoa käytännön näytemäärillä. Yksinkertaisin keino on rajata
yksittäisen näytteen radianssi ylhäältä, mikä on harhaista: kuva
tummuu hieman. Parempi keino on poistaa syy: MIS kiiltäville
pinnoille, polkujen kaventaminen karheusrajoilla tai
suodattimen robusti estimaatti, joka korvaa ääriarvot naapureiden
mediaanilla.

## Sävykuvaus

Radianssilla ei ole ylärajaa, mutta näytöllä on. Valolähteet,
heijastukset ja aurinko ovat satoja kertoja kirkkaampia kuin keskiharmaa
pinta. *Sävykuvaus* (tone mapping) puristaa alueen välille $[0, 1]$
ennen sRGB-koodausta. Yksinkertainen leikkaus säilyttää tummat sävyt
mutta tekee kirkkaista alueista tasaisen valkoisia. Reinhardin
käyrä $x/(1 + x)$ ei koskaan saavuta valkoista, ja laajennettu
versio kuvaa valkoisen pisteen $W$ arvoksi 1. Elokuvateollisuuden
ACES-käyrä antaa kontrastia keskisävyihin ja pehmeän olkapään
kirkkaille alueille.

```{.cpp tiedosto="esimerkit/10-savykuvaus.cpp" osa="kayrat"}
```

```{.cpp tiedosto="esimerkit/10-savykuvaus.cpp" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/10-savykuvaus.odotettu"}
```

Keskiharmaa (radianssi 0,18) koodautuu leikkauksella tavuksi 118,
Reinhardilla 109 ja ACES-käyrällä 141. ACES-kuva näyttää siksi
kirkkaammalta ja kontrastisemmalta, ja siksi sen kanssa käytetään
yleensä pienempää valotusta. Käyrä valitaan kuvan tarkoituksen mukaan:
mittauksiin ja vertailuun lineaarinen leikkaus, elokuvamaiseen
kuvaan ACES tai vastaava. Sävykuvaus tehdään aina radianssille ennen
sRGB-koodausta, ja valotus (radianssin kerroin) ennen sävykuvausta.
Väreille käyrä sovelletaan tavallisesti kuhunkin kanavaan erikseen,
mikä muuttaa kirkkaiden värien sävyä; tarkemmat menetelmät
käsittelevät luminanssia ja värikylläisyyttä erikseen.

## Käytännössä

- **Osita tai käytä matalan diskrepanssin jonoa** pikselin
  alueelle ja ensimmäisille ulottuvuuksille. Hyöty on suurin reunoilla
  ja pienillä näytemäärillä.
- **Pidä apupuskurit.** Normaali, syvyys ja albedo ensimmäisestä
  osumasta ovat kohinattomia ja kaikkien suodattimien syöte.
- **Laske vertailukuva aina harhattomasti.** Kohinan poisto ja
  kirkkaiden näytteiden leikkaus ovat harhaisia, ja niiden vaikutus
  pitää pystyä mittaamaan.
- **Poista kirkkaiden pisteiden syy** ennen kuin leikkaat niitä:
  useimmiten puuttuva MIS tai väärä pdf.
- **Sävykuvaus viimeisenä**, radianssille, ja valitse käyrä
  tarkoituksen mukaan.

## Itsearviointi

- Osaat toteuttaa ositetun näytteistyksen ja Haltonin jonon ja
  selittää, miksi ne pienentävät virhettä reunoilla.
- Osaat selittää Cranleyn ja Pattersonin kierron tarkoituksen.
- Osaat toteuttaa apupuskuria käyttävän reunat säilyttävän
  suodattimen ja arvioida sen harhaa vertailukuvaa vastaan.
- Osaat vertailla sävykuvauskäyriä ja sijoittaa valotuksen,
  sävykuvauksen ja sRGB-koodauksen oikeaan järjestykseen.
