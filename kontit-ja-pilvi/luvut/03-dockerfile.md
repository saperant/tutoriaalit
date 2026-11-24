# Säiliökuva Dockerfilellä

Dockerfile on resepti, jonka jokainen käsky tuottaa kuvaan kerroksen
tai asetuksen. Hyvä Dockerfile on toistettava (sama lähde tuottaa saman
kuvan), nopea rakentaa (välimuisti toimii) ja tuottaa pienen kuvan,
joka ajaa vain sitä, mitä tarvitaan.

## Käyntilaskurin kuva

Käyntilaskurin kuvassa on kolme vaihetta (*stage*). Ensimmäinen,
`perus`, valitsee peruskuvan ja yhteiset asetukset:

```{.dockerfile tiedosto="esimerkit/sovellus/Dockerfile" osa="perus"}
```

- **Peruskuva tagilla ja digestillä.** `python:3.12-slim` kertoo
  lukijalle, mistä on kyse; digest takaa, että rakennus käyttää täsmälleen
  samaa kuvaa ensi vuonnakin. Päivitys on tietoinen muutos, jonka
  työkalu (Renovate, Dependabot) ehdottaa ja CI testaa.
- **`slim`-muunnelma.** Debianin karsittu versio ilman kääntäjiä ja
  dokumentaatiota. Alpine-pohjaiset kuvat ovat vielä pienempiä, mutta
  niiden musl-kirjasto poikkeaa glibc:stä, mikä näkyy joskus
  Python-pakettien kanssa.
- **Ympäristömuuttujat.** `PYTHONUNBUFFERED` kirjoittaa lokirivit heti,
  jolloin ne näkyvät `docker logs` -komennolla viiveettä.

Toinen vaihe ajaa testit kuvan sisällä:

```{.dockerfile tiedosto="esimerkit/sovellus/Dockerfile" osa="testit"}
```

Testit ajetaan samalla Python-versiolla ja samoilla kirjastoilla kuin
tuotanto. `docker build --target testit sovellus` epäonnistuu, jos
testit epäonnistuvat, joten sama komento sopii kehittäjälle ja
CI-putkelle.

Kolmas vaihe on varsinainen kuva:

```{.dockerfile tiedosto="esimerkit/sovellus/Dockerfile" osa="ajo"}
```

## Mitä kukin rivi tekee ja miksi

**`ARG` ja `LABEL`.** Rakennusargumentti `VERSIO` tulee rakennuksesta
(`--build-arg VERSIO=1.0.0`) ja päätyy sekä kuvan merkintöihin että
ajonaikaiseen ympäristömuuttujaan. OCI-merkinnät
(`org.opencontainers.image.*`) kertovat työkaluille ja ihmisille, mistä
kuva on peräisin.

**`COPY` vain tarvittavat tiedostot.** Ajokuvaan ei kopioida testejä
eikä muuta ylimääräistä. Rakennuskontekstiin päätyy vain se, mitä
`.dockerignore` ei suodata:

```{.text tiedosto="esimerkit/sovellus/.dockerignore"}
```

Ilman `.dockerignore`a kontekstiin menee kaikki: välimuistit,
`.git`-hakemisto ja pahimmillaan salaisuuksia sisältävä `.env`, joka
`COPY . .` -käskyllä päätyisi kuvaan ja sen mukana rekisteriin.

**Oma käyttäjä.** `useradd` luo käyttäjän, jolla ei ole kotihakemistoa
eikä kuorta, ja `USER 10001` vaihtaa siihen. Numeerinen tunniste on
parempi kuin nimi: Kubernetes voi tarkistaa ilman kuvan
`/etc/passwd`-tiedostoa, että kontti ei aja rootina (luku 8).
Samassa käskyssä luodaan `/data` ja annetaan se käyttäjälle. Ilman sitä
laskuri kaatuisi Composessa: uusi nimetty volyymi saa omistajansa
kuvan hakemistosta, ja oletuksena se olisi root. Tämä virhe tulee
vastaan lähes jokaisessa kontissa, joka ajaa ei-root-käyttäjänä ja
kirjoittaa volyymiin.

**`EXPOSE`.** Dokumentoi portin; se ei avaa mitään. Portti julkaistaan
ajossa (`-p` tai Composen `ports`).

**`HEALTHCHECK`.** Konttiajoympäristö ajaa komennon määrävälein ja
merkitsee kontin terveeksi tai sairaaksi. Composen riippuvuudet
odottavat terveyttä (luku 6). Tarkistus on oma pieni ohjelmansa,
koska kuvassa ei ole `curl`ia:

```{.python tiedosto="esimerkit/sovellus/terveys.py"}
```

Kubernetes ei käytä Dockerfilen `HEALTHCHECK`iä; siellä vastaavat ovat
koettimet (*probes*, luku 8).

