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

Ajastetut tehtävät tehdään perinteisesti `cron`-palvelulla
(`crontab -e`, rivi `30 3 * * * /usr/local/bin/varmuuskopioi`) tai
systemd-ajastimella (`.timer`-yksikkö). Ajastimen etuja ovat loki
journalissa, riippuvuudet ja `Persistent=true`, joka ajaa väliin
jääneen ajon, kun kone käynnistyy.

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
- Osaat lukea palvelun lokia `journalctl`-komennolla ajan ja tason
  mukaan rajattuna.
- Osaat analysoida kirjautumislokin ja tunnistaa salasanojen
  arvausyritykset.
