# Mikä kontti on

Kontti ei ole kevyt virtuaalikone. Se on tavallinen Linux-prosessi,
jolle ydin näyttää rajatun näkymän järjestelmään ja jonka resurssien
käyttöä ydin rajoittaa. Virtuaalikoneessa on oma ydin ja emuloitu
laitteisto; kontit jakavat isäntäkoneen ytimen. Siksi kontti
käynnistyy millisekunneissa ja vie vähän muistia, mutta sen eristys on
heikompi kuin virtuaalikoneen.

## Nimiavaruudet: mitä prosessi näkee

Linuxin *nimiavaruus* (*namespace*) antaa prosessille oman kopion
jostakin järjestelmän resurssista:

| Nimiavaruus | Eristää |
|-------------|---------|
| PID | prosessitunnisteet: kontin ensimmäinen prosessi on PID 1 |
| mount | tiedostojärjestelmäpuun: kontilla on oma juurihakemisto |
| network | verkkoliitännät, reititystaulut ja portit |
| UTS | isäntänimen |
| IPC | jaetun muistin ja viestijonot |
| user | käyttäjätunnisteet: kontin root voi olla isännässä tavallinen käyttäjä |
| cgroup | näkymän cgroup-hierarkiaan |

Konttiajoympäristöä ei tarvita nimiavaruuksien kokeilemiseen.
`unshare` käynnistää komennon uusissa nimiavaruuksissa:

```{.bash tiedosto="esimerkit/nimiavaruudet.sh" osa="unshare"}
```

```{.tuloste tiedosto="esimerkit/nimiavaruudet.odotettu"}
```

Kuori luulee olevansa järjestelmän ensimmäinen prosessi, ja sen
asettama isäntänimi näkyy vain nimiavaruudessa. Konttiajoympäristö
(Docker, containerd, CRI-O, Podman) tekee saman, ja lisäksi se
valmistelee juuritiedostojärjestelmän kuvasta, verkon ja rajoitukset.
Esimerkki vaatii pääkäyttäjän oikeudet, joten se ajetaan `sudo`lla.

## cgroups: mitä prosessi saa käyttää

*Ohjausryhmät* (*control groups*, cgroups) rajoittavat ja mittaavat
prosessiryhmän resurssien käyttöä: muistia, suoritinaikaa, levyn
siirtonopeutta ja prosessien määrää. Kun kontille annetaan muistiraja,
konttiajoympäristö luo cgroupin ja kirjoittaa rajan sen tiedostoon.
Raja näkyy kontin sisältä:

```text
docker run --rm --memory 64m kaynnit:1.0.0 ... cat /sys/fs/cgroup/memory.max
```

Esimerkkien testi lukee rajan kontin sisältä (rivi *muistiraja
cgroupissa* tiedostossa `testit/docker.odotettu`): arvo on 67108864
tavua eli 64 MiB. Jos kontin prosessit ylittävät rajan, ydin lopettaa
niistä yhden (*OOM kill*), ja kontti päättyy virhekoodiin 137. Raja
koskee koko konttia, ei yksittäistä prosessia.

Suoritinraja (`--cpus 0.5`) toimii toisin: prosessi ei kuole vaan
saa suoritinaikaa enintään puolet yhdestä ytimestä jokaisella
jaksolla. Liian tiukka suoritinraja näkyy viiveinä, ei virheinä.

## Kuvat ja kerrokset

*Säiliökuva* on pino tiedostojärjestelmän *kerroksia* (*layer*) ja
asetustiedosto, joka kertoo käynnistyskomennon, ympäristömuuttujat,
käyttäjän ja portit. Kuvamuoto on standardoitu (OCI, *Open Container
Initiative*), joten Dockerilla rakennettu kuva toimii Kubernetesissa,
Podmanissa ja pilvipalveluiden konttiajoissa.

