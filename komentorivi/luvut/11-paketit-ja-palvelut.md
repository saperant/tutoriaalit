# Paketit, palvelut ja lokit

Ohjelmistot asennetaan Linuxissa paketinhallinnalla, taustapalvelut
käynnistää ja valvoo `systemd`, ja lokit kerää `journald`. Tämä luku
käy läpi Debianin ja Ubuntun työkalut. Fedorassa ja RHEL:ssä
paketinhallinta on `dnf` ja `rpm`, mutta systemd ja journald ovat
samat.

Testikontissa ei ole systemd:tä eikä verkkoa pakettivarastoihin. Siksi
luvun asennus- ja palvelukomennot näytetään ilman testattua tulostetta.

## Paketinhallinta

Paketti sisältää ohjelman tiedostot, riippuvuuksien luettelon ja
asennusskriptit. `apt` hakee paketit varastoista, ratkaisee riippuvuudet
ja käyttää alemman tason työkalua `dpkg`, joka asentaa yksittäisen
paketin.

```text
sudo apt update                  # päivitä pakettiluettelot
apt search --names-only ripgrep  # etsi
apt show ripgrep                 # kuvaus, versio, riippuvuudet
sudo apt install ripgrep         # asenna riippuvuuksineen
apt list --upgradable            # päivitettävät
sudo apt upgrade                 # päivitä asennetut
sudo apt remove ripgrep          # poista (asetukset jäävät)
sudo apt purge ripgrep           # poista asetuksineen
sudo apt autoremove              # tarpeettomat riippuvuudet pois
apt-cache policy nginx           # asennettu ja saatavilla olevat versiot
```

`dpkg` vastaa kysymyksiin asennetusta järjestelmästä ilman verkkoa:
mistä paketista tiedosto tulee, mitä paketti sisältää ja onko se
asennettu:

```{.bash tiedosto="esimerkit/11-paketit.sh" osa="dpkg"}
```

```{.tuloste tiedosto="esimerkit/11-paketit.odotettu"}
```

`dpkg -L paketti` listaa paketin tiedostot. Se kertoo esimerkiksi,
mihin asetustiedosto tai ohjesivu asentui.

Jakelun varastojen lisäksi ohjelmia asennetaan valmistajan omista
varastoista (Docker, PostgreSQL), Snap- ja Flatpak-paketteina tai
kielikohtaisilla paketinhallinnoilla (`pip`, `npm`, `cargo`).
Kielikohtaiset paketit asennetaan projektikohtaisesti
(virtuaaliympäristö, `node_modules`), ei järjestelmään `sudo`:lla, koska
ne voivat rikkoa jakelun omia työkaluja. Ubuntu 24.04 estää
järjestelmän Pythoniin asentamisen oletuksena.

## Palvelut: systemd

systemd käynnistää palvelut, käynnistää kaatuneet uudelleen, hoitaa
riippuvuusjärjestyksen ja kerää tulosteen lokiin. Palvelu kuvataan
*yksikkötiedostolla* (*unit*):

| Komento | Tehtävä |
|---------|---------|
| `systemctl status nginx` | Tila, PID, muisti ja viimeiset lokirivit |
| `sudo systemctl start` / `stop` / `restart nginx` | Käynnistä, pysäytä, käynnistä uudelleen |
| `sudo systemctl reload nginx` | Lue asetukset uudelleen katkaisematta |
| `sudo systemctl enable --now nginx` | Käynnistä nyt ja jokaisella käynnistyksellä |
| `systemctl list-units --failed` | Epäonnistuneet yksiköt |
| `systemctl cat nginx` | Yksikkötiedosto ja sen muutokset |
| `sudo systemctl edit nginx` | Paikallinen muutos (*drop-in*) |
| `sudo systemctl daemon-reload` | Lue muutetut yksikkötiedostot |

Oman palvelun yksikkö kirjoitetaan hakemistoon `/etc/systemd/system`.
Esimerkki ajaa Python-sovelluksen omana käyttäjänään, käynnistää sen
uudelleen kaatumisen jälkeen ja rajaa sen oikeuksia:

