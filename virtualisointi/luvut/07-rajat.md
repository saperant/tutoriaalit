# Kontit: cgroups, kyvyt ja seccomp

Nimiavaruudet rajaavat sen, mitä prosessi näkee. Tämä luku käsittelee
kolme mekanismia, jotka rajaavat sen, mitä prosessi saa tehdä:
**cgroups** rajoittaa resursseja, **kyvyt** pilkkovat rootin oikeudet
ja **seccomp** suodattaa järjestelmäkutsuja. Konttiajoympäristö
asettaa kaikki kolme jokaiselle kontille.

## cgroups v2

**cgroup** (control group) on prosessiryhmä, jonka resurssien käyttöä
ydin mittaa ja rajoittaa. Ryhmät muodostavat hierarkian, joka näkyy
tiedostojärjestelmänä hakemistossa `/sys/fs/cgroup`. Ryhmä luodaan
hakemistona, prosessi siirretään kirjoittamalla sen numero tiedostoon
`cgroup.procs`, ja rajat asetetaan kirjoittamalla ohjaimen tiedostoihin.

| Ohjain | Tiedosto | Rajaa |
|--------|----------|-------|
| memory | `memory.max`, `memory.high` | muistin kovan ja pehmeän rajan |
| cpu | `cpu.max`, `cpu.weight` | suoritinajan kiintiön ja painon |
| io | `io.max`, `io.weight` | levyn läpäisyn ja IOPS:n |
| pids | `pids.max` | prosessien ja säikeiden määrän |
| cpuset | `cpuset.cpus`, `cpuset.mems` | sallitut ytimet ja NUMA-solmut |

Versio 2 (cgroups v2) on nykyisissä jakeluissa oletus: hierarkia on
yksi, ja ohjaimet otetaan käyttöön alaryhmille tiedostolla
`cgroup.subtree_control`. Vanhemmassa versiossa 1 jokaisella ohjaimella
oli oma hierarkiansa. systemd käyttää cgroupeja kaikille palveluille,
joten jokainen palvelu on jo omassa ryhmässään
(`systemd-cgls`, `systemctl status`).

## Prosessiraja käytännössä

Seuraava esimerkki luo ryhmän, jonka prosessiraja on viisi, ja yrittää
käynnistää siinä kymmenen lasta. Esimerkki toimii sekä v2:lla että
v1:llä:

```{.bash tiedosto="esimerkit/valinnaiset/cgroups/pids.sh" osa="ryhma"}
```

```{.bash tiedosto="esimerkit/valinnaiset/cgroups/pids.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/valinnaiset/cgroups/pids.odotettu"}
```

Python itse on yksi ryhmän viidestä tehtävästä, joten lapsia
käynnistyy neljä. Loput `fork`-kutsut epäonnistuvat virheellä
`EAGAIN`. Sama raja estää kontin sisällä haarukkapommin (fork bomb)
kaatamasta koko isäntää. Esimerkki tarvitsee kirjoitettavan
cgroup-tiedostojärjestelmän, jota konttien sisällä ei yleensä ole,
joten esimerkkien Makefile ajaa sen vain, jos ryhmän voi luoda.

Muistirajan ylitys toimii toisin: ydin yrittää ensin vapauttaa
välimuisteja, ja jos se ei riitä, ryhmän sisällä käynnistyy
**OOM-tappaja**, joka lopettaa ryhmän prosessin. Kontin sovellus näkee
tämän SIGKILLinä (paluuarvo 137) ilman varoitusta, ellei se seuraa
omaa muistinkäyttöään. `memory.high` hidastaa prosessia ennen kovaa
rajaa ja antaa sille mahdollisuuden reagoida.

## Kyvyt

Perinteisessä Unixissa root saa kaiken ja muut eivät mitään.
**Kyvyt** (capabilities) pilkkovat rootin oikeudet noin 40 osaan, joita
voi antaa ja poistaa erikseen:

| Kyky | Sallii |
|------|--------|
| `CAP_NET_BIND_SERVICE` | porttien < 1024 sitomisen |
| `CAP_NET_ADMIN` | verkkoasetukset, palomuurin, reitit |
| `CAP_CHOWN` | tiedostojen omistajan vaihtamisen |
| `CAP_SYS_ADMIN` | liitokset, nimiavaruudet ja paljon muuta ("uusi root") |
| `CAP_SYS_PTRACE` | toisten prosessien jäljittämisen |
| `CAP_DAC_OVERRIDE` | tiedosto-oikeuksien ohittamisen |

Docker antaa kontin rootille oletuksena 14 kykyä. Esimerkiksi
`CAP_SYS_ADMIN` ja `CAP_NET_ADMIN` puuttuvat, joten kontin root ei voi
liittää tiedostojärjestelmiä eikä muuttaa verkkoa. Kun kyky poistetaan,
root on sen osalta tavallinen käyttäjä:

```{.bash tiedosto="esimerkit/07-kyvyt.sh" osa="pudotus"}
```

Toiseen suuntaan kyvyn voi antaa ohjelmalle ilman rootia.
**Ambient**-kyky periytyy `exec`-kutsun yli, joten palvelu voi
kuunnella porttia 80 tavallisena käyttäjänä:

```{.bash tiedosto="esimerkit/07-kyvyt.sh" osa="lisays"}
```

```{.tuloste tiedosto="esimerkit/07-kyvyt.odotettu"}
```

## seccomp

Linuxissa on yli 350 järjestelmäkutsua, ja jokainen on ytimen
hyökkäyspintaa. **seccomp** antaa prosessin asentaa itselleen
suodattimen, joka tutkii jokaisen järjestelmäkutsun ennen sen
suorittamista. Suodatin on **BPF**-ohjelma, joka näkee kutsun numeron,
arkkitehtuurin ja argumentit ja päättää, sallitaanko kutsu,
palautetaanko virhe vai tapetaanko prosessi.

```{.c tiedosto="esimerkit/07-seccomp.c" osa="suodatin"}
```

Arkkitehtuurin tarkistus on välttämätön: sama numero tarkoittaa eri
kutsua eri arkkitehtuureilla, ja x86-64-prosessi voi tehdä myös
32-bittisiä kutsuja. Ensimmäinen lapsi saa kielletystä kutsusta
virheen, toinen tapetaan:

```{.c tiedosto="esimerkit/07-seccomp.c" osa="virhe"}
```

```{.c tiedosto="esimerkit/07-seccomp.c" osa="tappo"}
```

```{.tuloste tiedosto="esimerkit/07-seccomp.odotettu"}
```

Suodatin periytyy lapsille eikä sitä voi poistaa, vain tiukentaa.
Dockerin oletusprofiili estää noin 50 kutsua, joita tavallinen
sovellus ei tarvitse, kuten `mount`, `reboot`, `kexec_load` ja
`bpf`. Kubernetes ottaa saman profiilin käyttöön asetuksella
`seccompProfile: RuntimeDefault`. Myös selaimet, systemd-palvelut
(`SystemCallFilter=`) ja OpenSSH:n aliprosessit käyttävät seccompia.

## LSM: AppArmor ja SELinux

Linux Security Modules -kehyksen politiikat ovat viimeinen kerros.
**AppArmor** (Ubuntu, Debian) rajaa ohjelman polkuihin perustuvalla
profiililla, **SELinux** (Red Hat -perhe) leimoilla. Docker asettaa
konteille oletusprofiilin (`docker-default`), joka estää muun muassa
liitokset ja `/proc`-hakemiston arkojen tiedostojen kirjoittamisen.
Tämän tutoriaalin kehityskontti ajetaan ilman profiilia, koska
esimerkit luovat nimiavaruuksia ja liitoksia: tuotantokontille
sellaista ei pidä antaa.

## Käytännössä

- **Aseta muistiraja aina.** Ilman rajaa yksi vuotava kontti voi viedä
  koko solmun muistin. Kubernetesissa `resources.limits.memory`, ja
  sovellus kannattaa mitoittaa rajan alle (JVM:llä
  `-XX:MaxRAMPercentage`).
- **CPU-raja hidastaa, painot jakavat.** `cpu.max`-kiintiö kuristaa
  prosessin, vaikka suoritin olisi vapaa, mikä näkyy viiveinä
  (throttling). Monessa kuormassa pelkkä paino (`cpu.weight`,
  Kubernetesin `requests`) on parempi.
- **Pudota kyvyt.** `--cap-drop=ALL` ja tarvittavat takaisin
  (`--cap-add=NET_BIND_SERVICE`). Älä anna `CAP_SYS_ADMIN`-kykyä
  tuotantokontille, koska sillä pääsee useimmista muista rajoista.
- **`--privileged` poistaa kaiken.** Kyvyt, seccomp, LSM ja
  laiterajat poistuvat kerralla. Etuoikeutettu kontti on käytännössä
  root isännässä.
- **Pidä seccomp-oletus päällä** ja kiristä profiilia, kun sovelluksen
  tarvitsemat kutsut tunnetaan (esim. `strace -c` tai
  oci-seccomp-bpf-hook).

## Itsearviointi

- Osaat luoda cgroupin, siirtää prosessin siihen ja asettaa sille muisti-,
  CPU- ja prosessirajan sekä selittää, mitä rajan ylittyessä tapahtuu.
- Osaat kertoa, mitä kyvyt ovat, poistaa kyvyn rootilta ja antaa kyvyn
  tavalliselle käyttäjälle ambient-kykynä.
- Osaat kirjoittaa seccomp-suodattimen, joka tarkistaa arkkitehtuurin ja
  palauttaa virheen tai tappaa prosessin.
- Osaat perustella, miksi `--privileged` ja `CAP_SYS_ADMIN` kumoavat
  kontin eristyksen.
