# Kontit: nimiavaruudet ja minikontti

Kontti ei ole ytimen käsite. Linuxissa ei ole järjestelmäkutsua
"luo kontti", vaan kontti kootaan erillisistä mekanismeista:

| Mekanismi | Rajaa | Luku |
|-----------|-------|------|
| Nimiavaruudet | mitä prosessi näkee | 6 |
| Juuritiedostojärjestelmä (overlay) | mitkä tiedostot ovat olemassa | 6 |
| cgroups | paljonko resursseja prosessi saa | 7 |
| Kyvyt | mitä rootin oikeuksia prosessilla on | 7 |
| seccomp | mitä järjestelmäkutsuja prosessi saa tehdä | 7 |
| LSM (AppArmor, SELinux) | mitä tiedostoja ja toimintoja politiikka sallii | 7 |

Dockerin, Podmanin ja Kubernetesin alla toimiva **OCI-ajoympäristö**
(runc, crun) tekee juuri nämä asiat järjestyksessä ja käynnistää
kontin ensimmäisen prosessin. Tässä luvussa kootaan sama käsin.

## Nimiavaruudet

**Nimiavaruus** (namespace) antaa prosessiryhmälle oman kopion
jostain ytimen globaalista resurssista. Prosessi kuuluu jokaisen
tyypin nimiavaruuteen, ja lapsi perii vanhempansa nimiavaruudet, ellei
toisin pyydetä (`clone`, `unshare` tai `setns`).

| Nimiavaruus | Eristää | Lippu |
|-------------|---------|-------|
| mnt | liitospisteet (tiedostojärjestelmänäkymä) | `CLONE_NEWNS` |
| uts | konenimi ja verkkotunnus | `CLONE_NEWUTS` |
| ipc | System V IPC ja POSIX-viestijonot | `CLONE_NEWIPC` |
| pid | prosessinumerot | `CLONE_NEWPID` |
| net | verkkoliitännät, reitit, palomuuri, portit | `CLONE_NEWNET` |
| user | käyttäjä- ja ryhmätunnukset sekä kyvyt | `CLONE_NEWUSER` |
| cgroup | näkymä cgroup-hierarkiaan | `CLONE_NEWCGROUP` |
| time | monotoniset kellot (esim. siirretyille konteille) | `CLONE_NEWTIME` |

Prosessin nimiavaruudet näkyvät hakemistossa `/proc/<pid>/ns/`.
Kahdella prosessilla on sama nimiavaruus, jos linkkien kohteet ovat
samat.

## Yksi kerrallaan

`unshare` käynnistää komennon uusissa nimiavaruuksissa. UTS-
nimiavaruudessa konenimen voi vaihtaa vaikuttamatta isäntään:

```{.bash tiedosto="esimerkit/06-nimiavaruudet.sh" osa="uts"}
```

PID-nimiavaruudessa ensimmäisestä prosessista tulee PID 1. Valitsin
`--fork` tarvitaan, koska `unshare` itse jää vanhaan nimiavaruuteen ja
vasta sen lapsesta tulee uuden nimiavaruuden ensimmäinen prosessi.
`--mount-proc` liittää uuden `/proc`-hakemiston, jotta työkalut näkevät
uuden numeroinnin:

```{.bash tiedosto="esimerkit/06-nimiavaruudet.sh" osa="pid"}
```

Uudessa verkkonimiavaruudessa on vain silmukkaliitäntä, eikä sekään
ole päällä. Konttiajoympäristö luo lisäksi veth-parin isännän
siltaan (ks. taito *Tietoverkot*):

```{.bash tiedosto="esimerkit/06-nimiavaruudet.sh" osa="net"}
```

Liitosnimiavaruudessa tehdyt liitokset eivät näy isännälle. Valitsin
`--propagation private` estää liitosten leviämisen kumpaankaan
suuntaan:

```{.bash tiedosto="esimerkit/06-nimiavaruudet.sh" osa="mnt"}
```

