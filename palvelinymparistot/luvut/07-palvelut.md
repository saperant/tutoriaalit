# Palvelut ja systemd

Palvelin on olemassa palvelujensa takia, ja Linux-palvelimella
palveluista huolehtii systemd: se käynnistää ne oikeassa järjestyksessä,
käynnistää kaatuneen uudelleen, rajaa sen oikeudet ja resurssit ja
kerää sen lokin. Taito *Komentorivi ja Linux* näytti, miten palvelu
käynnistetään ja sen tila ja loki luetaan. Tässä luvussa ollaan
ylläpitäjän puolella: kirjoitetaan yksikkö omalle palvelulle niin, että
se kestää kaatumiset, on rajattu ja tarkistettu ennen kuin se viedään
yhdellekään koneelle.

Luvun esimerkkinä on pieni TCP-palvelu `mittari`, joka vastaa
komentoon `tila`. Sille kirjoitetaan yksiköt, ne tarkistetaan ja
kovennetaan, ja lopuksi samat tiedostot ajetaan oikean systemd:n alla.

## Asennus on jakelun asia

Käyttöjärjestelmän asennusta ei käydä tässä läpi. Jokaisella jakelulla
on siihen oma, ajan tasalla pidetty ohjeensa, ja suuressa ympäristössä
asennus automatisoidaan jakelun omalla välineellä:

- Ubuntu Server: <https://ubuntu.com/server/docs> (automaattinen
  asennus: autoinstall)
- Debian: <https://www.debian.org/releases/stable/installmanual>
  (automaattinen asennus: preseed)
- Red Hat Enterprise Linux: <https://docs.redhat.com/>; johdannaisista
  esimerkiksi Rocky Linux: <https://docs.rockylinux.org/>
  (automaattinen asennus: Kickstart)
- Pilvessä ja virtuaalikoneissa valmiin levykuvan ensimmäisen
  käynnistyksen asetukset tekee cloud-init: <https://cloud-init.io/>

Tämän tutoriaalin kannalta olennaista on, että asennus tuottaa
mahdollisimman vähän: perusjärjestelmän, verkon ja SSH-yhteyden. Kaikki
muu tulee konfiguraationhallinnasta (luku *Konfiguraationhallinta
Ansiblella*), jolloin kone voidaan rakentaa uudelleen samanlaiseksi.

## Yksikkö kuvaa palvelun

