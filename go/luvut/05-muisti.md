# Muisti, osoittimet ja allokaatiot {.runko-muisti}

Go hallitsee muistia roskienkeruulla: ohjelmoija ei vapauta muistia,
eikä roikkuvia osoittimia tai vapautetun muistin käyttöä ole. Kehittäjän
on silti ymmärrettävä, mikä kopioituu, mikä jaetaan ja mikä varataan
keosta, koska nämä määräävät sekä oikeellisuuden että suorituskyvyn.

## Arvot ja viitteet

Sijoitus ja parametrin välitys kopioivat aina arvon. Tyypistä riippuu,
mitä arvo sisältää:

| Tyyppi | Kopioituu | Jaetaan |
|--------|-----------|---------|
| perustyypit, rakenteet, taulukot `[N]T` | koko sisältö | ei mitään |
| osoitin `*T` | osoite | osoitettu arvo |
| viipale `[]T` | otsake: osoitin, pituus, kapasiteetti | taustataulukko |
| merkkijono `string` | otsake: osoitin ja pituus | muuttumattomat tavut |
| kartta, kanava, funktio | osoitin sisäiseen rakenteeseen | koko rakenne |
| rajapinta | tyyppi ja arvo (tai osoitin arvoon) | osoitettu arvo |

```{.go tiedosto="esimerkit/05-arvot.go" osa="kopiot"}
```

```{.tuloste tiedosto="esimerkit/05-arvot.odotettu"}
```

## Osoittimet

Osoitin `*T` osoittaa arvoon, `&x` ottaa osoitteen ja `*p` viittaa
arvoon. Osoitinaritmetiikkaa ei ole (paitsi `unsafe`-paketissa), ja
kenttään viitataan suoraan: `p.X` tarkoittaa `(*p).X`. Paikallisen
muuttujan osoitteen voi palauttaa turvallisesti; kääntäjä siirtää
muuttujan kekoon tarvittaessa.

```{.go tiedosto="esimerkit/05-arvot.go" osa="osoitin"}
```

Metodin vastaanottaja on joko arvo tai osoitin. Arvovastaanottaja saa
kopion, osoitinvastaanottaja voi muuttaa alkuperäistä. Kutsu `a.M()`
ottaa osoitteen automaattisesti, kun `a` on muuttuja:

```{.go tiedosto="esimerkit/05-arvot.go" osa="vastaanottajat"}
```

Nil-osoittimen kautta lukeminen kaataa ohjelman paniikkiin:

```{.go tiedosto="esimerkit/05-nil.kaatuu.go"}
```

```{.tuloste tiedosto="esimerkit/05-nil.virhe"}
```

Go:ssa ei ole nollaturvallisia tyyppejä. Funktio, joka voi palauttaa
`nil`-osoittimen, palauttaa yleensä myös `bool`- tai `error`-arvon,
jolloin kutsuja joutuu käsittelemään puuttuvan tapauksen.

## Pino, keko ja pakoanalyysi

Go:n kääntäjä päättää itse, varataanko muuttuja pinosta vai keosta.
*Pakoanalyysi* (*escape analysis*) varaa muuttujan keosta, jos se voi
elää funktion jälkeen: osoite palautetaan, tallennetaan kekoon tai
annetaan rajapintana funktiolle, jota kääntäjä ei tunne. Muuten
muuttuja on pinossa, ja sen varaaminen on lähes ilmaista.

```{.go tiedosto="esimerkit/05-allokaatiot.go" osa="pako"}
```

Kääntäjän päätökset näkyvät lipulla `-gcflags=-m`:

```
$ go build -gcflags=-m 05-allokaatiot.go
./05-allokaatiot.go:20:48: &Piste{...} escapes to heap
./05-allokaatiot.go:34:11: make([]int, 0, n) escapes to heap
```

Allokaatiot voi mitata ohjelmasta `testing.AllocsPerRun`-funktiolla ja
testeissä lipulla `-benchmem` (luku 12):

```{.go tiedosto="esimerkit/05-allokaatiot.go" osa="kokoelmat"}
```

```{.tuloste tiedosto="esimerkit/05-allokaatiot.odotettu"}
```

- Rakenne arvona ei allokoi, osoitin palautettuna allokoi.
- `append` ilman kapasiteettia varaa tuhannen alkion kasvatukseen
  kaksitoista kertaa. Kun koko tiedetään, yksi `make` riittää.
