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

```{.ajoituskaavio otsikko="Keskeytyksen käsittelyn vaiheet aika-akselilla (periaatekuva). Taso 1 tarkoittaa, että linja on aktiivinen tai koodi suorituksessa."}
{"signal": [
  {"name": "laitteen keskeytyslinja", "wave": "01.0......."},
  {"name": "yläpuolisko: kuittaus",   "wave": "0.10......."},
  {"name": "keskeytyssäie",           "wave": "0...1.0...."},
  {"name": "odottava prosessi",       "wave": "0.....1..0."}
]}
```

Linja laskee, kun yläpuolisko kuittaa laitteen. Keskeytyssäie pääsee
ajoon vasta, kun vuorontaja valitsee sen, ja herättää lopuksi
prosessin, joka odotti laitetta. Yläpuoliskossa ei saa nukkua, kahdessa
muussa saa.

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

## Asetukset ja tila: sysfs-attribuutit

Laitetiedosto välittää herätykset. Asetuksille ja tilatiedoille
luontevampi paikka on sysfs: ajurimalli tekee jokaisesta laitteesta
hakemiston, ja ajuri voi lisätä siihen *attribuutteja*, jotka näkyvät
tiedostoina. Sääntö on *yksi arvo tiedostoa kohden*, tekstinä ja
rivinvaihtoon päättyen. Ajuri antaa lukufunktion (`show`) ja
tarvittaessa kirjoitusfunktion (`store`):

```{.c tiedosto="esimerkit/03-platform/herate.c" osa="sysfs"}
```

- **`DEVICE_ATTR_RO(nimi)` ja `DEVICE_ATTR_RW(nimi)`** luovat
  attribuutin, jonka funktioiden nimet ovat `nimi_show` ja
  `nimi_store` ja oikeudet `0444` tai `0644`.
- **`sysfs_emit`** kirjoittaa sivun kokoiseen puskuriin ja tarkistaa
  rajat. Vanha tapa `sprintf` ei tarkista.
- **`store`** saa käyttäjän tekstin, joka on jo kopioitu ytimen
  muistiin. Se jäsennetään `kstrto*`-funktiolla, joka hylkää
  roskan ja hyväksyy lopun rivinvaihdon. Paluuarvo on käytetty pituus
  tai negatiivinen virhe.
- **`ATTRIBUTE_GROUPS`** kokoaa attribuutit ryhmäksi, joka annetaan
  ajurin `dev_groups`-kentässä (luku 4). Ajurimalli luo tiedostot, kun
  ajuri sidotaan laitteeseen, ja poistaa ne irrotuksessa.

Ryhmä `dev_groups`-kentässä on parempi kuin `device_create_file`-kutsu
`probe`-funktiossa. Tiedostot syntyvät ennen sidonnasta kertovaa
*uevent*-tapahtumaa (`bind`), joten `udev`-sääntö näkee ne heti, eikä
ajurin tarvitse poistaa niitä itse. sysfs on käyttäjätilan rajapinta,
joten julkaistua attribuuttia ei voi enää poistaa eikä sen muotoa
muuttaa; binääriattribuutit, debugfs ja rajapinnan valinta käsitellään
luvussa 9.

Attribuutti `jakso` tekee herätyksestä jaksollisen: yläpuolisko siirtää
silloin vertailuarvoa eteenpäin jokaisessa keskeytyksessä. Sen
`store`-funktio muuttaa keskeytyksen kanssa jaettua tilaa ja ottaa
siksi saman spinlockin kuin herätyksen asetus.

```{.text tiedosto="esimerkit/03-platform/herate.vaiheet" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/testit/03-herate.odotettu" osa="jakso"}
```

Laskurin ja vertailuarvon arvot riippuvat ajasta, joten testi korvaa ne
pisteillä.

## Viiveet, ajastimet ja muistinvaraus

Sama jako nukkuvaan ja atomiseen kontekstiin ratkaisee, miten ajuri
odottaa ja varaa muistia. Tämän luvun ajuri tarvitsi vain viivästetyn
työn, mutta vaihtoehdot on hyvä tuntea:

| Tarve | Saa nukkua | Atomisessa kontekstissa |
|-------|------------|-------------------------|
| lyhyt viive (mikrosekunteja) | `usleep_range`, `fsleep` | `udelay` (polttaa CPU-aikaa) |
| pitkä viive (millisekunteja) | `msleep` | ei viivettä: ajasta työ tai ajastin |
| myöhemmin ajettava funktio | viivästetty työ (`delayed_work`) | `timer_list` (tarkkuus yksi tikki), `hrtimer` (tarkka) |
| ehdon odotus | `wait_event_timeout`, `readl_poll_timeout` | `readl_poll_timeout_atomic` |
| muistin varaus | `kmalloc(…, GFP_KERNEL)` | `kmalloc(…, GFP_ATOMIC)`, voi epäonnistua herkemmin |

Ajastimen funktio (`timer_list`, `hrtimer`) ajetaan
keskeytyskontekstissa, joten sitä koskevat yläpuoliskon säännöt. Jos
työ tarvitsee mutexia tai väylää, ajastin vain ajastaa työn työjonoon.
Jokainen ajastin ja työ on peruttava `remove`-funktiossa
(`timer_shutdown_sync`, `hrtimer_cancel`, `cancel_delayed_work_sync`).

`kmalloc` antaa fyysisesti yhtenäistä muistia ja sopii pienille
rakenteille; `devm_kzalloc` on sen hallittu, nollaava muoto, jota
`probe` tavallisesti käyttää. Suuret puskurit, joiden ei tarvitse olla
yhtenäisiä, varataan funktiolla `vmalloc` tai `kvmalloc`, joka valitsee
näistä sopivan. Laitteelle annettava muisti varataan DMA-rajapinnalla
(luku 6).

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
- Osaat tehdä laitteelle luettavia ja kirjoitettavia sysfs-attribuutteja
  ja antaa ne ajurin `dev_groups`-kentässä.
- Osaat valita viiveen, ajastimen ja muistinvarauksen sen mukaan, saako
  kontekstissa nukkua.