systemd hallitsee *yksiköitä* (unit). Palvelu on yksikkö, samoin
kuuntelusoketti, ajastin, liitospiste ja kohde (target), joka kokoaa
muita yksiköitä yhteen. Yksikkö on tekstitiedosto, joka kuvaa halutun
tilan: mitä ajetaan, minkä jälkeen ja mitä tehdään, kun se kaatuu.
Itse kirjoitetut yksiköt kuuluvat hakemistoon `/etc/systemd/system`,
pakettien mukana tulevat hakemistoon `/usr/lib/systemd/system`.

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.service"}
```

Rivi `Type=` kertoo, milloin systemd pitää palvelua käynnistyneenä.
Valinta ratkaisee, toimivatko riippuvuudet:

| Tyyppi | Palvelu on käynnistynyt, kun | Käyttö |
|-----------|-----------------------------|----------------------------------------------|
| `simple` | prosessi on luotu | oletus; käynnistysvirhe huomataan vasta jälkikäteen |
| `exec` | ohjelman suoritus on alkanut | kuten `simple`, mutta puuttuva ohjelmatiedosto on käynnistysvirhe |
| `notify` | palvelu ilmoittaa itse olevansa valmis | palvelut, joista muut riippuvat |
| `oneshot` | ohjelma on päättynyt | kertaluonteiset työt ja alustukset |
| `forking` | käynnistävä prosessi on päättynyt | vanhat taustalle siirtyvät palvelut |

Tyypin `simple` palvelu on systemd:n mielestä käynnissä heti, vaikka se
kaatuisi sekunnin kuluttua asetusvirheeseen. Siitä riippuva palvelu
käynnistetään silloin liian aikaisin. Uuteen palveluun kannattaa valita
`notify`, jos ohjelman voi saada ilmoittamaan valmiutensa, ja muuten
`exec`.

```{.dot otsikko="Palveluyksikön tilat. Kaatunut palvelu palaa käynnistykseen, jos Restart= sallii sen ja käynnistysraja ei ole täynnä."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.5;
  node [shape=box, style="rounded,filled", fillcolor="#EEF1F4", fontsize=10];
  edge [fontsize=9];
  inactive -> activating [label="start"];
  activating -> active [label="valmis"];
  active -> deactivating [label="stop"];
  deactivating -> inactive;
  activating -> failed [label="virhe tai\naikaraja"];
  active -> failed [label="kaatuu"];
  failed -> activating [label="Restart=,\nRestartSec", style=dashed];
}
```

## Riippuvuus ja järjestys ovat eri asioita

Yksikön `[Unit]`-osiossa on kahdenlaisia viittauksia muihin
yksiköihin, ja ne sekoitetaan usein:

| Asetus | Merkitys |
|--------|----------|
| `Wants=b` | Kun tämä käynnistetään, käynnistetään myös b. b:n epäonnistuminen ei haittaa. |
| `Requires=b` | Kuten `Wants`, mutta jos b ei käynnisty, tätäkään ei käynnistetä. |
| `BindsTo=b` | Kuten `Requires`, ja lisäksi tämä pysäytetään, jos b pysähtyy myöhemmin. |
| `After=b` | Jos molemmat käynnistetään, tämä vasta b:n jälkeen. Ei käynnistä b:tä. |

`Requires` ilman `After`-riviä käynnistää yksiköt rinnakkain, eikä
riippuvuuden epäonnistuminen silloin estä tämän yksikön
käynnistymistä, koska tulosta ei odoteta.
`After` ilman `Wants`- tai `Requires`-riviä taas ei käynnistä mitään.
Tavallisesti tarvitaan molemmat, kuten yllä: `mittari.service` vaatii
sokettinsa ja käynnistyy sen jälkeen. Verkkoa tarvitseva palvelu
kirjoittaa `Wants=network-online.target` ja
`After=network-online.target`.

Riippuvuudeksi valitaan `Wants`, ellei ole selvää syytä muuhun.
`Requires` tekee yhden palvelun viasta usean palvelun vian. Ero näkyy
luvun lopun kokeessa.

## Valmius ja sokettiaktivointi

Palvelu ilmoittaa valmiutensa lähettämällä datagrammin sokettiin, jonka
osoitteen systemd antaa ympäristömuuttujassa `NOTIFY_SOCKET`. Viesti on
tekstiä: `READY=1` kertoo valmiudesta, `STATUS=` on vapaa tilarivi,
joka näkyy komennossa `systemctl status`, ja `WATCHDOG=1` on
elonmerkki. Ohjelmassa tähän riittää muutama rivi, eikä erillistä
kirjastoa tarvita:

```{.python tiedosto="esimerkit/07-palvelu/mittari.py" osa="ilmoitus"}
```

*Sokettiaktivoinnissa* kuuntelusoketin avaa systemd eikä palvelu.
Soketilla on oma yksikkönsä:

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.socket"}
```

Kun sokettiin tulee yhteys, systemd käynnistää samannimisen palvelun ja
antaa sille soketin valmiiksi avattuna tiedostokuvaajana 3. Palvelu
tunnistaa tilanteen ympäristömuuttujista `LISTEN_FDS` ja `LISTEN_PID`:

```{.python tiedosto="esimerkit/07-palvelu/mittari.py" osa="soketti"}
```

Järjestelystä on kolme hyötyä. Portti on auki heti käynnistyksessä,
joten palveluja ei tarvitse käynnistää tietyssä järjestyksessä. Yhteys,
joka tulee palvelun käynnistyessä tai uudelleenkäynnistyessä, jää
ytimen jonoon eikä katkea. Palvelu ei myöskään tarvitse oikeutta avata
porttia itse, joten se voidaan ajaa tavallisena käyttäjänä myös
portissa 443.

Palvelun ja valvojan välinen sopimus on niin pieni, että sen voi
testata ilman systemd:tä. Esimerkin valvoja tekee käynnistyksessä
saman kuin systemd:

```{.python tiedosto="esimerkit/07-palvelu/valvoja.py" osa="kaynnista"}
```

Testi avaa soketin, ottaa siihen yhteyden ennen kuin palvelua on
olemassa, ja käynnistää palvelun vasta sitten:

```{.python tiedosto="esimerkit/07-palvelu/main.py" osa="aktivointi"}
```

