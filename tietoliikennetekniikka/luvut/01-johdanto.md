# Johdanto {.runko-johdanto}

Tietoverkkojen protokollat olettavat, että bitti lähtee yhdestä päästä
ja saapuu toiseen. Tietoliikennetekniikka selittää, miten se tapahtuu:
millä nopeudella bittejä voi siirtää kuparissa, kuidussa ja radiossa,
miksi nopeutta ei voi kasvattaa loputtomiin, miten monta yhteyttä
jakaa saman siirtotien ja mitä tapahtuu, kun asemat lähettävät
samanaikaisesti. Nämä rajat näkyvät suoraan sovellusten arjessa:
Wi-Fi hidastuu seinän takana, kaukainen palvelin tuntuu hitaalta
nopeallakin liittymällä, ja täysi jono kasvattaa viivettä
räjähdysmäisesti.

Tutoriaali käy asiat läpi insinöörin tavalla: jokainen ilmiö lasketaan
tai simuloidaan pienellä Python-ohjelmalla, ja tulosta verrataan
teoriaan. Näin kaavoista tulee työkaluja, joilla arvioidaan, riittääkö
yhteys, eikä vain muistettavia lausekkeita.

## Esitiedot ja rajaus

Lukija tuntee tietoverkkojen kerrosmallin ja protokollat (taito
*Tietoverkot*), todennäköisyyslaskennan perusteet (taito
*Todennäköisyys ja tilastot*) sekä Pythonin ja NumPyn (taito
*Python työkaluohjelmointiin*). Signaalinkäsittelyä ei edellytetä.

Tutoriaali pysyy linkin ja siirtotien tasolla. Sen ulkopuolelle jäävät:

- modulaatioiden, pulssinmuokkauksen ja synkronoinnin toteutus (taito
  *Digitaalinen tiedonsiirto*); tässä niistä esitetään periaate
- protokollat verkkokerroksesta ylöspäin (taito *Tietoverkot*)
- lähiverkon ja langattoman verkon suunnittelu ja laitteiden asetukset
  (taito *Verkkoinfrastruktuuri*).

Luvut etenevät siirtotiestä ylöspäin, ja jokainen vastaa yhteen
kysymykseen:

| Luku | Kysymys |
|------|---------|
| Siirtotiet | Miksi signaali heikkenee kuparissa, kuidussa ja radiossa? |
| Kapasiteetti | Paljonko bittejä kanavaan mahtuu? |
| Linjakoodaus ja kehystys | Miten bitit muuttuvat signaaliksi ja kehyksiksi? |
| Virheet | Miten virheet havaitaan ja korjataan? |
| Multipleksointi | Miten monta yhteyttä jakaa saman siirtotien? |
| Kytkentä ja viive | Mistä viive syntyy ja miksi paketit voittivat piirit? |
| Kanavanvaraus | Kuka saa lähettää, kun kaikki haluavat? |
| Ethernet | Miten nämä yhdistyvät yleisimmässä lähiverkossa? |
| Matkaviestinverkot | Miten 4G ja 5G jakavat radion? |
| Jonot ja palvelun laatu | Miksi viive kasvaa kuormassa ja miten sitä hallitaan? |

## Esimerkit

Esimerkit ovat Python 3.12 -ohjelmia, jotka käyttävät vain
standardikirjastoa ja NumPya, ja ne ajetaan sellaisinaan, esimerkiksi
`python3 esimerkit/03-shannon.py`. Ne tarkistetaan työkaluilla ruff ja
mypy --strict, ja niiden tulostetta verrataan odotettuun. Simulaatiot
käyttävät kiinteää satunnaislukusiementä, joten jokainen ajo tuottaa
saman tuloksen, ja tulosta verrataan analyyttiseen arvoon aina kun se
on mahdollista. Simulaatiot ovat tahallaan pieniä: ne mahtuvat sivulle
ja valmistuvat sekunnissa, mutta niissä on samat ilmiöt kuin oikeissa
järjestelmissä. Kirjan kuvaajat on piirretty samoilla ohjelmilla:
`kuvat/piirra.py` lataa esimerkin ja piirtää sen funktioiden tulokset
(`make kuvat`).

Kertoimet ja raja-arvot ovat suuruusluokaltaan oikeita mutta
pyöristettyjä. Kun lasket oikeaa linkkiä, käytä laitteen tietolehden ja
standardin arvoja.
