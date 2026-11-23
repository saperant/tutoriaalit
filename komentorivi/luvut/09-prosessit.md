# Prosessit ja signaalit

Jokainen käynnissä oleva ohjelma on prosessi, jolla on tunniste (PID),
vanhempi, käyttäjä, avoimet tiedostot ja tila. Kuori luo prosessin
jokaiselle ulkoiselle komennolle ja odottaa sen päättymistä, ellei
komentoa käynnistetä taustalle. Tässä luvussa käsitellään prosessien
seuraamista, lopettamista ja resurssien rajaamista.

## Prosessien tarkastelu

| Komento | Tehtävä |
|---------|---------|
| `ps aux` | Kaikki prosessit: käyttäjä, PID, CPU, muisti, komento |
| `ps -ef --forest` | Vanhempi-lapsi-puu |
| `ps -o pid,ni,rss,args -p PID` | Valitut sarakkeet yhdestä prosessista |
| `pgrep -a nginx`, `pgrep -f malli` | PID:t nimen tai komentorivin mukaan |
| `top`, `htop` | Reaaliaikainen näkymä; `P` CPU:n, `M` muistin mukaan |
| `/proc/PID/` | Ytimen tiedot: `cmdline`, `status`, `fd/`, `environ` |
| `lsof -p PID`, `lsof -i :8080` | Avoimet tiedostot, porttia kuunteleva prosessi |
| `ss -tlnp` | Kuuntelevat TCP-portit ja prosessit |
| `free -h`, `uptime` | Muisti, kuormitus |

`ps` ja `top` lukevat tietonsa hakemistosta `/proc`, jota voi lukea
myös suoraan. `cmdline` erottaa argumentit nollatavuilla:

```{.bash tiedosto="esimerkit/09-tyot.sh" osa="tausta"}
```

`$!` on viimeksi taustalle käynnistetyn prosessin PID. `kill -0`
ei lähetä signaalia vaan tarkistaa, onko prosessi olemassa ja onko
siihen oikeus.

*Kuormitus* (`uptime`: *load average*) on ajoa odottavien ja levyä
odottavien prosessien keskimääräinen määrä 1, 5 ja 15 minuutin ajalta.
Sitä verrataan suoritinytimien määrään (`nproc`).

## Signaalit

Signaali on ytimen välittämä ilmoitus prosessille. Prosessi voi
käsitellä useimmat signaalit itse, esimerkiksi siivota ja lopettaa
hallitusti, mutta `KILL`- ja `STOP`-signaaleja ei voi käsitellä.

| Signaali | Numero | Tavallinen merkitys |
|----------|--------|---------------------|
| `HUP` | 1 | Pääte suljettiin; palvelut: lue asetukset uudelleen |
| `INT` | 2 | Ctrl+C |
| `QUIT` | 3 | Ctrl+\\, lopeta ja tee muistivedos |
| `KILL` | 9 | Lopeta heti, ei käsittelyä eikä siivousta |
| `TERM` | 15 | Pyyntö lopettaa hallitusti; `kill`-komennon oletus |
| `STOP`, `CONT` | 19, 18 | Pysäytä, jatka (Ctrl+Z lähettää `TSTP`) |
| `PIPE` | 13 | Putken lukija lopetti |

Signaalin tappaman prosessin paluuarvo on 128 + signaalin numero:

```{.bash tiedosto="esimerkit/09-tyot.sh" osa="lopetus"}
```

```{.tuloste tiedosto="esimerkit/09-tyot.odotettu"}
```

Lopettamisen oikea järjestys on `TERM`, odotus ja vasta sitten `KILL`.
`KILL` ei anna prosessille mahdollisuutta tyhjentää puskureita, poistaa
lukkotiedostoja tai sulkea tietokantayhteyksiä. Järjestelmänhallinta
(`systemctl stop`) ja konttien ajoympäristöt toimivat samoin: ensin
`TERM`, ja `KILL` vasta aikarajan jälkeen.

## Työt ja taustaprosessit

Vuorovaikutteisessa kuoressa komento voidaan käynnistää taustalle
(`komento &`) tai pysäyttää (Ctrl+Z) ja siirtää taustalle (`bg`) tai
etualalle (`fg`). `jobs` listaa kuoren työt. Työt ovat kuoren lapsia ja
saavat `HUP`-signaalin, kun pääte suljetaan.