```{.tuloste tiedosto="esimerkit/07-palvelu.odotettu" asti="lopetetaan"}
```

Palvelu on tilassa `activating`, kunnes `READY=1` saapuu, ja jonossa
odottanut asiakas saa vastauksensa. Lokirivit palvelu kirjoittaa
vakiovirtaan: systemd ohjaa palvelun vakiotulosteen ja -virheen
journaliin, joten palvelu ei tarvitse omaa lokitiedostoa eikä
lokikirjastoa. Rivin alun `<3>` tai `<6>` kertoo vakavuuden, ja
journal tallentaa sen kenttään `PRIORITY`:

```{.python tiedosto="esimerkit/07-palvelu/mittari.py" osa="loki"}
```

## Uudelleenkäynnistys ja käynnistysraja

`Restart=on-failure` käynnistää palvelun uudelleen, kun se päättyy
virheeseen, signaaliin tai aikarajaan. Hallittu lopetus paluuarvolla 0
ei käynnistä sitä. `Restart=always` käynnistää palvelun myös siistin
lopetuksen jälkeen, mikä harvoin on tarkoitus. `RestartSec` on tauko
ennen uutta yritystä.

Asetusvirheeseen kaatuva palvelu kaatuisi näin loputtomasti. Siksi
käynnistyksillä on raja: `StartLimitBurst=3` ja
`StartLimitIntervalSec=60` sallivat kolme käynnistystä minuutissa, ja
sen jälkeen yksikkö jää tilaan `failed`, kunnes ylläpitäjä puuttuu
asiaan. Esimerkin valvoja toteuttaa saman säännön kolmen
käynnistyksen rajalla, ja palvelu pannaan kaatumaan käynnistyessään
ensin kahdesti ja sitten viidesti:

```{.tuloste tiedosto="esimerkit/07-palvelu.odotettu" alkaen="== palvelu kaatuu 2"}
```

Ohimenevästä viasta palvelu toipuu itse. Pysyvä vika pysäyttää
yritykset, ja tila `failed` on se, josta valvonta hälyttää (luku
*Valvonta ja palvelutasot*).

Kaatuminen on helpoin vika. Jumiin jäänyt palvelu on yhä käynnissä,
mutta ei vastaa. Sitä varten on *vahtikoira*: kun yksikössä on
`WatchdogSec=30`, palvelun on lähetettävä `WATCHDOG=1` vähintään 30
sekunnin välein, tai systemd tappaa sen ja käynnistää uudelleen.
Esimerkkipalvelu lähettää elonmerkin pääsilmukastaan, joten elonmerkki
lakkaa, jos silmukka jumittuu.

## Yksikköjen tarkistus ennen käyttöönottoa

Yksikkötiedoston kirjoitusvirhe ei estä palvelua käynnistymästä:
tuntematon avain ohitetaan varoituksella, ja palvelu käy väärillä
asetuksilla. `systemd-analyze verify` lukee yksiköt samoin kuin
systemd, mutta ei käynnistä mitään, joten sen voi ajaa kehittäjän
koneella ja CI-putkessa:

```{.bash tiedosto="esimerkit/07-yksikot/main.sh" osa="tarkista"}
```

Viallisessa yksikössä on neljä virhettä:

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/rikki.service"}
```

```{.tuloste tiedosto="esimerkit/07-yksikot.odotettu" asti="paluuarvo 1"}
```

Kaksi ensimmäistä ovat varoituksia, joiden jälkeen palvelu olisi
käynnistynyt oletustyypillä ja ilman uudelleenkäynnistystä. Paluuarvo
tekee tarkistuksesta putken vaiheen samaan tapaan kuin Ansible Lint
rooleille.

## Palvelun rajaaminen

Oletuksena palvelu ajetaan pääkäyttäjänä, ja se näkee koko
tiedostojärjestelmän. Murrettu palvelu on silloin murrettu kone.
systemd:llä rajaus tehdään yksikössä, ei ohjelmassa. Mekanismit ovat
samat kuin konteissa (nimiavaruudet, kyvyt, seccomp ja cgroupit,
ks. *Käyttöjärjestelmät*), mutta ne otetaan käyttöön yksi asetus
kerrallaan.

Asetukset kirjoitetaan *lisäystiedostoihin* (drop-in) hakemistoon
`mittari.service.d`. Näin paketin tai sovelluskehittäjän toimittamaa
yksikköä ei muokata, ja ylläpitäjän lisäykset säilyvät päivityksissä.
Komento `systemctl edit mittari.service` luo tällaisen tiedoston.
Ensimmäinen lisäys vaihtaa käyttäjän:

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.service.d/10-kayttaja.conf"}
```

