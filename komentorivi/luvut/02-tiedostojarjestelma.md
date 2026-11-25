# Tiedostojärjestelmä

Linuxissa on yksi hakemistopuu, jonka juuri on `/`. Levyt, osiot,
verkkolevyt ja virtuaaliset tiedostojärjestelmät liitetään (*mount*)
puun haaroiksi. Myös laitteet (`/dev`) ja ytimen tila (`/proc`,
`/sys`) näkyvät tiedostoina, joten samat työkalut toimivat kaikkeen.

## Hakemistohierarkia

Hakemistojen tarkoitus on sovittu FHS-standardissa (*Filesystem
Hierarchy Standard*):

| Hakemisto | Sisältö |
|-----------|---------|
| `/usr/bin`, `/usr/lib` | Paketinhallinnan asentamat ohjelmat ja kirjastot; `/bin` on nykyään linkki tänne |
| `/usr/local` | Paikallisesti, paketinhallinnan ohi asennetut ohjelmat |
| `/opt` | Itsenäiset kolmannen osapuolen sovellukset |
| `/etc` | Järjestelmän asetukset tekstitiedostoina |
| `/var` | Muuttuva data: `/var/log` lokit, `/var/lib` sovellusten tila |
| `/home/<käyttäjä>` | Käyttäjien kotihakemistot, `~` lyhenteenä |
| `/tmp` | Väliaikaiset tiedostot, tyhjennetään usein käynnistyksessä |
| `/proc`, `/sys` | Ytimen tiedot prosesseista ja laitteista |
| `/dev` | Laitetiedostot, esim. `/dev/null` ja `/dev/sda` |

Sääntö käytännössä: älä muokkaa paketinhallinnan omistamia tiedostoja
hakemistossa `/usr`. Paikalliset asennukset kuuluvat hakemistoon
`/usr/local` tai `/opt`, asetukset hakemistoon `/etc`.

## Polut ja liikkuminen

Absoluuttinen polku alkaa juuresta (`/etc/ssh/sshd_config`), suhteellinen
nykyisestä hakemistosta (`../lahde/paa.c`). Erikoisnimet: `.` nykyinen,
`..` ylempi, `~` koti, `-` edellinen hakemisto (`cd -`).

| Komento | Tehtävä |
|---------|---------|
| `pwd`, `cd polku` | Missä olen, siirry |
| `ls -la`, `ls -lh`, `ls -lt` | Kaikki tiedostot, koot luettavasti, uusin ensin |
| `mkdir -p a/b/c` | Luo hakemistot välihakemistoineen, ei virhettä jos on jo |
| `cp -a lahde kohde` | Kopioi rekursiivisesti oikeudet ja ajat säilyttäen |
| `mv vanha uusi` | Siirrä tai nimeä uudelleen |
| `rm tiedosto`, `rm -r hakemisto` | Poista; ei roskakoria |
| `stat tiedosto` | Koko, oikeudet, inode, ajat |
| `du -sh *`, `df -h` | Hakemistojen tilankäyttö, levyjen vapaa tila |
| `findmnt`, `lsblk` | Mitä puuhun on liitetty, mitä levyjä ja osioita koneessa on |

Kuori laajentaa jokerimerkit (*glob*) ennen kuin komento käynnistyy:
`*` mikä tahansa merkkijono, `?` yksi merkki ja `[a-j]` merkkiväli.
Aaltosulkulaajennus `{a,b}` tuottaa vaihtoehdot riippumatta siitä,
ovatko tiedostot olemassa, joten sillä voi luoda rakenteita:

```{.bash tiedosto="esimerkit/02-rakenne.sh" osa="luonti"}
```

```{.bash tiedosto="esimerkit/02-rakenne.sh" osa="glob"}
```

```{.bash tiedosto="esimerkit/02-rakenne.sh" osa="polut"}
```

```{.tuloste tiedosto="esimerkit/02-rakenne.odotettu"}
```

Komennot `basename` ja `dirname` erottavat polusta tiedostonimen ja
hakemiston, ja `realpath` muuntaa polun absoluuttiseksi tai, kuten
tässä, suhteelliseksi toiseen hakemistoon nähden.