```text
$ ./pitka-ajo.sh > ajo.log 2>&1 &
[1] 4182
$ jobs
[1]+  Running    ./pitka-ajo.sh > ajo.log 2>&1 &
$ fg %1        # takaisin etualalle; Ctrl+Z ja bg taustalle
```

Jos ajon on jatkuttava uloskirjautumisen jälkeen, vaihtoehdot ovat:

- `nohup komento > ajo.log 2>&1 &` jättää `HUP`-signaalin huomiotta.
- `tmux` tai `screen` pitää koko istunnon käynnissä, ja siihen voi
  palata myöhemmin, myös toiselta koneelta (luku *Etäkäyttö: ssh*).
- `systemd-run --user komento` tai oma palveluyksikkö, kun ajo on
  pysyvä (luku *Paketit, palvelut ja lokit*).

## Aikarajat

`timeout` lopettaa komennon, joka kestää liian kauan. Sen paluuarvo 124
erottaa aikarajan komennon omasta virheestä. `--preserve-status`
palauttaa sen sijaan lopetetun komennon arvon (143 = `TERM`):

```{.bash tiedosto="esimerkit/09-timeout.sh" osa="timeout"}
```

```{.tuloste tiedosto="esimerkit/09-timeout.odotettu"}
```

Aikaraja kuuluu jokaiseen automaatioon, joka odottaa verkkoa tai muuta
ulkoista resurssia. Jumiutunut komento pysäyttää muuten koko putken.

## Prioriteetti ja resurssirajat

`nice` alentaa prosessin suoritinprioriteettia arvolla 0–19.
Korkeampi arvo antaa suorittimen herkemmin muille. Raskaat eräajot,
kuten varmuuskopiot ja käännökset, kannattaa ajaa näin jaetulla
koneella. Levyn käytölle sama työkalu on `ionice -c3`. Käynnissä olevan
prosessin prioriteettia muutetaan komennolla `renice`.

`ulimit` asettaa kuoren ja sen lasten resurssirajat: muistin, avoimien
tiedostojen määrän (`-n`) ja muistivedoksen koon (`-c`). Alikuori
rajaa vaikutuksen yhteen komentoon:

```{.bash tiedosto="esimerkit/09-nice.sh" osa="nice"}
```

```{.bash tiedosto="esimerkit/09-nice.sh" osa="ulimit"}
```

```{.tuloste tiedosto="esimerkit/09-nice.odotettu"}
```

Palveluille rajat asetetaan pysyvästi palveluyksikössä
(`MemoryMax=`, `LimitNOFILE=`). Virhe *Too many open files* korjataan
nostamalla `LimitNOFILE`-rajaa tai etsimällä vuotavat tiedostokahvat
(`ls /proc/PID/fd | wc -l`).

## Käytännössä

- **`TERM` ensin, `KILL` viimeisenä keinona.** `kill -9` on refleksi,
  joka jättää jälkeensä rikkinäisiä tiloja.
- **Etsi prosessi tarkasti**: `pgrep -a` näyttää komentorivin ennen
  kuin `pkill` lopettaa väärän prosessin. `pkill -f python` lopettaa
  kaikki Python-ohjelmat.
- **Mikä kuuntelee porttia?** `ss -tlnp` tai `lsof -i :PORTTI`. Tämä
  ratkaisee virheen *Address already in use*.
- **Pitkät ajot `tmux`-istuntoon** etäkoneella. Katkennut yhteys ei
  silloin keskeytä ajoa.
- **Aikaraja kaikkeen, mikä odottaa** verkkoa, lukkoa tai toista
  prosessia.
- **Hidas kone**: `uptime` (kuormitus), `top` (kuka käyttää suoritinta
  tai muistia), `free -h` (onko muisti loppu), `df -h` (onko levy
  täynnä). Tämä järjestys löytää useimmat syyt minuutissa.

## Itsearviointi

- Osaat löytää prosessin nimen, komentorivin tai portin perusteella ja
  tutkia sen tietoja hakemistosta `/proc`.
- Osaat lopettaa prosessin hallitusti ja tulkita paluuarvon
  128 + signaali.
- Osaat pitää ajon käynnissä uloskirjautumisen jälkeen ja kertoa
  vaihtoehtojen erot.
- Osaat asettaa komennolle aikarajan, alentaa sen prioriteettia ja
  rajata sen resursseja.