`DynamicUser=yes` varaa palvelulle tunnuksen käynnistyksen ajaksi, joten
käyttäjää ei tarvitse luoda. `StateDirectory=` luo palvelulle
hakemiston `/var/lib/mittari`, joka on ainoa paikka, johon palvelu saa
jättää pysyvää dataa. Toinen lisäys rajaa tiedostojärjestelmän ja
kolmas oikeudet:

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.service.d/20-tiedostot.conf"}
```

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.service.d/30-oikeudet.conf"}
```

`ProtectSystem=strict` liittää koko tiedostojärjestelmän palvelulle
vain luettavaksi, ja `PrivateTmp=yes` antaa sille oman tyhjän
`/tmp`-hakemiston. `SystemCallFilter=@system-service` sallii
tavallisen palvelun tarvitsemat järjestelmäkutsut ja kieltää loput,
esimerkiksi ytimen moduulien latauksen.

`systemd-analyze security` arvioi yksikön altistuksen asteikolla
nollasta kymmeneen. Arvion voi laskea tiedostosta ilman käynnissä
olevaa palvelua:

```{.bash tiedosto="esimerkit/07-yksikot/main.sh" osa="altistus"}
```

```{.tuloste tiedosto="esimerkit/07-yksikot.odotettu" alkaen="== altistus" asti="40-resurssit"}
```

![Altistuksen arvio, kun lisäystiedostot otetaan käyttöön yksi
kerrallaan. Luvut ovat yllä olevasta testatusta
tulosteesta.](kuvat/07-altistus.png){width=78%}

Arvio on tarkistuslista eikä mittaus: se kertoo, mitkä suojaukset ovat
käytössä, ei sitä, onko palvelussa haavoittuvuuksia. Jäljelle jäävät
huomautukset ovat asioita, joita tämä palvelu tarvitsee, kuten verkko:

```{.tuloste tiedosto="esimerkit/07-yksikot.odotettu" alkaen="== mitä arvio" asti="IPAddressDeny"}
```

Kynnysarvolla arviosta saa hyväksymisehdon. Raporttityön yksikkö, jota
ei ole kovennettu yhtä pitkälle, jää kiinni:

```{.bash tiedosto="esimerkit/07-yksikot/main.sh" osa="kynnys"}
```

```{.tuloste tiedosto="esimerkit/07-yksikot.odotettu" alkaen="== kynnysarvo" asti="raportti.service"}
```