- Jokainen kerros on muutosjoukko edelliseen: lisätyt, muutetut ja
  poistetut tiedostot.
- Kerrokset ovat vain luku -tilassa ja jaettuja. Jos kymmenen kuvaa
  käyttää samaa peruskuvaa, se on levyllä kerran.
- Käynnistyvä kontti saa päällimmäiseksi oman kirjoitettavan
  kerroksen, joka katoaa kontin mukana. Säilytettävä data kuuluu
  volyymiin (luku 5).
- Kuvan tunniste on sen sisällön tiiviste, *digest* (`sha256:…`). Tagi
  (`3.12-slim`) on siirrettävä nimi, digest ei muutu.

## Rekisterit

Kuvat jaetaan *rekisterien* (*registry*) kautta: Docker Hub, GitHub
Container Registry (`ghcr.io`), pilvipalveluiden omat rekisterit ja
organisaation sisäiset rekisterit (Harbor, Artifactory). Kuvan nimi
kertoo rekisterin, polun, tagin ja valinnaisesti digestin:

```text
ghcr.io/esimerkki/kaynnit:1.0.0@sha256:0b5f…
```

Ilman rekisterin nimeä Docker olettaa Docker Hubin, ja ilman tagia se
olettaa tagin `latest`. Molemmat oletukset kannattaa kirjoittaa auki.

## Kontti vai virtuaalikone

| | Kontti | Virtuaalikone |
|-|--------|---------------|
| Ydin | jaettu isännän kanssa | oma |
| Käynnistys | millisekunteja | sekunteja–minuutteja |
| Koko | megatavuja | gigatavuja |
| Eristys | nimiavaruudet, cgroups, seccomp | laitteistotuettu hypervisori |
| Käyttöjärjestelmä | sama ydin kuin isännällä | mikä tahansa |

Pilvessä kontit ajetaan yleensä virtuaalikoneiden sisällä: virtuaalikone
eristää asiakkaat toisistaan, kontit saman asiakkaan palvelut. Jos
kontteihin ajetaan luottamatonta koodia, tarvitaan vahvempi eristys,
esimerkiksi gVisor tai Kata Containers (taito *Virtualisointi*).

## Käytännössä

- **Kontti on prosessi.** Kun kontin pääprosessi päättyy, kontti
  päättyy. Kontissa ei ajeta init-järjestelmää eikä useita
  taustapalveluita; yksi kontti, yksi vastuu.
- **Älä aja konttia rootina.** Kontin root on oletuksena isännän root
  rajoitetuin oikeuksin; ytimen haavoittuvuus tai väärä
  volyymiliitos riittää karkaamiseen. Luku 3 näyttää, miten kuva ajaa
  tavallisena käyttäjänä.
- **Aseta muistiraja jokaiselle kontille.** Ilman rajaa vuotava
  palvelu vie koko koneen muistin ja kaataa naapurinsa. Raja tekee
  ongelmasta yhden kontin uudelleenkäynnistyksen.
- **Viittaa kuviin digestillä, kun toistettavuus on tärkeää.** Tagi
  voi muuttua alta; digest ei. Rakennukset kiinnitetään digestiin,
  ja päivitykset tuodaan hallitusti (Renovate, Dependabot).
- **`--privileged` poistaa eristyksen.** Sitä tarvitaan harvoin; jos
  kontti tarvitsee yhden lisäoikeuden, anna vain se (`--cap-add`).

## Itsearviointi

- Osaat selittää, miten kontti eroaa virtuaalikoneesta, ja mistä
  kontin eristys koostuu.
- Osaat kertoa, mitä PID-, mount-, network- ja user-nimiavaruudet
  eristävät, ja kokeilla niitä `unshare`lla.
- Osaat kertoa, miten muisti- ja suoritinraja toimivat ja miltä niiden
  ylitys näyttää.
- Osaat selittää kuvan kerrokset, tagin ja digestin eron sekä kuvan
  nimen osat.