Huomaa viimeinen `echo`-rivi: aaltosulkulaajennus tehdään ennen globia,
joten `*.{c,h}` tuottaa ensin `.c`-tiedostot ja sitten `.h`-tiedostot.
Jos glob ei osu mihinkään, Bash jättää sen sellaisenaan, ja komento saa
kirjaimellisen merkkijonon `*.txt`. Piilotiedostot (`.`-alkuiset) eivät
osu globiin `*`.

## Tiedostojen katselu ja muokkaaminen

| Komento | Tehtävä |
|---------|---------|
| `cat tiedosto` | Tulostaa koko sisällön; sopii lyhyille tiedostoille |
| `less tiedosto` | Selaa sisältöä sivu kerrallaan |
| `head -n 20 tiedosto`, `tail -n 20 tiedosto` | Alku ja loppu |
| `tail -f loki` | Seuraa kasvavaa tiedostoa; Ctrl+C lopettaa |
| `file tiedosto` | Päättelee tyypin sisällöstä, ei nimestä |

Sivutin `less` on komentorivin yleisin katseluohjelma, ja myös `man`
näyttää ohjesivut sillä. Välilyönti siirtyy sivun eteenpäin ja `b`
taaksepäin, `g` ja `G` hyppäävät alkuun ja loppuun, `/sana` hakee,
`n` siirtyy seuraavaan osumaan ja `q` lopettaa.

Palvelimella ei yleensä ole graafista editoria, joten asetustiedostot
muokataan päätteessä. Lisäksi moni komento avaa editorin itse, esimerkiksi
`crontab -e`, `git commit` ja `systemctl edit`. Tavallisesti avautuu
jompikumpi kahdesta:

- **nano** on tavallisen tekstieditorin kaltainen. Näppäimet näkyvät
  ruudun alareunassa, jossa `^` tarkoittaa Ctrl-näppäintä: Ctrl+O
  tallentaa, Ctrl+X lopettaa ja Ctrl+W hakee.
- **vi** ja sen seuraaja **Vim** ovat lähes jokaisessa järjestelmässä.
  Niissä on tilat: komentotilassa näppäimet ovat komentoja, ja tekstiä
  kirjoitetaan vasta lisäystilassa. Alla ovat taidot, joilla tiedoston
  saa muokattua ja editorista pääsee pois.

| Näppäily | Toiminto |
|----------|----------|
| `i` | Lisäystilaan: näppäilyt ovat nyt tekstiä |
| Esc | Takaisin komentotilaan |
| `:w` ja Enter | Tallenna |
| `:q` ja Enter | Lopeta; `:wq` tallentaa ja lopettaa |
| `:q!` ja Enter | Lopeta tallentamatta |
| `/sana` ja Enter | Hae; `n` siirtyy seuraavaan osumaan |
| `dd`, `u` | Poista rivi, kumoa edellinen muutos |

Jos editori avautui vahingossa, paina Esc ja kirjoita `:q!`. Komento
`vimtutor` opettaa Vimin perusteet puolessa tunnissa. Sen, mikä editori
avautuu, määräävät muuttujat `VISUAL` ja `EDITOR` (luku *Ympäristö ja
kuoren asetukset*).

## Lainausmerkit

Kuori käsittelee komentorivin ennen kuin komento näkee sen: se jakaa
rivin sanoiksi välilyöntien kohdalta, korvaa muuttujat arvoillaan
(`$nimi` on muuttujan `nimi` arvo) ja laajentaa jokerimerkit.
Lainausmerkeillä päätetään, mikä tästä tehdään:

| Muoto | Mitä kuori tekee sisällölle |
|-------|-----------------------------|
| `'teksti'` | Ei mitään: jokainen merkki on kirjaimellinen |
| `"teksti"` | Laajentaa muuttujat `$nimi` ja komennot `$(komento)`; ei jaa sanoiksi eikä laajenna jokerimerkkejä |
| Ei lainausta | Laajentaa kaiken, jakaa tuloksen sanoiksi ja laajentaa jokerimerkit |
| `\merkki` | Poistaa yhden merkin erikoismerkityksen |

