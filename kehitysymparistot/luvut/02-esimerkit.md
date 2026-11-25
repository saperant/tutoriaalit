# Tutoriaalien esimerkit käyttöön

Jokaisen tutoriaalin koodi on hakemistossa `<paketti>/esimerkit/`, ja
jokaisella tutoriaalilla on oma kehityskontti, jossa on juuri sen
työkalut: C:lle GCC 14, Clang 20 ja sanitoijat, Rustille rustc ja
Clippy, tietoverkoille verkkotyökalut ja niin edelleen. CI ajaa
jokaisen tutoriaalin testit sen omassa kontissa, joten kontti varmasti
riittää esimerkkien ajamiseen.

Esimerkit saa käyttöön neljällä tavalla:

| Tapa | Tarvitset | Sopii, kun |
|-------------------|----------------------|------------------------------|
| GitHub Codespaces | selaimen ja GitHub-tilin | haluat kokeilla heti asentamatta mitään |
| VS Code ja kehityskontti | Dockerin ja VS Coden | työskentelet pidempään omalla koneella |
| Zip-paketti | Dockerin ja VS Coden | haluat vain yhden tutoriaalin esimerkit |
| Ilman konttia | työkalut itse asennettuina | käytät jo Linuxia ja haluat omat työkalusi |

## GitHub Codespaces

Codespaces rakentaa kontin GitHubin palvelimelle ja avaa siihen VS Coden
selaimessa.

1. Avaa repositorio GitHubissa ja valitse *Code → Codespaces → New
   with options*.
2. Valitse kohdasta *Dev container configuration* haluamasi
   tutoriaali, esimerkiksi *C-kieli: esimerkit*.
3. Odota, että kontti rakentuu. Ensimmäinen kerta kestää muutaman
   minuutin; sen jälkeen sama ympäristö käynnistyy nopeasti.

Taitopuukartalla on jokaisen valmiin tutoriaalin kohdalla linkki *Avaa
Codespacesissa*, joka valitsee oikean konfiguraation valmiiksi.

Codespaces on maksullinen palvelu, mutta henkilökohtaisella tilillä on
kuukausittainen ilmainen käyttökiintiö (kirjoitushetkellä 120 ydintuntia
ja 15 Gt tallennustilaa). Pysäytä tai poista ympäristö, kun et käytä
sitä: pysäytetty ympäristö kuluttaa vain tallennustilaa. Ajantasaiset
ehdot ovat GitHubin dokumentaatiossa.

## VS Code ja kehityskontti omalla koneella

Tarvitset kolme asiaa: Dockerin (Linuxissa Docker Engine, Windowsissa ja
macOS:ssä Docker Desktop tai vastaava), Visual Studio Coden ja sen
laajennuksen *Dev Containers* (`ms-vscode-remote.remote-containers`).

1. Kloonaa repositorio ja avaa sen juurihakemisto VS Codessa.
2. Avaa komentopaletti (Ctrl+Shift+P tai F1) ja valitse *Dev
   Containers: Reopen in Container*.
3. Valitse luettelosta tutoriaalin konfiguraatio.

VS Code rakentaa kuvan, käynnistää kontin, liittää repositorion sen
sisään ja avaa suoraan tutoriaalin esimerkkihakemiston. Pääte, kääntäjä,
debuggeri ja kielituki toimivat kontin sisällä; omalle koneelle ei
asennu mitään. Toiseen tutoriaaliin vaihdetaan komennolla *Dev
Containers: Switch Container*, ja komento *Reopen Folder Locally* palaa
takaisin omalle koneelle.

Kaikki konfiguraatiot rakennetaan samasta Dockerfilesta
(`.devcontainer/Dockerfile`), jolle tutoriaali antaa omat työkalunsa
rakennusargumentteina. Yhteinen pohja ladataan ja rakennetaan vain
kerran, joten toisen tutoriaalin kontti valmistuu ensimmäistä
nopeammin.

## Zip-paketti

Taitopuukartalta saa kunkin tutoriaalin esimerkit tiedostona
`<paketti>-esimerkit.zip`. Paketissa ovat esimerkit, niiden kehityskontti
(`.devcontainer/devcontainer.json` ja `Dockerfile`) ja lyhyt ohje. Pura
paketti, avaa kansio VS Codessa ja valitse *Reopen in Container*.

Paketissa ei ole repositorion yhteisiä testityökaluja, joten komento
`make -C <paketti> testaa` ei ole käytössä. Jos esimerkkikansiossa on
Makefile, `make` rakentaa ja tarkistaa esimerkit.

## Ilman konttia

Kontti ei ole pakollinen. Tarvittavat työkalut näkee tutoriaalin
konfiguraatiosta `.devcontainer/<paketti>/devcontainer.json`: kohdassa
`build.args` on lueteltu, mitä yhteisen pohjan päälle asennetaan. Saman
tiedon tulostaa tämän tutoriaalin apuohjelma:

```text
python3 kehitysymparistot/esimerkit/kokoelma.py tyokalut tietoverkot
```

Ohjelma lukee konfiguraation ja tulostaa apt-, pip- ja npm-paketit sekä
kontin tarvitsemat erityisoikeudet:

```{.python tiedosto="esimerkit/kokoelma.py" osa="tyokalut"}
```

Tämän tutoriaalin oma kontti tarvitsee vain Pythonin tarkistustyökalut:

