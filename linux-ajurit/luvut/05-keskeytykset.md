# Keskeytykset ja lukitus

Bare-metal-ohjelmassa keskeytyskäsittelijä on vektoritaulun funktio,
joka kuittaa laitteen ja asettaa lipun pääsilmukalle (*Mikrokontrollerit
ja bare-metal-ohjelmointi*). Linuxissa periaate on sama, mutta
välissä on kerroksia: keskeytysohjaimen ajuri, ytimen yleinen
keskeytyskäsittely ja ajurin rekisteröimä käsittelijä. Lisäksi ytimessä
on monta suorituskontekstia, joista jokaisella on omat sääntönsä.

Luvun ajuri on luvun 4 herätysajastin. PL031 nostaa keskeytyksen, kun
sen laskuri saavuttaa vertailurekisterin arvon.

## Keskeytyksen polku

QEMU:n virt-koneen keskeytysohjain on ARM:n GIC. Laitepuun
`interrupts = <0x00 0x02 0x04>` tarkoittaa GIC:n jaettua keskeytystä
(SPI, 0) numero 2 tasoliipaistuna (4). GIC numeroi jaetut keskeytykset
32:sta alkaen, joten laitteistonumero on 34. Ydin antaa sille oman
*virtuaalisen* keskeytysnumeronsa, jota ajuri käyttää ja joka näkyy
tiedoston `/proc/interrupts` ensimmäisessä sarakkeessa:

```{.tuloste tiedosto="esimerkit/testit/03-herate.odotettu" osa="keskeytys"}
```

Keskeytyksen tullessa GIC:n ajuri selvittää laitteistonumeron,
keskeytysalue (*irq domain*) muuntaa sen virtuaaliseksi, ja ydin kutsuu
rekisteröityjä käsittelijöitä. Ajurin ei tarvitse tietää GIC:stä
mitään: sama ajuri toimii piirissä, jonka keskeytysohjain on toinen tai
jossa keskeytys kulkee GPIO-ohjaimen kautta.

## Ylä- ja alapuolisko

Keskeytyskäsittelijä ajetaan *keskeytyskontekstissa*: se keskeyttää
mitä tahansa, mitä CPU juuri teki, eikä se saa nukkua. Se ei siis saa
ottaa mutexia, varata muistia `GFP_KERNEL`-lipulla, kopioida käyttäjän
muistiin eikä odottaa laitetta pitkään. Siksi työ jaetaan kahteen
osaan:

- **Yläpuolisko** (*top half*) tekee vain kiireellisen: tarkistaa, että
  keskeytys on tämän laitteen, kuittaa sen ja tallentaa tilan.
- **Alapuolisko** (*bottom half*) tekee loput myöhemmin kontekstissa,
  jossa saa nukkua.

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="keskeytys"}
```

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="tila"}
```

Rekisteröinti tapahtuu `probe`-funktiossa funktiolla
`devm_request_threaded_irq` (luku 4). Yläpuoliskon paluuarvo kertoo
ytimelle, mitä tehdään:

| Paluuarvo | Merkitys |
|----------------|------------------------------------------|
| `IRQ_NONE` | keskeytys ei ollut tämän laitteen; jaettu linja kysyy seuraavaa käsittelijää |
| `IRQ_HANDLED` | käsitelty, alapuoliskoa ei tarvita |
| `IRQ_WAKE_THREAD` | herätä keskeytyssäie, joka ajaa alapuoliskon |

Tasoliipaistu keskeytys on kuitattava yläpuoliskossa, muuten linja pysyy
aktiivisena ja käsittelijä kutsutaan heti uudelleen. Jos laitetta ei
voi kuitata nopeasti, esimerkiksi I2C-laitteen rekisteri luetaan väylän
yli, ydin pitää linjan peitettynä, kunnes säie on valmis. Se pyydetään
lipulla `IRQF_ONESHOT`, ja yläpuoliskoksi annetaan `NULL`. Ytimen
`irq_default_primary_handler` herättää silloin pelkän säikeen.

Alapuoliskon vaihtoehdot:

| Keino | Konteksti | Saa nukkua | Käyttö |
|--------------|----------------|------|-----------------------------|
| keskeytyssäie | oma ytimen säie | kyllä | useimmat ajurit, väylän yli luettavat laitteet |
| työjono (`workqueue`) | yhteinen ytimen säie | kyllä | viivästetyt ja ajastetut työt |
| tasklet ja softirq | keskeytyksen jälkeen, atominen | ei | verkko- ja lohkopino; taskletit ovat vanhentumassa |

## Työjono: vahtikoira