```ini
# /etc/systemd/system/varasto.service
[Unit]
Description=Varastopalvelun HTTP-rajapinta
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
User=varasto
Group=varasto
WorkingDirectory=/opt/varasto
EnvironmentFile=/etc/varasto/ymparisto
ExecStart=/opt/varasto/venv/bin/python -m varasto --portti 8080
Restart=on-failure
RestartSec=5
UMask=0027
MemoryMax=512M
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/lib/varasto

[Install]
WantedBy=multi-user.target
```

Palvelu kirjoittaa lokinsa tulosteeseen. systemd ohjaa sen journaliin,
joten sovelluksen ei tarvitse hallita lokitiedostoja. Lopetus lähettää
`TERM`-signaalin ja aikarajan jälkeen `KILL`-signaalin (luku
*Prosessit ja signaalit*).

Kun yksikkö on otettu käyttöön (`sudo systemctl enable --now varasto`),
`systemctl status varasto` näyttää tilan ja viimeiset lokirivit:

```text
● varasto.service - Varastopalvelun HTTP-rajapinta
     Loaded: loaded (/etc/systemd/system/varasto.service; enabled)
     Active: active (running) since Mon 2025-03-10 08:02:11 EET; 2h ago
   Main PID: 912 (python)
     Memory: 48.3M (max: 512.0M)

Mar 10 08:02:11 palvelin systemd[1]: Started varasto.service.
Mar 10 08:02:12 palvelin python[912]: Kuunnellaan porttia 8080
```

Rivi `Loaded` kertoo, mistä yksikkö luettiin ja käynnistyykö se koneen
käynnistyessä (`enabled`). Rivi `Active` kertoo tilan. Kaatunut palvelu
näyttää tältä:

```text
× varasto.service - Varastopalvelun HTTP-rajapinta
     Loaded: loaded (/etc/systemd/system/varasto.service; enabled)
     Active: failed (Result: exit-code) since Mon 2025-03-10 10:31:40 EET
    Process: 5120 ExecStart=/opt/varasto/venv/bin/python … (code=exited,
             status=1/FAILURE)

Mar 10 10:31:40 palvelin python[5120]: FileNotFoundError: asetukset.toml
Mar 10 10:31:40 palvelin systemd[1]: varasto.service: Failed with result
                                     'exit-code'.
```

Syy on lähes aina viimeisillä lokiriveillä: tässä sovellus ei löytänyt
asetustiedostoaan ja päättyi paluuarvoon 1. `Restart=on-failure` yrittää
käynnistystä uudelleen, mutta toistuvien epäonnistumisten jälkeen
systemd luovuttaa ja tila jää arvoon `failed`.

## Ajastetut tehtävät

Toistuvat tehtävät, kuten varmuuskopiot ja siivoukset, ajastetaan
perinteisesti `cron`-palvelulla. Komento `crontab -e` avaa käyttäjän
ajastustaulun editoriin. Jokaisella rivillä on viisi aikakenttää
(minuutti, tunti, kuukaudenpäivä, kuukausi, viikonpäivä) ja komento:

```text
# min tunti pv kk vkpv  komento
30    3     *  *  *     /usr/local/bin/varmuuskopioi
*/15  *     *  *  1-5   /usr/local/bin/tarkista-levytila
```

Ensimmäinen rivi ajetaan joka yö kello 3.30 ja toinen arkisin vartin
välein. cron ajaa komennot suppealla ympäristöllä (lyhyt `PATH`, ei
kuoren asetustiedostoja), joten komennot kirjoitetaan täysillä poluilla
ja tuloste ohjataan lokiin.

systemd-ajastin tekee saman kahdella yksiköllä: `.service` kertoo,
mitä ajetaan, ja samanniminen `.timer`, milloin:

```ini
# /etc/systemd/system/varmuuskopio.service
[Unit]
Description=Yöllinen varmuuskopio

[Service]
Type=oneshot
ExecStart=/usr/local/bin/varmuuskopioi

# /etc/systemd/system/varmuuskopio.timer
[Unit]
Description=Ajaa varmuuskopion joka yö

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Ajastin otetaan käyttöön komennolla `sudo systemctl enable --now
varmuuskopio.timer`, ja `systemctl list-timers` näyttää seuraavan ja
edellisen ajon. Ajastimen etuja cronin riviin verrattuna ovat loki
journalissa, riippuvuudet muihin yksiköihin ja `Persistent=true`, joka
ajaa väliin jääneen ajon, kun kone käynnistyy.

## Lokit

`journalctl` lukee systemd:n keräämää lokia:

```text
journalctl -u nginx               # yhden palvelun loki
journalctl -u nginx -f            # seuraa
journalctl -u nginx --since "1 hour ago" -p warning
journalctl -b -p err              # tämän käynnistyksen virheet
journalctl -k                     # ytimen viestit (vrt. dmesg)
journalctl -u ssh -o cat          # pelkät viestit ilman aikaleimoja
journalctl -u nginx -o json       # rakenteinen muoto jq:lle
```

Jokaisella rivillä on aikaleima, koneen nimi, prosessi ja sen PID sekä
viesti:

```text
$ journalctl -u ssh -n 3
Mar 10 08:14:02 palvelin sshd[4100]: Accepted publickey for aino from
    192.0.2.44 port 51234 ssh2: ED25519 SHA256:kq1Zr0v…
Mar 10 08:14:02 palvelin sshd[4100]: pam_unix(sshd:session): session
    opened for user aino(uid=1000) by (uid=0)
Mar 10 09:02:51 palvelin sshd[4391]: Invalid user admin from
    203.0.113.9 port 40022
```

Perinteiset tekstilokit ovat hakemistossa `/var/log` (esim. `syslog`,
`auth.log`, `nginx/access.log`). Molemmat käsitellään edellisten
lukujen työkaluilla. Esimerkki laskee ssh-palvelun epäonnistuneet
kirjautumiset lähdeosoitteittain ja poimii olemattomat käyttäjätunnukset,
joita on yritetty:

```{.bash tiedosto="esimerkit/11-lokit.sh" osa="aineisto"}
```

```{.bash tiedosto="esimerkit/11-lokit.sh" osa="analyysi"}
```

```{.tuloste tiedosto="esimerkit/11-lokit.odotettu"}
```

Kenttää ei poimita sijainnin mukaan, koska `invalid user` muuttaa
kenttien määrää. Awk etsii sanan `from` ja tulostaa sitä seuraavan
kentän. Tällainen analyysi on peruste estää osoite palomuurissa tai
ottaa käyttöön `fail2ban`.

## Käytännössä

- **Jakelun paketti ensin.** Se päivittyy tietoturvapäivitysten
  mukana. Asenna muualta vain, kun versio on liian vanha, ja kirjaa
  silloin, mistä ja miksi.
- **Älä `sudo pip install`.** Järjestelmän Python kuuluu jakelulle.
  Käytä virtuaaliympäristöä tai `pipx`:ää.
- **Muutokset yksikköihin `systemctl edit`-komennolla.** Drop-in-
  tiedosto säilyy paketin päivityksessä, toisin kuin muokattu
  alkuperäinen.
- **Palvelu tulostaa, systemd kirjaa.** Älä toteuta lokitiedostojen
  kiertoa sovellukseen. Rakenteinen loki (JSON) helpottaa myöhempää
  analyysia.
- **Vianetsinnän aloitus**: `systemctl status palvelu` ja
  `journalctl -u palvelu -n 50`. Virhe on lähes aina viimeisillä
  riveillä.
- **Rajaa palvelun oikeudet yksikössä** (`User=`, `ProtectSystem=`,
  `NoNewPrivileges=`). `systemd-analyze security palvelu` arvioi
  rajauksen.

## Itsearviointi

- Osaat etsiä, asentaa, päivittää ja poistaa paketteja `apt`:lla ja
  selvittää `dpkg`:lla, mistä paketista tiedosto on peräisin.
- Osaat käynnistää, pysäyttää ja ottaa käyttöön palvelun sekä
  kirjoittaa oman palvelun yksikkötiedoston.
- Osaat lukea `systemctl status` -tulosteesta, onko palvelu käynnissä
  ja miksi se kaatui.
- Osaat ajastaa toistuvan tehtävän cronilla tai systemd-ajastimella.
- Osaat lukea palvelun lokia `journalctl`-komennolla ajan ja tason
  mukaan rajattuna.
- Osaat analysoida kirjautumislokin ja tunnistaa salasanojen
  arvausyritykset.