Neljäs lisäys ei muuta altistuksen arviota, koska se ei rajaa
oikeuksia vaan kulutusta:

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/mittari.service.d/40-resurssit.conf"}
```

Jokainen palvelu on omassa cgroupissaan, joten rajat koskevat palvelun
kaikkia prosesseja yhdessä. `MemoryMax` ylittyessään tappaa palvelun
(ja `Restart=` käynnistää sen uudelleen) sen sijaan, että koko kone
alkaisi sivuttaa. `systemd-cgtop` näyttää kulutuksen palveluittain.

## Sama oikean systemd:n alla

Edellä yksiköt tarkistettiin tiedostoina. Viimeinen koe asentaa ne
koneeseen, jossa systemd on käynnissä, ja ajaa saman palvelun niiden
alla. Koe ajetaan automaattisesti CI-koneessa, jossa systemd on
prosessi 1. Kehityskontissa ja muissa ympäristöissä, joissa systemd ei
ole käynnissä, koe ohittaa itsensä; tässä näkyvä tuloste on tallennettu
ja sitä verrataan aina, kun koe ajetaan. Omalla testikoneella kokeen voi
ajaa komennolla `make -C esimerkit`.

```{.bash tiedosto="esimerkit/07-elava/aja.bash" osa="asennus"}
```

```{.bash tiedosto="esimerkit/07-elava/aja.bash" osa="aktivointi"}
```

```{.tuloste tiedosto="esimerkit/07-elava/odotettu.txt" asti="NRestarts=0"}
```

Soketti on aktiivinen ja palvelu ei, kunnes ensimmäinen asiakas ottaa
yhteyden. Kovennus näkyy palvelun sisältä, kun palvelulta kysytään sen
ympäristöä: käyttäjä on dynaaminen, `/etc` ei ole kirjoitettavissa ja
oma tilahakemisto on. Resurssirajat näkyvät yksikön ominaisuuksina.

```{.tuloste tiedosto="esimerkit/07-elava/odotettu.txt" alkaen="== kovennus" asti="TasksMax"}
```

Käynnistysrajaa ja riippuvuuksia varten koe luo muutaman pienen yksikön.
`kaatuva.service` päättyy aina virheeseen:

```{.bash tiedosto="esimerkit/07-elava/aja.bash" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/07-elava/odotettu.txt" alkaen="== kaatuva" asti="too quickly"}
```

Kolmen uudelleenkäynnistyksen jälkeen systemd kieltäytyy neljännestä.
Yksiköt `vaatii.service` ja `toivoo.service` riippuvat yksiköstä, jonka
käynnistys epäonnistuu, toinen rivillä `Requires` ja toinen rivillä
`Wants`:

```{.bash tiedosto="esimerkit/07-elava/aja.bash" osa="riippuvuus"}
```

```{.tuloste tiedosto="esimerkit/07-elava/odotettu.txt" alkaen="== Requires"}
```

## Lokit: journald

journald kerää palvelujen tulosteet, ytimen viestit ja syslog-viestit
yhteen lokiin. Jokainen merkintä on joukko kenttiä: viestin ja
vakavuuden lisäksi tallentuvat ainakin yksikkö, prosessin tunniste ja
käyttäjä. Nämä alaviivalla alkavat kentät (`_SYSTEMD_UNIT`, `_PID`,
`_UID`) lisää journald eikä palvelu, joten palvelu ei voi väärentää
niitä. Kokeessa palvelun rivit haetaan ajokerran tunnisteella ja
tulostetaan kaksi kenttää:

```{.bash tiedosto="esimerkit/07-elava/aja.bash" osa="loki"}
```

```{.tuloste tiedosto="esimerkit/07-elava/odotettu.txt" alkaen="== loki" asti="lopetetaan"}
```

Tavallisimmat kyselyt:

| Komento | Näyttää |
|---------|---------|
| `journalctl -u mittari -b` | palvelun merkinnät tämän käynnistyksen ajalta |
| `journalctl -u mittari -p err` | vain virheet ja vakavammat (`PRIORITY` enintään 3) |
| `journalctl -u mittari --since "1 hour ago"` | viimeisen tunnin |
| `journalctl -u mittari -f` | uudet merkinnät sitä mukaa kuin niitä tulee |
| `journalctl -u mittari -o json` | kaikki kentät koneluettavina |
| `journalctl -k -b -1` | ytimen viestit edellisestä käynnistyksestä |

Lokin koko rajataan tiedostossa `/etc/systemd/journald.conf`:
`SystemMaxUse=` on levytilan yläraja ja `MaxRetentionSec=` säilytysaika.
Rajaamaton loki on tavallinen syy levyn täyttymiseen. Yhden koneen loki
ei riitä häiriön selvittämiseen eikä kestä murtoa, joten merkinnät
välitetään keskitettyyn lokipalveluun joko journaldin omalla
välityksellä (`systemd-journal-upload`), syslog-palvelun kautta
(`ForwardToSyslog=yes`) tai lokiagentilla, joka lukee journalia.

## Ajastimet

Toistuva työ on kaksi yksikköä: palvelu, joka tekee työn, ja ajastin,
joka käynnistää sen.

```{.ini tiedosto="esimerkit/07-yksikot/yksikot/raportti.timer"}
```

Croniin verrattuna ajastetulla työllä on samat ominaisuudet kuin
muillakin palveluilla: tuloste menee journaliin, työ voidaan rajata ja
kovettaa, sillä voi olla riippuvuuksia, eikä uusi ajo käynnisty edellisen
päälle. `RandomizedDelaySec` hajottaa ajohetken, jotta sata konetta ei
aloita samaa työtä samalla sekunnilla. Kalenterilausekkeen voi
tarkistaa etukäteen:

```{.bash tiedosto="esimerkit/07-yksikot/main.sh" osa="ajastin"}
```

```{.tuloste tiedosto="esimerkit/07-yksikot.odotettu" alkaen="== ajastimen"}
```

Perjantain jälkeen seuraava ajo on maanantaina. `systemctl list-timers`
näyttää käynnissä olevalla koneella kaikkien ajastimien edellisen ja
seuraavan ajon.

## Kun palvelu ei käynnisty

Vianetsintä etenee aina samassa järjestyksessä: tila, loki, yksikkö,
riippuvuudet.

| Kysymys | Komento |
|------------------------------------------|------------------------------------------|
| Mikä on tila ja viimeisin paluuarvo? | `systemctl status mittari` |
| Mitä palvelu ja systemd sanoivat? | `journalctl -u mittari -b -e` |
| Mitkä asetukset ovat voimassa lisäyksineen? | `systemctl cat mittari` |
| Mitkä yksiköt ovat epäonnistuneet? | `systemctl --failed` |
| Mitä yksikkö vetää mukaansa ja mitä se odottaa? | `systemctl list-dependencies mittari` |
| Mikä hidastaa käynnistystä? | `systemd-analyze critical-chain` ja `blame` |

Seuraava tuloste on mallituloste testikoneelta: yksikön ohjelmatiedosto
puuttuu, ja palvelu on jäänyt käynnistysrajaan.

```text
× kaatuva.service - Esimerkki kaatuvasta palvelusta
     Loaded: loaded (/run/systemd/system/kaatuva.service; static)
     Active: failed (Result: exit-code) since Thu 2026-11-26 07:49:29 UTC
    Process: 5617 ExecStart=/usr/bin/python3 /opt/puuttuu/palvelu.py
             (code=exited, status=2)

systemd[1]: kaatuva.service: Scheduled restart job, restart counter is at 3.
systemd[1]: kaatuva.service: Start request repeated too quickly.
systemd[1]: kaatuva.service: Failed with result 'exit-code'.
```

Tilasta luetaan kolme asiaa. Rivi `Loaded` kertoo, mistä tiedostosta
yksikkö on ladattu, ja paljastaa, jos muokattu tiedosto on eri kuin
käytössä oleva. Rivi `Process` kertoo paluuarvon; arvon selitys on
palvelun omissa lokiriveissä, jotka tässä tapauksessa puuttuvat, koska
ohjelma ei koskaan käynnistynyt. Viesti *Start request repeated too
quickly* tarkoittaa, että varsinainen virhe on aiemmissa riveissä ja
että korjauksen jälkeen laskuri nollataan komennolla
`systemctl reset-failed`.

Tavallisimmat syyt ovat arkisia: yksikköä muokattiin, mutta
`systemctl daemon-reload` jäi ajamatta; kovennus estää hakemiston,
johon palvelu kirjoittaa (lisää `StateDirectory=` tai
`ReadWritePaths=`); `Type=notify`-palvelu ei koskaan lähetä
`READY=1`-viestiä ja kaatuu käynnistyksen aikarajaan.

## Aika palvelimella

Palvelimen kellon on oltava oikeassa kolmesta syystä. Eri koneiden
lokeja ei voi yhdistää häiriön aikajanaksi, jos koneiden kellot
eroavat. Varmenteen voimassaolo tarkistetaan kellosta, joten väärä
kello hylkää kelvollisen varmenteen tai hyväksyy vanhentuneen. Kerberos
hylkää pyynnön, jonka aikaleima poikkeaa yli viisi minuuttia (luku
*Käyttäjähallinta ja hakemistot*).

Kellot tahdistetaan NTP-protokollalla. Asiakas kirjaa kyselyn
lähetysajan $t_1$ ja vastauksen saapumisajan $t_4$ omasta kellostaan,
ja palvelin kirjaa vastaanottoajan $t_2$ ja lähetysajan $t_3$ omastaan.
Näistä saadaan kellojen ero ja verkon kiertoviive:

```{.python tiedosto="esimerkit/07-ntp.py" osa="ntp"}
```

Kaava olettaa, että viesti kulkee kumpaankin suuntaan yhtä kauan. Kun
näin ei ole, arviossa on virhe, joka on puolet suuntien erosta ja aina
enintään puolet kiertoviiveestä:

```{.tuloste tiedosto="esimerkit/07-ntp.odotettu" asti="286.0 ms"}
```

![Kyselyn neljä aikaleimaa, kun meno kestää 20 ms ja paluu 4 ms.
Asiakas ei voi erottaa epäsymmetriaa kellojen erosta, joten arvio on
8 ms pielessä.](kuvat/07-ntp.png){width=80%}

Siksi aikapalvelin valitaan läheltä ja niitä kysytään useita: lyhyt
kiertoviive rajaa virheen pieneksi, ja poikkeava palvelin erottuu
joukosta. Ilman tahdistusta kello ajautuu. Tavallisen kiteen virhe on
kymmeniä miljoonasosia (ppm):

```{.tuloste tiedosto="esimerkit/07-ntp.odotettu" alkaen="ajautuma"}
```

Ubuntu 24.04:ssä oletuksena on `systemd-timesyncd`, joka riittää
asiakkaalle.
Palvelimille asennetaan yleensä **chrony**, joka kysyy useaa lähdettä,
mittaa kellon ajautumisnopeuden ja korjaa sen, ja voi toimia itse
aikapalvelimena muulle verkolle. Tilan näyttävät `timedatectl` ja
`chronyc tracking`, ja lähteet `chronyc sources`. Kelloa korjataan
tavallisesti nopeuttamalla tai hidastamalla sitä (slew), koska
taaksepäin hyppäävä kello rikkoo ohjelmia, jotka mittaavat kestoja
seinäkellosta. Tahdistuksen tila kuuluu valvontaan: hälytys laukeaa,
kun ero ylittää rajan tai lähteitä ei tavoiteta.

## Käytännössä

- **Yksikkö on osa palvelua.** Yksikkötiedostot ja lisäykset ovat
  versionhallinnassa ja kulkevat koneille konfiguraationhallinnalla
  kuten muutkin asetukset.
- **Tarkista ennen käyttöönottoa.** `systemd-analyze verify` ja
  altistuksen kynnysarvo ajetaan putkessa, jolloin kirjoitusvirhe tai
  poistunut kovennus pysäyttää muutoksen.
- **Valmius ilmoitetaan, ei arvata.** `Type=notify` tai
  sokettiaktivointi tekee riippuvuuksista luotettavia; `sleep`
  käynnistysskriptissä ei tee.
- **`Wants` ja `After` oletuksena.** `Requires` vain, kun palvelu on
  todella käyttökelvoton ilman toista.
- **Uudelleenkäynnistys rajalla.** `Restart=on-failure` hoitaa
  ohimenevät viat, käynnistysraja pysäyttää pysyvät, ja tilasta
  `failed` hälytetään.
- **Kovenna lisäystiedostoilla.** Aloita käyttäjästä ja
  tiedostojärjestelmästä, kiristä asetus kerrallaan ja testaa palvelu
  jokaisen jälkeen; jokainen poikkeus perustellaan kommentilla.
- **Loki vakiovirtaan, journal rajattuna.** Palvelu ei hallitse
  lokitiedostoja, journalin koolla on yläraja, ja merkinnät välitetään
  pois koneelta.
- **Kello valvontaan.** Tahdistuksen tila ja ero ovat mittareita siinä
  missä levytila.

## Itsearviointi

- Osaat kirjoittaa palvelulle yksikön ja valita sille tyypin sen
  mukaan, milloin palvelu on käyttövalmis.
- Osaat selittää, miten `Wants`, `Requires` ja `After` eroavat ja mitä
  kustakin seuraa, kun riippuvuus ei käynnisty.
- Osaat toteuttaa palveluun valmiuden ilmoituksen ja valmiina annetun
  kuuntelusoketin käytön ja kertoa, mitä hyötyä sokettiaktivoinnista
  on.
- Osaat valita uudelleenkäynnistyskäytännön ja käynnistysrajan ja
  kertoa, mihin vahtikoiraa tarvitaan.
- Osaat tarkistaa yksikön ilman käynnissä olevaa systemd:tä ja lukea
  `systemd-analyze security` -arvion.
- Osaat rajata palvelun käyttäjän, tiedostojärjestelmän, oikeudet ja
  resurssit lisäystiedostoilla.
- Osaat hakea palvelun lokista merkintöjä kenttien perusteella ja
  rajata journalin koon ja säilytyksen.
- Osaat korvata cron-työn ajastinyksiköllä ja tarkistaa
  kalenterilausekkeen.
- Osaat selvittää järjestyksessä, miksi palvelu ei käynnisty.
- Osaat laskea kellon siirtymän NTP-kyselystä ja perustella, miksi
  palvelimen kello tahdistetaan ja tahdistusta valvotaan.