```{.bash tiedosto="esimerkit/02-lainaus.sh" osa="lainaus"}
```

```{.tuloste tiedosto="esimerkit/02-lainaus.odotettu"}
```

Lainaamaton `$nimi` jakautui kahdeksi argumentiksi, koska arvossa on
välilyönti. Tämä on komentorivin yleisin virhe, ja siksi muuttujat
kirjoitetaan kaksinkertaisiin lainausmerkkeihin. Yksinkertaisia
lainausmerkkejä käytetään, kun tekstissä on merkkejä, jotka kuori muuten
tulkitsisi, kuten `grep`- ja `awk`-komentojen lausekkeissa. Laajennusten
tarkka järjestys kuuluu taitoon *Bash-skriptaus*.

## Inodet ja linkit

Tiedoston sisältö ja metatiedot ovat *inodessa*. Hakemisto on vain
lista nimistä, jotka osoittavat inodeihin. Tästä seuraa kaksi
linkkityyppiä:

- **Kova linkki** (`ln a b`) on toinen nimi samalle inodelle. Sisältö
  säilyy, kunnes viimeinen nimi poistetaan. Kova linkki ei voi
  osoittaa hakemistoon eikä toiseen tiedostojärjestelmään.
- **Symbolinen linkki** (`ln -s a b`) on pieni tiedosto, joka sisältää
  polun. Se voi osoittaa mihin tahansa ja rikkoutuu, jos kohde
  poistetaan.

```{.dot otsikko="Kova linkki on toinen nimi samalle inodelle, symbolinen linkki oma tiedostonsa, jonka sisältö on polku"}
digraph {
  rankdir=LR; nodesep=0.25;
  n1 [label="asetukset.conf", shape=plaintext];
  n2 [label="kova.conf", shape=plaintext];
  n3 [label="symbolinen.conf", shape=plaintext];
  i1 [label="inode A\nsisältö: versio 1\nlinkkejä: 2"];
  i2 [label="inode B\nsisältö: polku\nasetukset.conf"];
  n1 -> i1; n2 -> i1; n3 -> i2;
  i2 -> n1 [style=dashed, label="kuori seuraa polkua", constraint=false];
}
```

```{.bash tiedosto="esimerkit/02-linkit.sh" osa="linkit"}
```

```{.bash tiedosto="esimerkit/02-linkit.sh" osa="muutos"}
```

Uudelleenohjaus `>` kirjoittaa olemassa olevaan inodeen, joten muutos
näkyy kaikkien nimien kautta. Sen sijaan `mv` vaihtaa nimen
osoittamaan uuteen inodeen. Kova linkki jää osoittamaan vanhaan
sisältöön:

```{.bash tiedosto="esimerkit/02-linkit.sh" osa="korvaus"}
```

```{.tuloste tiedosto="esimerkit/02-linkit.odotettu"}
```

```{.dot otsikko="mv vaihtaa nimen osoittamaan uuteen inodeen; kova linkki jää vanhaan"}
digraph {
  rankdir=LR; nodesep=0.25;
  subgraph cluster_e {
    label="ennen"; color="#D9E0E3";
    e1 [label="toinen.conf", shape=plaintext];
    e2 [label="kova2.conf", shape=plaintext];
    e3 [label="uusi.conf", shape=plaintext];
    ea [label="inode A\nversio 2"]; eb [label="inode B\nversio 3"];
    e1 -> ea; e2 -> ea; e3 -> eb;
  }
  subgraph cluster_j {
    label="mv uusi.conf toinen.conf"; color="#D9E0E3";
    j1 [label="toinen.conf", shape=plaintext];
    j2 [label="kova2.conf", shape=plaintext];
    ja [label="inode A\nversio 2"]; jb [label="inode B\nversio 3"];
    j1 -> jb; j2 -> ja;
  }
  eb -> j1 [style=invis];
}
```