```{.tuloste tiedosto="esimerkit/tyokalut.odotettu"}
```

Apt-pakettien nimet ovat Ubuntu 24.04:n nimiä. Yhteisessä pohjassa ovat
aina `make`, GCC 14, Clang 20, `gdb` ja Python 3.

Ilman konttia vastaat itse siitä, että versiot täsmäävät. Jos esimerkki
käyttäytyy koneellasi eri tavalla kuin tekstissä, kokeile ensin
kontissa.

## Esimerkkien testaaminen

Repositorion juuressa komento

```text
make -C c-kieli testaa
```

tekee saman kuin CI:

1. tarkistaa tutoriaalin rakenteen (luvut, itsearvioinnit, pikaopas),
2. tarkistaa, kääntää ja ajaa jokaisen esimerkin ja vertaa tulostetta
   odotettuun,
3. ajaa esimerkkihakemiston oman Makefilen, jos sellainen on.

Tekstissä näkyvä koodi ja tulosteet sisällytetään PDF:ään samoista
tiedostoista, joten kirjassa ei ole koodia, jota ei olisi testattu.
Tiedostojen nimet kertovat, mitä testi niillä tekee:

| Tiedosto | Merkitys |
|------------------------|----------------------------------------------|
| `03-nimi.c` | esimerkki; numero on luku, jossa se esitellään |
| `03-nimi.odotettu` | ohjelman odotettu tuloste |
| `03-nimi.syote` | ohjelmalle annettava syöte |
| `03-nimi.argumentit` | komentoriviargumentit, yksi rivillään |
| `03-nimi.ei-kaanny.c` | ei saa kääntyä sellaisenaan, korjattuna kyllä |
| `03-nimi.kaatuu.c` | päättyy tarkoituksella ajonaikaiseen virheeseen |
| `03-nimi.virhe` | rivit, joiden on löydyttävä virhetulosteesta |
| `03-nimi/` | usean tiedoston esimerkki; pääohjelma on `main.*` |

Virheelliset esimerkit ovat mukana tarkoituksella: `.ei-kaanny` näyttää
virheen, jonka kääntäjä tai tarkistin pysäyttää, ja `.kaatuu` virheen,
jonka sanitoija tai ajonaikainen tarkistus pysäyttää. C:ssä ja C++:ssa
korjattu versio käännetään makrolla `-DKORJATTU`, muissa kielissä
poistamalla rivit, joilla on merkintä `@virhe`.

Tutoriaaleissa, joiden esimerkit ovat kokonaisia projekteja (esimerkiksi
web-sovellukset tai tämä tutoriaali), testit ajaa esimerkkihakemiston
Makefile, ja komennot on kerrottu sen alussa.

## Yksittäisen esimerkin ajaminen

Kontti avautuu tutoriaalin esimerkkihakemistoon, joten esimerkin voi
ajaa suoraan:

```text
python3 01-kulut.py < 01-kulut.syote
python3 01-kulut.py < 01-kulut.syote | diff - 01-kulut.odotettu
```

Jälkimmäinen rivi vertaa tulostetta odotettuun; `diff` ei tulosta
mitään, kun ne ovat samat. C- ja C++-tutoriaalien esimerkkihakemistossa
on Makefile, joka kääntää samoilla valitsimilla kuin testit:

```text
make                      # kääntää kaikki hakemistoon bin/
make aja-01-hei           # kääntää ja ajaa yhden esimerkin
make virhe-03-etumerkki   # näyttää .ei-kaanny-esimerkin käännösvirheen
```

Paras tapa oppia on muuttaa esimerkkiä ja katsoa, mitä tapahtuu.
Versionhallinta pitää alkuperäisen tallessa: `git diff` näyttää
muutoksesi ja `git restore <tiedosto>` palauttaa tiedoston.

## Käytännössä

- **Kokeile ensin Codespacesissa.** Se on nopein tapa päästä alkuun, eikä
  omalle koneelle asennu mitään. Siirry omaan koneeseen, kun työskentelet
  pidempään.
- **Kontti on totuus.** Tekstin tulosteet on tuotettu kehityskontin
  työkaluilla. Eri kääntäjäversio voi antaa eri varoitukset ja
  sanitoija eri virheilmoituksen.
- **Yksi tutoriaali, yksi kontti.** Kontit ovat tarkoituksella pieniä:
  jokaisessa on vain oman tutoriaalinsa työkalut. PDF:ien
  rakentamiseen on oma konfiguraationsa *Tutoriaalien kirjoittaminen*.
- **Aja testit ennen kuin epäilet esimerkkiä.** Jos `make -C <paketti>
  testaa` menee kontissa läpi, esimerkki toimii, ja ero on omassa
  ympäristössäsi tai muutoksessasi.

## Itsearviointi

- Osaat avata minkä tahansa tutoriaalin esimerkit Codespacesissa tai
  omalla koneellasi kehityskontissa.
- Osaat selvittää tutoriaalin konfiguraatiosta, mitä työkaluja sen
  esimerkit tarvitsevat.
- Osaat ajaa tutoriaalin testit ja yksittäisen esimerkin ja verrata
  tulostetta odotettuun.
- Osaat kertoa, mitä tiedostopäätteet `.odotettu`, `.ei-kaanny` ja
  `.kaatuu` tarkoittavat.
