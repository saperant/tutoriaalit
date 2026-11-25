# Johdanto {.runko-johdanto}

Versionhallinta tallentaa projektin tiedostojen historian: jokainen
tallennettu tila voidaan palauttaa, muutoksia voidaan verrata ja jokaisesta
muutoksesta tiedetään, kuka sen teki, milloin ja miksi. Samalla se on
yhteistyön väline. Usea ihminen voi muuttaa samaa koodia rinnakkain, ja
muutokset yhdistetään hallitusti.

Git on nykyään käytännössä ainoa yleisesti käytetty versionhallinta.
Linus Torvalds kirjoitti sen vuonna 2005 Linux-ytimen kehitystä varten,
kun ytimen aiemman työkalun käyttölupa päättyi. Gitin suunnittelua
ohjasivat ytimen tarpeet: tuhansia kehittäjiä, valtava historia,
nopeus ja eheys. Ne näkyvät yhä sen ominaisuuksissa.

## Esitiedot ja rajaus

Esitietona on taito *Komentorivi ja Linux*: komentojen ajaminen
päätteessä, tiedostot ja hakemistot sekä tekstieditorin käyttö.
Ohjelmointitaitoa ei tarvita.

Tutoriaali ei käsittele seuraavia aiheita:

- testien ajaminen jokaisesta muutoksesta: taito *Käännösjärjestelmät,
  testaus ja CI*
- runkopohjainen kehitys ja toimitusputki syvemmin: taito *Jatkuva
  integraatio ja toimitus*
- salaisuusvuodot, allekirjoitukset ja haarasuojaukset: taito
  *Tietoturva kehitystyössä*
- GitOps: taito *Kontit ja pilvi-infrastruktuuri*.

## Hajautettu versionhallinta

Vanhemmissa keskitetyissä järjestelmissä (CVS, Subversion) historia oli
palvelimella, ja jokainen commit oli verkko-operaatio. Gitissä jokaisella
kehittäjällä on koko historia omalla koneellaan:

- commit, haarat, historian selaaminen ja vertailu toimivat ilman verkkoa
  ja ovat nopeita,
- jokainen kopio on täydellinen varmuuskopio,
- "palvelin" (GitHub, GitLab, oma) on sopimuksenvarainen yhteinen kopio,
  ei teknisesti erityinen.

Hajautetun mallin hinta on, että samasta haarasta voi olla useita
erilaisia versioita eri koneilla. Luvut *Etärepositoriot ja yhteistyö*
ja *Työnkulut ja repositorion rakenne* käsittelevät, miten tämä
hallitaan.

## Mihin Git ei sovellu

Git versioi tekstiä hyvin ja suuria binääritiedostoja huonosti. Jokainen
kuvan, mallin tai aineiston versio jää historiaan pysyvästi, ja jokainen
kloonaaja lataa ne kaikki. Suurille binääreille käytetään Git LFS:ää tai
erillistä artefaktivarastoa, ja käännöstuotteet (PDF:t, binäärit,
riippuvuushakemistot) jätetään kokonaan pois ja tuotetaan
käännösputkessa. Git ei myöskään ole varmuuskopio eikä salaisuuksien
säilö: historiaan tallennettu salaisuus leviää jokaiseen kopioon
(ks. taito *Tietoturva kehitystyössä*).

## Asennus ja asetukset

Git asennetaan paketinhallinnasta (`apt install git`, `brew install git`,
Windowsissa Git for Windows). Ennen ensimmäistä committia asetetaan nimi
ja sähköposti, jotka tallentuvat jokaiseen committiin:

```text
git config --global user.name "Aino Kehittäjä"
git config --global user.email aino@example.fi
git config --global init.defaultBranch main
git config --global pull.ff only
```

Viimeinen asetus estää `git pull`ia tekemästä yllättäviä
yhdistämiscommitteja; luku *Etärepositoriot ja yhteistyö* kertoo miksi.
Asetukset ovat tasoittain: järjestelmä (`--system`), käyttäjä
(`--global`, tiedosto `~/.gitconfig`) ja repositorio (`.git/config`).
Tarkempi taso voittaa. `git config --list --show-origin` näyttää, mistä
kukin asetus tulee.

## Ensimmäinen repositorio

`git init` luo repositorion: nykyiseen hakemistoon tulee piilotettu
hakemisto `.git`, jossa koko historia on. Tiedosto lisätään
*valmistelualueelle* komennolla `git add`, ja `git commit` tallentaa
valmistelualueen sisällön uudeksi tilannekuvaksi:

```{.bash tiedosto="esimerkit/01-ensimmainen.sh" osa="alustus"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

`git status --short` kertoo tiedostojen tilan kahdella merkillä:
vasen sarake on valmistelualue, oikea työhakemisto. `??` on seuraamaton,
`A` lisätty, `M` muutettu, `D` poistettu.

## Tutoriaalin esimerkit

Esimerkit ovat Bash-skriptejä, jotka luovat tilapäiseen hakemistoon
repositorion, tekevät siinä jotain ja tulostavat tuloksen. Testit ajavat
jokaisen skriptin ja vertaavat tulostetta tekstissä näkyvään. Jotta
commit-tunnisteet olisivat joka ajolla samat, jokaisen skriptin alussa on
sama vakio-osa: käyttäjän omat asetukset ohitetaan, tekijä on kiinteä ja
kello etenee minuutin jokaisella commitilla.

```{.bash tiedosto="esimerkit/01-ensimmainen.sh" osa="vakiot"}
```

Omassa työssä näitä muuttujia ei tarvita. Jos ajat esimerkkejä itse,
ne luovat hakemistoja nykyiseen hakemistoon, joten aja ne tyhjässä
hakemistossa (`cd "$(mktemp -d)"`). Esimerkkien kehityskontissa
(`.devcontainer/versionhallinta`) on Git ja ShellCheck.

Tutoriaali olettaa taidon *Komentorivi ja Linux*. Lukujen järjestys
kulkee tietomallista arkityöhön ja yhteistyöhön. Kokenut käyttäjä voi
lukea luvun *Gitin tietomalli* ja hypätä sen jälkeen suoraan haluamaansa
lukuun.