- Merkkijonon kasvattaminen `+=`-operaattorilla kopioi koko
  merkkijonon joka kerta, mikä on neliöllinen. `strings.Builder`
  kasvattaa puskuria kuten `append`.

## Roskienkeruu

Go:n roskienkerääjä on rinnakkainen, merkitse ja pyyhi -periaatteella
toimiva keruu, joka ei siirrä olioita. Se toimii sovelluksen rinnalla ja
pysäyttää ohjelman vain hetkiksi, tyypillisesti alle millisekunniksi.
Keruun kokonaiskuorma on kuitenkin suoraan verrannollinen allokaatioihin.

| Asetus | Merkitys |
|--------|----------|
| `GOGC=100` | keruu alkaa, kun keko on kasvanut 100 % edellisen keruun jälkeen |
| `GOMEMLIMIT=2GiB` | pehmeä muistiraja: keruu tihenee rajan lähellä (Go 1.19) |
| `GODEBUG=gctrace=1` | tulostaa jokaisen keruun tiedot |
| `runtime.ReadMemStats` | keon koko ja keruiden määrä ohjelmasta |

Kontissa ajettavalle palvelulle asetetaan `GOMEMLIMIT` hieman kontin
muistirajan alle. Muuten ohjelma voi kasvattaa kekoaan, kunnes
ydin lopettaa sen muistin loputtua.

## Resurssit

Roskienkeruu vapauttaa vain muistin. Tiedostot, verkkoyhteydet,
lukot ja tietokantayhteydet vapautetaan itse, tavallisesti `defer`-
lauseella heti resurssin saamisen jälkeen (luku 4). Finalisoijia
(`runtime.SetFinalizer`) ei käytetä resurssien hallintaan, koska niiden
suoritusajankohta on määrittelemätön.

## Käytännössä

- **Arvo vai osoitin?** Pienet, muuttumattomat tyypit (piste, aika,
  rahamäärä) välitetään arvoina. Osoitinta käytetään, kun metodi
  muuttaa vastaanottajaa, tyyppi sisältää lukon tai on suuri (nyrkkisääntö:
  yli muutama sana). Kaikki tyypin metodit käyttävät samaa
  vastaanottajalajia.
- **Älä kopioi lukkoa.** Rakennetta, jossa on `sync.Mutex`, ei saa
  kopioida, koska kopio saa oman, erillisen lukon. `go vet` varoittaa
  (`copylocks`).
- **Esivaraa, kun koko tiedetään.** `make([]T, 0, n)`, `make(map[K]V,
  n)` ja `strings.Builder.Grow` poistavat kasvatuksen allokaatiot.
- **Mittaa ennen optimointia.** `-benchmem`, `go test -cpuprofile` ja
  `pprof` kertovat, missä allokaatiot ovat. Pakoanalyysin tulosteella
  selvitetään, miksi jokin pakenee.
- **Uudelleenkäyttö `sync.Pool`-altaalla** kannattaa vain mitatusti
  kuumissa poluissa, kuten puskureissa. Allas tyhjenee roskienkeruussa,
  eikä sitä käytetä yhteyksien säilyttämiseen.
- **Viipale pitää koko taustataulukon elossa.** Pieni viipale suuresta
  taulukosta estää koko taulukon vapautuksen; kopioi tarvittava osa
  (`slices.Clone`).
- **Hinta.** Kekoallokaatio maksaa kymmeniä nanosekunteja ja kasvattaa
  keruun työtä. Arvon muuntaminen rajapinnaksi (`any`) allokoi, jos
  arvo ei ole osoitin tai pieni vakio.

## Itsearviointi

- Osaat kertoa, mitä sijoitus kopioi rakenteelle, taulukolle,
  viipaleelle, kartalle ja osoittimelle.
- Osaat valita arvo- ja osoitinvastaanottajan välillä perustellusti.
- Osaat selittää pakoanalyysin ja tarkistaa sen tulokset lipulla
  `-gcflags=-m`.
- Osaat mitata allokaatioita ja vähentää niitä esivaraamalla.
- Osaat kertoa, mitä `GOGC` ja `GOMEMLIMIT` säätävät ja milloin niitä
  tarvitaan.