Ajuri asettaa herätyksen yhteydessä viivästetyn työn, joka varoittaa,
jos keskeytystä ei kuulu. Keskeytyssäie peruu työn:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="vahti"}
```

`mod_delayed_work` asettaa tai siirtää työn, ja
`cancel_delayed_work_sync` (funktiossa `remove`) odottaa käynnissä
olevan työn loppuun, ennen kuin ajurin tila vapautetaan. Unohtunut
peruutus on tyypillinen ajurivirhe: moduuli poistetaan, ja työjono
kutsuu myöhemmin funktiota, jota ei ole.

Vahti paljastaa viallisen laitepuun. Esimerkki `vaara.dtsi` antaa
laitteelle väärän keskeytysnumeron:

```{.c tiedosto="esimerkit/03-platform/vaara.dtsi"}
```

```{.tuloste tiedosto="esimerkit/testit/03-vahti.odotettu"}
```

Raakatila `RTCRIS=1` kertoo, että laite nosti keskeytyksen, mutta se
ei tullut perille. Vika on siis keskeytyksen reitissä eikä laitteessa.
Tämä on oikeassa laitteessa yleinen vika: laitepuussa on väärä numero,
väärä liipaisutapa tai väärä keskeytysohjain (`interrupt-parent`).

## Lukitus konteksteittain

Ajurin tila on yhteistä kolmelle kontekstille: prosessille, joka lukee
tai kirjoittaa laitetta, keskeytyksen yläpuoliskolle ja
keskeytyssäikeelle. Lukon valinta riippuu siitä, missä kontekstissa
tilaa käytetään:

| Lukko | Nukkuminen lukossa | Keskeytyksessä | Käyttö |
|------------------|----------|-------------|--------------------------|
| `mutex` | kyllä | ei | prosessikonteksti, pitkät toiminnot |
| `spinlock` | ei | kyllä | lyhyt kriittinen osa |
| `spin_lock_irqsave` | ei | — | prosessissa, kun samaa lukkoa käytetään keskeytyksessä |
| atominen muuttuja, `READ_ONCE` | — | kyllä | yksittäinen laskuri tai lippu |

Jos prosessi ottaisi tavallisen spinlockin ja keskeytys tulisi samalle
CPU:lle, yläpuolisko jäisi pyörimään lukkoon, jota prosessi ei koskaan
vapauta. Siksi prosessikontekstissa käytetään `spin_lock_irqsave`-
funktiota, joka estää keskeytykset paikallisesti lukon ajaksi:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="aseta"}
```

Herätyksen asetus käyttää kahta lukkoa: mutex sarjallistaa asettajat
(prosessit, joille nukkuminen on sallittua), ja spinlock suojaa
keskeytyksen kanssa jaetut kentät ja rekisterit. Lukkojen järjestys on
aina sama: ensin mutex, sitten spinlock. Lukkojärjestyksen rikkominen
löytyy lockdep-tarkistimella (luku 10).

## Laite käyttäjälle

Ajuri rekisteröi `miscdevice`-laitteen `/dev/herate`. Kirjoitus asettaa
herätyksen, luku odottaa sitä ja `poll` kertoo, onko herätys tapahtunut:

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="misc"}
```

Odottaminen on sama malli kuin luvun 3 jonossa: ehto tarkistetaan,
`wait_event_interruptible` nukkuu ja keskeytyssäie herättää.
`kstrtou32_from_user` kopioi ja jäsentää käyttäjän kirjoittaman luvun
yhdellä kutsulla. Testiohjelma asettaa herätyksen ja odottaa sitä
`poll`-kutsulla:

```{.c tiedosto="esimerkit/03-platform/heratetesti.c" osa="odota"}
```

Jaksollisessa tilassa yläpuolisko siirtää vertailuarvoa eteenpäin
jokaisessa keskeytyksessä. Jakso asetetaan sysfs-attribuutilla (luku 9):

```{.text tiedosto="esimerkit/03-platform/herate.vaiheet" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/testit/03-herate.odotettu" osa="jakso"}
```

Laskurin ja vertailuarvon arvot riippuvat ajasta, joten testi korvaa ne
pisteillä.

## Käytännössä

- **Tee yläpuoliskossa vain välttämätön.** Tarkista, onko keskeytys
  tämän laitteen, kuittaa se ja siirrä loput keskeytyssäikeelle.
- **Kuittaa tasoliipaistu keskeytys yläpuoliskossa tai käytä
  `IRQF_ONESHOT`-lippua.** Muuten käsittelijä kutsutaan uudelleen
  loputtomasti, ja ydin lopulta poistaa linjan käytöstä.
- **Valitse lukko kontekstin mukaan.** Keskeytyksen kanssa jaettu tila
  vaatii spinlockin ja prosessikontekstissa `spin_lock_irqsave`-
  funktion. Muuten mutex.
- **Pysäytä laite ja peru työt ennen tilan vapautusta.** Peitä
  keskeytys laitteesta ja kutsu `cancel_*_sync` funktiossa `remove`.
- **Lisää ajuriin vahti laitteelle, joka voi jäädä vastaamatta.**
  Aikaraja ja selkeä lokiviesti säästävät tunteja vianetsinnässä.

## Itsearviointi

- Osaat selittää keskeytyksen polun laitteesta GIC:n kautta ajurin
  käsittelijään sekä laitteisto- ja virtuaalisen keskeytysnumeron eron.
- Osaat jakaa käsittelyn yläpuoliskoon ja keskeytyssäikeeseen ja valita
  oikean paluuarvon.
- Osaat käyttää viivästettyä työtä ja perua sen turvallisesti laitteen
  irrotuksessa.
- Osaat valita mutexin, spinlockin ja `spin_lock_irqsave`-funktion
  välillä sen mukaan, missä kontekstissa tilaa käytetään.
