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

## Kenelle ja mitä tarvitaan

Lukija tuntee tietoverkkojen kerrosmallin ja protokollat (taito
*Tietoverkot*), todennäköisyyslaskennan perusteet (taito
*Todennäköisyys ja tilastot*) sekä Pythonin ja NumPyn (taito
*Python työkaluohjelmointiin*). Signaalinkäsittelyä ei edellytetä: modulaatiot ja
synkronointi käsitellään syvällisemmin taidossa *Digitaalinen tiedonsiirto*, ja
tässä niistä tarvitaan vain periaate.

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

## Desibelit

Tietoliikenteessä tehot vaihtelevat kymmenien kertaluokkien välillä:
lähetin voi syöttää 100 mW, ja vastaanotin kuulee 0,000 000 001 mW.
Siksi tehot ja tehosuhteet ilmaistaan logaritmisesti desibeleinä.
Tehosuhde $P_2/P_1$ on desibeleinä $10 \log_{10}(P_2/P_1)$, ja
absoluuttinen taso milliwattiin verrattuna ilmaistaan yksikössä dBm.

```{.python tiedosto="esimerkit/01-desibelit.py" osa="nyrkkisaannot"}
```

Desibelien etu on, että ketjun vahvistukset ja vaimennukset vain
lasketaan yhteen. Siirtoketju lasketaan siksi aina desibeleinä:

```{.python tiedosto="esimerkit/01-desibelit.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/01-desibelit.odotettu"}
```

Kaksi sudenkuoppaa: desibelejä ei voi summata, kun lasketaan yhteen
*tehoja* (kaksi 0 dBm:n lähdettä on 3 dBm, ei 0 dBm), ja jännitteen
tai virran suhde on $20 \log_{10}$, koska teho on verrannollinen
jännitteen neliöön.

## Esimerkit

Esimerkit ovat Python 3.12 -ohjelmia, jotka käyttävät vain
standardikirjastoa ja NumPya. Ne tarkistetaan työkaluilla ruff ja
mypy --strict, ja niiden tulostetta verrataan odotettuun. Simulaatiot
käyttävät kiinteää satunnaislukusiementä, joten jokainen ajo tuottaa
saman tuloksen, ja tulosta verrataan analyyttiseen arvoon aina kun se
on mahdollista. Simulaatiot ovat tahallaan pieniä: ne mahtuvat sivulle
ja valmistuvat sekunnissa, mutta niissä on samat ilmiöt kuin oikeissa
järjestelmissä.

Kertoimet ja raja-arvot ovat suuruusluokaltaan oikeita mutta
pyöristettyjä. Kun lasket oikeaa linkkiä, käytä laitteen tietolehden ja
standardin arvoja.