`nsenter` liittyy olemassa olevan prosessin nimiavaruuksiin
järjestelmäkutsulla `setns`. Näin toimii `docker exec`: uusi prosessi
käynnistetään kontin nimiavaruuksissa:

```{.bash tiedosto="esimerkit/06-nimiavaruudet.sh" osa="nsenter"}
```

```{.tuloste tiedosto="esimerkit/06-nimiavaruudet.odotettu"}
```

## Käyttäjänimiavaruus ja rootless-kontit

Käyttäjänimiavaruus kuvaa nimiavaruuden sisäiset käyttäjätunnukset
ulkoisiksi. Kontin sisällä prosessi voi olla root (UID 0) ja omistaa
kaikki kyvyt **omassa nimiavaruudessaan**, vaikka isännän silmissä se
on tavallinen käyttäjä, esimerkiksi UID 100000:

```text
$ unshare --user --map-root-user sh -c 'id -u; cat /proc/self/uid_map'
0
         0       1000          1
```

Tällä perustuvat **rootless-kontit** (Podman, rootless Docker): kontin
käynnistäminen ei vaadi isännän rootia, ja kontista karkaava prosessi
on isännässä etuoikeudeton. Hinta on rajoitukset: esimerkiksi
etuoikeutettuja portteja, laitteita ja osaa tiedostojärjestelmistä ei
voi käyttää. Osa jakeluista (Ubuntu 24.04) rajoittaa
etuoikeudettomien käyttäjänimiavaruuksien luontia AppArmorilla, koska
ne ovat paljastaneet ytimestä haavoittuvuuksia.

## Konttikuva ja overlay

Konttikuva on joukko tiedostojärjestelmäkerroksia. Kontti saa juureksi
**overlay**-tiedostojärjestelmän: kuvan kerrokset ovat vain luettavia
alempia kerroksia (lowerdir), ja kontin muutokset menevät ylimpään,
kirjoitettavaan kerrokseen (upperdir). Kun kontti poistetaan, ylin
kerros poistetaan, ja kuva on koskematon. Sama kuva palvelee kaikkia
kontteja, kuten qcow2-peruskuva palveli virtuaalikoneita.

```{.dot otsikko="Sama ajatus kahdella tasolla: vain luettavat jaetut kerrokset (harmaat) alla ja kirjoitettava kerros päällä. Overlay toimii tiedostojen tasolla, qcow2 levylohkojen"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.1;
  node [shape=plaintext, fontsize=9];
  o [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>kontti: overlay</b></td></tr>
    <tr><td bgcolor="#f3e6c8">kontin näkemä juuri</td></tr>
    <tr><td>upperdir: kontin muutokset</td></tr>
    <tr><td bgcolor="#d9d9d9">lowerdir: kuvan kerros 2</td></tr>
    <tr><td bgcolor="#d9d9d9">lowerdir: kuvan kerros 1</td></tr></table>>];
  q [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>virtuaalikone: qcow2</b></td></tr>
    <tr><td bgcolor="#f3e6c8">vieraan näkemä levy</td></tr>
    <tr><td>kerros: koneen muutokset</td></tr>
    <tr><td bgcolor="#d9d9d9">peruskuva</td></tr></table>>];
  o -> q [style=invis];
}
```

Jaettavassa muodossa (OCI-kuva) jokainen kerros on tar-paketti, joka
nimetään sisältönsä tiivisteellä. **Manifesti** luettelee kuvan
kerrokset tiivisteineen ja viittaa asetustiedostoon, jossa ovat
käynnistettävä komento ja ympäristömuuttujat. Koska nimi on sisällön
tiiviste, sama kerros tallennetaan ja ladataan vain kerran, vaikka
kymmenen kuvaa rakentuisi sen päälle, ja muuttunut kerros huomataan
heti. Kuvien rakentaminen ja jakelu ovat taidon *Kontit ja
pilvi-infrastruktuuri* aihe.

## Minikontti

Seuraava skripti kokoaa kontin ilman konttityökaluja. Kontin "kuva" on
hakemisto, jossa on vain staattisesti käännetty init-ohjelma:

```{.c tiedosto="esimerkit/kuva/sbin/init.c" osa="init"}
```

Ensin rakennetaan kerrokset muistiin ja liitetään overlay. Kaikki
tapahtuu omassa liitosnimiavaruudessa, joten mikään ei näy isännälle:

```{.bash tiedosto="esimerkit/06-minikontti.sh" osa="kerrokset"}
```

Sitten init käynnistetään uusissa nimiavaruuksissa overlay juurenaan.
`--root` vaihtaa juurihakemiston kuten `chroot`. Oikeat
ajoympäristöt käyttävät turvallisempaa `pivot_root`-kutsua, joka
irrottaa vanhan juuren kokonaan:

```{.bash tiedosto="esimerkit/06-minikontti.sh" osa="kaynnistys"}
```

```{.bash tiedosto="esimerkit/06-minikontti.sh" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-minikontti.odotettu"}
```

Kontin init on PID 1 ja näkee vain itsensä. Sen konenimi on oma,
verkkoliitäntöjä on vain yksi, ja sen kirjoittama tiedosto päätyi
ylimpään kerrokseen. Tästä puuttuvat vielä resurssirajat ja
oikeuksien karsiminen, jotka ovat seuraavan luvun aihe.

## PID 1 kontissa

Kontin ensimmäisellä prosessilla on kaksi tehtävää, joista tavallinen
ohjelma ei tiedä (orvot ja zombit yleisesti: taito
*Käyttöjärjestelmät*):

- **Orvot.** Kun prosessin vanhempi päättyy, PID 1 perii sen ja sen
  on kerättävä sen paluuarvo (`wait`). Muuten nimiavaruuteen kertyy
  zombeja.
- **Signaalit.** Ydin ei toimita PID 1:lle signaaleja, joille sillä ei
  ole käsittelijää. `docker stop` lähettää ensin SIGTERMin, ja jos
  sovellus on PID 1 ilman käsittelijää, mitään ei tapahdu, kunnes
  aikakatkaisun jälkeen tulee SIGKILL.

Siksi konteissa käytetään pientä init-ohjelmaa (`tini`, `docker run
--init`) tai sovellus käsittelee signaalit itse.

## Käytännössä

- **Kontti on prosessi.** Kontin prosessit näkyvät isännän `ps`-
  listassa, ja niiden suorituskyky on natiivi. Vianetsinnässä voi
  käyttää isännän työkaluja (`nsenter --target <pid> --net ss -tlnp`).
- **Nimiavaruus ei ole turvaraja yksinään.** Kaikki kontit jakavat
  saman ytimen, joten ytimen haavoittuvuus vaikuttaa kaikkiin.
  Turvallisuus tulee kerroksista: käyttäjänimiavaruus, kyvyt, seccomp,
  LSM ja tarvittaessa virtuaalikone (luku 8).
- **Kuva vain luettavaksi.** Ajonaikainen tila kuuluu taltioihin, ei
  kontin ylimpään kerrokseen, joka häviää kontin mukana. Moni
  ajoympäristö voi tehdä juuresta kokonaan vain luettavan
  (`--read-only`), mikä paljastaa sovelluksen huonot oletukset
  aikaisin.
- **Käytä init-prosessia.** Jos sovellus käynnistää aliprosesseja tai
  sen on sammuttava siististi, käynnistä kontti `--init`-valitsimella
  tai käsittele SIGTERM sovelluksessa.

## Itsearviointi

- Osaat luetella Linuxin nimiavaruudet ja kertoa, mitä kukin eristää.
- Osaat käyttää `unshare`- ja `nsenter`-komentoja ja selittää, miksi
  PID-nimiavaruus vaatii `--fork`-valitsimen.
- Osaat koota overlay-juuren ja käynnistää prosessin omissa
  nimiavaruuksissaan ilman konttityökaluja.
- Osaat selittää käyttäjänimiavaruuden ja rootless-konttien
  perusidean sekä PID 1:n erityistehtävät kontissa.