**`ENTRYPOINT` ja `CMD` exec-muodossa.** JSON-taulukkomuoto
(`["python", "api.py"]`) käynnistää ohjelman suoraan ilman kuorta.
Kuorimuoto (`CMD python api.py`) käynnistäisi `/bin/sh -c`:n, joka
olisi PID 1 eikä välittäisi SIGTERM-signaalia Pythonille: pysäytys
odottaisi aikarajan ja tappaisi palvelun kesken pyyntöjen.
`ENTRYPOINT ["python"]` ja `CMD ["api.py"]` erotetaan, jotta laskuri
voi käyttää samaa kuvaa toisella komennolla.

## Hallittu sammutus

Kontin pysäytys lähettää pääprosessille SIGTERMin ja aikarajan (Docker
10 s, Kubernetes 30 s) jälkeen SIGKILLin. Palvelun pitää lopettaa uusien
yhteyksien vastaanotto, viedä käsittelyssä olevat pyynnöt loppuun ja
poistua:

```{.python tiedosto="esimerkit/sovellus/yhteinen.py" osa="sammutus"}
```

Luvun 6 testi pysäyttää api-kontin ja tarkistaa, että viimeinen
lokirivi on `sammutettu`. Jos rivi puuttuisi, prosessi olisi tapettu.

## Kerrokset ja välimuisti

Docker tallentaa jokaisen käskyn tuloksen välimuistiin ja käyttää sitä
uudelleen, jos käsky ja sen syötteet eivät ole muuttuneet. Ensimmäinen
muuttunut käsky mitätöi välimuistin kaikilta sitä seuraavilta käskyiltä.
Siksi järjestys on:

1. peruskuva ja harvoin muuttuvat asetukset,
2. riippuvuuksien kuvaus (`requirements.txt`, `go.mod`, `package.json`),
3. riippuvuuksien asennus,
4. sovelluksen koodi,
5. ajoasetukset.

Kun vain koodi muuttuu, riippuvuuksia ei asenneta uudelleen. Luvun 4
Go-esimerkissä `go.mod` kopioidaan ja riippuvuudet ladataan ennen
lähdekoodia juuri tästä syystä. CI:ssä välimuisti katoaa ajojen välissä,
ellei sitä tallenneta erikseen (`--cache-from`, `--cache-to`, BuildKitin
välimuistit rekisterissä tai CI:n välimuistissa).

## Monivaiheinen rakennus

`FROM … AS nimi` aloittaa uuden vaiheen, ja `COPY --from=nimi` kopioi
tiedostoja aiemmasta vaiheesta. Lopulliseen kuvaan päätyy vain
viimeinen vaihe. Näin rakennustyökalut (kääntäjä, testikirjastot,
`node_modules`-kehityspaketit) eivät kasvata ajokuvaa eivätkä laajenna
sen hyökkäyspintaa.

BuildKit rakentaa vain ne vaiheet, joita kohdevaihe tarvitsee. Siksi
`--target ajo` ei aja testejä: testit ajetaan omana kohteenaan
(`--target testit`) ennen ajokuvan rakennusta, kuten esimerkkien
testi ja luvun 11 putki tekevät.

## Käytännössä

- **Peruskuva kiinni digestillä, päivitykset työkalulla.**
  Toistettavuus ja tietoturvapäivitykset eivät ole ristiriidassa, kun
  päivitys on automaattinen ehdotus, jonka CI testaa.
- **Yksi prosessi, exec-muoto, SIGTERM käsitelty.** Muuten kontin
  pysäytys katkaisee pyynnöt kesken jokaisessa käyttöönotossa.
- **Ei rootia.** Numeerinen `USER` ja kirjoitettavat hakemistot
  luotuina oikealle käyttäjälle.
- **`.dockerignore` aina.** Pienempi konteksti, nopeampi rakennus,
  ei vahingossa kopioituja salaisuuksia.
- **Riippuvuudet ennen koodia.** Välimuisti on nopean rakennuksen
  tärkein tekijä.
- **Salaisuudet eivät kuulu kuvaan.** Ei `ENV SALASANA=…` eikä
  `ARG`-salaisuuksia: molemmat näkyvät kuvan historiassa
  (`docker history`). Rakennusaikaiset salaisuudet välitetään
  BuildKitin `--secret`-liitoksella, ajonaikaiset ympäristöstä.

## Itsearviointi

- Osaat kirjoittaa Dockerfilen, joka ajaa testit omassa vaiheessaan ja
  tuottaa erillisen ajokuvan.
- Osaat selittää, miksi kontti ajetaan ei-root-käyttäjänä ja miten
  kirjoitettavan hakemiston omistajuus hoidetaan.
- Osaat selittää exec- ja kuorimuodon eron ja sen vaikutuksen
  sammutukseen.
- Osaat järjestää Dockerfilen käskyt niin, että välimuisti toimii, ja
  kertoa, miksi salaisuudet eivät kuulu kuvaan.
