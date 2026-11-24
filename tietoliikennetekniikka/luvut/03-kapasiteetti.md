# Kanavan kapasiteetti

Kuinka monta bittiä sekunnissa kanavan läpi voi siirtää? Vastaus
riippuu kahdesta suureesta: kaistanleveydestä ja signaali-kohinasuhteesta.
Kaistanleveys rajaa, kuinka monta symbolia sekunnissa voi lähettää, ja
kohina rajaa, kuinka monta bittiä yhteen symboliin voi pakata.

## Nyquist ja Shannon

Kaistanleveydeltään $B$ hertsin kanavan läpi voi lähettää enintään
$2B$ symbolia sekunnissa (Nyquist). Jos symbolilla on $M$ erotettavaa
tasoa, se kantaa $\log_2 M$ bittiä, joten kohinattoman kanavan raja on
$C = 2B \log_2 M$. Kohinattomassa kanavassa tasoja voisi lisätä
loputtomiin. Todellisessa kanavassa kohina sotkee lähekkäiset tasot,
ja Claude Shannon osoitti vuonna 1948, että virheettömän siirron
yläraja on

$$C = B \log_2\left(1 + \frac{S}{N}\right).$$

Raja ei kerro, miten siihen päästään, vaan sen, ettei mikään
modulaatio tai koodaus voi ylittää sitä. Nykyiset koodit (LDPC, polar)
pääsevät hyvin lähelle rajaa.

```{.python tiedosto="esimerkit/03-shannon.py" osa="kanavat"}
```

```{.python tiedosto="esimerkit/03-shannon.py" osa="tasot"}
```

```{.tuloste tiedosto="esimerkit/03-shannon.odotettu"}
```

Analogisen puhelinlinjan 3,1 kHz:n kaista ja 30 dB:n SNR antavat
noin 31 kbit/s, ja juuri siihen modeemit 1990-luvulla pysähtyivät
(56k-modeemi ohitti rajan vain, koska alalinkin toinen pää oli
digitaalinen). Laskusta näkyy myös, miksi tasojen lisääminen lakkaa
kannattamasta: 32 tasoa riittää jo saavuttamaan rajan.

Kaavan kaksi muuttujaa käyttäytyvät eri tavoin. Kapasiteetti kasvaa
**lineaarisesti** kaistanleveyden mukana mutta vain **logaritmisesti**
SNR:n mukana: kaistan kaksinkertaistaminen kaksinkertaistaa
kapasiteetin, mutta SNR:n kaksinkertaistaminen (+3 dB) lisää vain yhden
bitin hertsiä kohti. Siksi uudet radiojärjestelmät hakevat lisää
kaistaa (5G:n millimetriaallot, Wi-Fi 6E:n 6 GHz) ja rinnakkaisia
kanavia (MIMO) eivätkä lisää tehoa.

## Linkkibudjetti

Linkkibudjetti laskee, mikä SNR vastaanottimessa on. Vastaanotettu
teho on lähetysteho plus antennivahvistukset miinus kaikki vaimennukset.
Kohinan alaraja on lämpökohina: $-174$ dBm hertsiä kohti
huoneenlämmössä. Kun siihen lisätään kaistanleveys desibeleinä ja
vastaanottimen oma kohinaluku (*noise figure*), saadaan kohinataso.
SNR on näiden erotus.

```{.python tiedosto="esimerkit/03-linkkibudjetti.py" osa="budjetti"}
```

```{.tuloste tiedosto="esimerkit/03-linkkibudjetti.odotettu"}
```

Wi-Fi tarvitsee suurelle nopeudelle noin 25 dB:n SNR:n, ja se loppuu
jo kymmenien metrien päässä, kun välissä on seiniä. LoRa toimii
kilometrien päähän, vaikka lähetysteho on pienempi, koska sen kaista on
160-kertaisesti kapeampi (22 dB vähemmän kohinaa) ja koska se levittää
jokaisen bitin pitkälle ajalle niin, että vastaanotin ymmärtää
signaalin vielä kohinan alapuolelta (SNR $-20$ dB). Hinta näkyy
Shannonin kaavasta: LoRan nopeus on satoja bittejä sekunnissa.
Laskelma olettaa vapaan tilan etenemisen; maastossa ja kaupungissa
kantama on selvästi lyhyempi.

## Käytännössä

- **Kysy aina sekä kaistaa että SNR:ää.** Nopeuslupaus ilman
  signaalin laatua on merkityksetön: sama 20 MHz:n Wi-Fi antaa
  41 Mbit/s heikolla ja 166 Mbit/s hyvällä signaalilla.
- **Laske kohinataso kaistasta.** Kapeampi kaista tarkoittaa vähemmän
  kohinaa: 10-kertainen kaventaminen antaa 10 dB parempaa SNR:ää. Tämä
  on IoT-radioiden (LoRa, NB-IoT) pitkän kantaman salaisuus.
- **Shannonin raja on katto, ei tavoite.** Todellinen järjestelmä jää
  rajasta: tarvitaan otsakkeita, opetussignaaleja, suojavälejä ja
  virheenkorjausta. 60–80 % rajasta on tyypillinen tulos.
- **Varaudu adaptiiviseen modulaatioon.** Moderni radio vaihtaa
  modulaatiota ja koodisuhdetta SNR:n mukaan. Käyttäjien nopeus
  vaihtelee siksi paikan ja ajan mukaan, ja kapasiteettisuunnittelu
  tehdään jakaumilla, ei yhdellä luvulla.

## Itsearviointi

- Osaat laskea Shannonin kapasiteetin kaistanleveydestä ja SNR:stä ja
  selittää, miksi kaista kasvattaa kapasiteettia tehokkaammin kuin SNR.
- Osaat selittää Nyquistin ja Shannonin rajojen eron.
- Osaat laatia linkkibudjetin lähetystehosta, antennivahvistuksista,
  vaimennuksista ja kohinatasosta.
- Osaat perustella, miksi kapeakaistainen radio kantaa pidemmälle
  pienemmällä teholla.