Tämä ero on *atomisen korvaamisen* perusta: tiedosto kirjoitetaan
ensin väliaikaiseen nimeen samassa hakemistossa ja nimetään sitten
`mv`:llä oikeaksi. Lukija näkee joko vanhan tai uuden version, ei
koskaan puolikasta. Paketinhallinta ja monet editorit toimivat näin.
Siksi editori voi rikkoa kovan linkin, mutta symbolinen linkki säilyy.

Symbolisia linkkejä käytetään versioiden vaihtoon: `/opt/sovellus/nykyinen
-> versiot/2.4.1`. Uusi versio otetaan käyttöön vaihtamalla linkki
(`ln -sfn versiot/2.5.0 nykyinen`), ja paluu edelliseen on yhtä nopea.

## Hankalat tiedostonimet

Tiedostonimessä saa olla mitä tahansa paitsi `/` ja nollatavu, myös
välilyöntejä, rivinvaihtoja ja alussa viiva. Viiva tekee nimestä
valitsimen näköisen, ja lainaamaton välilyönti jakaa nimen kahdeksi
argumentiksi:

```{.bash tiedosto="esimerkit/02-hankalat-nimet.sh" osa="nimet"}
```

```{.bash tiedosto="esimerkit/02-hankalat-nimet.sh" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/02-hankalat-nimet.odotettu"}
```

Ilman erotinta `--` komento `rm -r` olisi tulkinnut nimen valitsimeksi.
Sama koskee kaikkia komentoja, jotka saavat tiedostonimiä
jokerimerkeistä: `rm *` hakemistossa, jossa on tiedosto `-rf`, on
klassinen ansa.

## Käytännössä

- **Lainaa nimet aina** (`"$f"`, `'vuosi raportti.txt'`) ja käytä `--`
  ennen operandeja, kun nimet tulevat jokerimerkeistä tai muuttujista.
- **Tarkista ennen kuin poistat.** Aja ensin `ls` samalla
  jokerimerkillä tai `echo rm *.log`, ja vasta sitten `rm`. `rm -i`
  kysyy vahvistuksen. Poistettua ei saa takaisin.
- **Korvaa tiedostot atomisesti** (`kirjoita tmp && mv tmp kohde`),
  kun joku muu voi lukea tiedostoa samaan aikaan. Väliaikaisen
  tiedoston on oltava samassa tiedostojärjestelmässä, koska vain silloin
  `mv` on pelkkä nimen vaihto.
- **Symbolinen linkki versionvaihtoon**, kova linkki harvoin. Kovia
  linkkejä käyttävät lähinnä varmuuskopio- ja paketointityökalut
  tilan säästämiseen.
- **Älä jäsennä `ls`-komennon tulostetta** skripteissä: tuloste on
  ihmiselle, ja hankalat nimet rikkovat sen. Käytä globia tai `find`-
  komentoa (luku *Etsintä, massatoiminnot ja arkistot*).
- **Tilaa etsiessä** `du -sh * | sort -h` hakemistossa ja `df -h`
  levyittäin. Täysi levy on yleinen syy palvelun kaatumiseen; lokit
  kasvavat hakemistossa `/var/log`.

## Itsearviointi

- Osaat kertoa, mitä hakemistoissa `/etc`, `/var`, `/usr/local` ja
  `/proc` on, ja mihin oman ohjelman asetukset ja lokit kuuluvat.
- Osaat käyttää jokerimerkkejä ja aaltosulkulaajennusta ja tiedät,
  että kuori laajentaa ne ennen komennon käynnistymistä.
- Osaat selittää kovan ja symbolisen linkin eron inodien avulla ja
  miksi `mv` korvaa tiedoston atomisesti.
- Osaat käsitellä tiedostonimiä, joissa on välilyöntejä tai jotka
  alkavat viivalla.
- Osaat selata tiedostoa `less`-sivuttimella sekä muokata ja tallentaa
  tiedoston nanolla tai vi:llä ja poistua editorista.
- Osaat valita yksinkertaisten ja kaksinkertaisten lainausmerkkien
  välillä ja selittää, miksi lainaamaton muuttuja voi jakautua
  useaksi argumentiksi.
