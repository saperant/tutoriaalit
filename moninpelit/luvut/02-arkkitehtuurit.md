# Arkkitehtuurit

Ensimmäinen päätös on, kuka pitää pelin virallista tilaa ja kenen kautta
tieto kulkee. Päätös vaikuttaa viiveeseen, kaistaan, huijaamiseen ja
kustannuksiin, eikä sitä voi helposti muuttaa myöhemmin.

## Kolme mallia

- **Vertaisverkko** (peer-to-peer). Jokainen kone lähettää tilansa tai
  syötteensä kaikille muille. Ei palvelinkuluja, ja suora reitti on
  usein lyhin. Viestien määrä kasvaa neliöllisesti, jokaisen pelaajan
  lähetyskaista kasvaa pelaajamäärän mukana, ja osoitteenmuunnokset
  (NAT) vaikeuttavat suoria yhteyksiä. Kenelläkään ei ole auktoriteettia.
- **Asiakas–palvelin.** Asiakkaat lähettävät syötteensä palvelimelle,
  joka simuloi pelin ja lähettää tilan takaisin. Palvelin on ainoa totuus
  ja huijaamisen esto on mahdollista. Hinta on palvelinkustannus ja se,
  että tieto kiertää palvelimen kautta.
- **Isäntä–asiakas** (listen server). Yksi pelaajista toimii
  palvelimena. Ei palvelinkuluja, mutta isännän viive omaan peliinsä on
  nolla, isännän lähetyskaista rajoittaa pelaajamäärää, ja jos isäntä
  lähtee, peli loppuu tai isäntä on siirrettävä.

Kun viiveet tunnetaan, mallien erot voi laskea:

```{.cpp tiedosto="esimerkit/02-topologiat.cpp" osa="viive"}
```

```{.cpp tiedosto="esimerkit/02-topologiat.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-topologiat.odotettu"}
```

Tulos voi yllättää: palvelimen kautta kulkeva pahin viive (56 ms) on
pienempi kuin suora vertaisyhteys (70 ms). Internetin reititys ei
noudata kolmioepäyhtälöä: hyvin kytketty konesali voi olla kahdelle
kaukaiselle pelaajalle lähempänä kuin he ovat toisilleen. Isäntämallissa
isäntä pelaa nollaviiveellä, kun kaukaisin pelaaja odottaa 140 ms
jokaista vastausta. Isännän lähetyskaista (86 kB/s) on mobiiliyhteydelle
jo paljon.

## Auktoriteetti

*Auktoriteetti* tarkoittaa, kenen päätös pätee, kun koneet ovat eri
mieltä. Täysin palvelimen auktoriteettiin perustuvassa pelissä asiakas
lähettää vain aikeensa (syötteet), ja palvelin päättää kaiken
lopputuloksen: sijainnit, osumat, pisteet ja tavarat. Asiakkaan
näkemä tila on palvelimen tilan arvio, jota korjataan jatkuvasti.

Auktoriteetin voi myös jakaa. Monessa pelissä asiakas saa päättää oman
kameransa, käyttöliittymän ja kosmeettiset efektit, joskus jopa oman
liikkeensä, jolloin palvelin vain tarkistaa uskottavuuden. Jaettu
auktoriteetti on helpompi tehdä ja tuntuu paremmalta huonolla
yhteydellä, mutta jokainen asiakkaalle annettu päätös on huijarille
avoin ovi (luku *Auktoriteetti ja huijaamisen esto*).

Lukitusaskelmallissa (luku *Lukitusaskel ja rollback*) kukaan ei lähetä
tilaa: kaikki koneet simuloivat saman pelin samoista syötteistä.
Auktoriteetti on silloin syötteiden järjestyksessä ja tarkistussummissa.

## Käytännössä

- **Kilpailullinen peli: palvelin.** Jos huijaamisella on merkitystä
  (sijoitukset, palkinnot, kauppa), auktoriteetin on oltava koneella,
  jota pelaaja ei hallitse. Oletusvalinta on omistettu palvelin
  (dedicated server).
- **Yhteistyö- ja kaveripelit: isäntä tai vertaisverkko.** Kun pelaajat
  tuntevat toisensa, huijaaminen ei ole ongelma ja palvelinkulut ovat.
  Varaudu isännän vaihtoon (host migration) tai tallenna peli niin,
  että sen voi jatkaa.
- **Mittaa, älä arvaa.** Kerää todelliset viiveet ja häviöt pelaajien
  alueilta ennen kuin päätät palvelinten sijainnit.
- **Relepalvelin vertaisverkolle.** NAT-läpäisy (STUN, hole punching)
  onnistuu usein mutta ei aina; varalla tarvitaan välityspalvelin
  (TURN-tyyppinen rele), joka lisää viivettä mutta ei simuloi peliä.
- **Hinta:** palvelin maksaa jatkuvasti ja kasvaa pelaajamäärän mukana;
  vertaisverkko siirtää kustannuksen pelaajien yhteyksille ja
  luotettavuuden heikoimmalle koneelle.

## Itsearviointi

- Osaat verrata vertaisverkkoa, asiakas–palvelin-mallia ja isäntää
  viiveen, kaistan, kustannusten ja huijaamisen kannalta.
- Osaat laskea viestimäärän ja pelaajan lähetyskaistan kussakin
  mallissa.
- Osaat selittää palvelimen auktoriteetin ja sen, miksi asiakas lähettää
  aikeita eikä lopputuloksia.
- Osaat perustella, milloin isäntämalli tai vertaisverkko riittää.
