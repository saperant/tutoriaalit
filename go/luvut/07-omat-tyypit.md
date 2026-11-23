# Rakenteet, rajapinnat ja geneerisyys {.runko-omat-tyypit}

Go:ssa ei ole luokkia. Data on rakenteissa, käyttäytyminen metodeissa,
ja yhteinen käyttäytyminen kuvataan rajapinnoilla, jotka tyypit
toteuttavat implisiittisesti. Uudelleenkäyttö tehdään upottamalla ja
geneerisillä funktioilla, ei periytymällä.

## Rakenteet ja konstruktorit

Rakenteen kentät ja metodit näkyvät paketin ulkopuolelle, jos niiden
nimi alkaa isolla kirjaimella. Pienellä kirjaimella alkavat ovat
paketin sisäisiä, mikä on Go:n ainoa kapselointikeino.

Jos tyypin nolla-arvo on kelvollinen, konstruktoria ei tarvita. Jos
tyypillä on invariantti, se luodaan `Uusi`- tai `New`-alkuisella
funktiolla, joka palauttaa osoittimen ja tarvittaessa virheen:

```{.go tiedosto="esimerkit/07-rakenteet.go" osa="konstruktori"}
```

## Upotus

Rakenteeseen voi upottaa toisen tyypin ilman kentän nimeä. Upotetun
tyypin kentät ja metodit *ylennetään* ulomman tyypin omiksi:

```{.go tiedosto="esimerkit/07-rakenteet.go" osa="upotus"}
```

Upotus ei ole periytymistä. `Asiakirja` ei ole `Aikaleima`, eikä sitä
voi antaa funktiolle, joka odottaa `Aikaleima`-arvoa. Ylennetty metodi
saa vastaanottajakseen upotetun kentän, ei ulompaa rakennetta, joten
virtuaalikutsuja ei ole. Upotuksella saadaan delegointi ilman
välitysmetodeja, ja ylennetyt metodit voivat täyttää rajapinnan.

## Rajapinnat

Rajapinta on joukko metodeja. Tyyppi toteuttaa rajapinnan, jos sillä on
kaikki rajapinnan metodit, eikä toteutusta tarvitse ilmoittaa. Siksi
rajapinnan voi määritellä jälkikäteen jo olemassa oleville tyypeille,
myös toisten pakettien tyypeille.

Standardikirjaston tärkeimmät rajapinnat ovat yhden metodin mittaisia:
`io.Reader`, `io.Writer`, `io.Closer`, `fmt.Stringer`, `error` ja
`sort.Interface`. Funktio, joka pyytää `io.Readerin`, toimii tiedoston,
verkkoyhteyden, merkkijonon ja pakatun virran kanssa:

```{.go tiedosto="esimerkit/07-rajapinnat.go" osa="kuluttaja"}
```

Rajapinnan toteuttavan tyypin voi koostaa toisen ympärille. Tämä
*koristelija* (*decorator*) laskee kirjoitetut tavut ja on itsekin
`io.Writer`:

```{.go tiedosto="esimerkit/07-rajapinnat.go" osa="laskuri"}
```

```{.go tiedosto="esimerkit/07-rajapinnat.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-rajapinnat.odotettu"}
```

Tyyppivarmistus `w.(T)` tarkistaa ajonaikana, onko rajapinnan
takana tyyppi `T` tai toteuttaako se rajapinnan `T`. Muoto `v, ok :=`
ei kaadu. Tällä tavoin esimerkiksi `io.Copy` tarkistaa, osaako kohde
kopioinnin itse tehokkaammin (`io.ReaderFrom`).

### Metodijoukot

Osoitinvastaanottajan metodit kuuluvat vain osoitintyypin
metodijoukkoon. Jos yksikin rajapinnan metodi on määritelty
osoitinvastaanottajalle, rajapinnan toteuttaa vain `*T`, ei `T`:

```{.go tiedosto="esimerkit/07-metodijoukko.ei-kaanny.go"}
```

```
cannot use loki (variable of type Muistiloki) as Kirjaaja value in
assignment: Muistiloki does not implement Kirjaaja (method Kirjaa has
pointer receiver)
```

Rivi `var _ Kirjaaja = (*Muistiloki)(nil)` on käännösaikainen
tarkistus siitä, että tyyppi toteuttaa rajapinnan. Se on hyödyllinen,
kun toteutus ja käyttö ovat eri paketeissa.

### Tyyppivalinta

`switch v := x.(type)` haarautuu dynaamisen tyypin mukaan. Haarassa
`v` on haaran tyyppiä, tai alkuperäistä rajapintatyyppiä, jos haarassa
on useita tyyppejä:

```{.go tiedosto="esimerkit/07-rakenteet.go" osa="tyyppivalinta"}
```

```{.tuloste tiedosto="esimerkit/07-rakenteet.odotettu"}
```

`time.Duration` osuu `Stringer`-haaraan, koska haarat tarkistetaan
järjestyksessä. Tyyppivalinta on oikea työkalu suljetulle joukolle
tapauksia, kuten jäsennyspuun solmuille. Avoimelle joukolle metodi
rajapinnassa on parempi.

### Nil-rajapinnan sudenkuoppa

Rajapinta-arvo on pari: dynaaminen tyyppi ja arvo. Se on `nil` vain,
jos *molemmat* puuttuvat. Nil-osoitin, joka sijoitetaan rajapintaan,
tuottaa ei-nil-rajapinnan:

```{.go tiedosto="esimerkit/07-nilrajapinta.go" osa="vaarin"}
```

```{.go tiedosto="esimerkit/07-nilrajapinta.go" osa="oikein"}
```

```{.go tiedosto="esimerkit/07-nilrajapinta.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-nilrajapinta.odotettu"}
```

Sääntö: funktio, jonka paluutyyppi on `error`, palauttaa `nil`-literaalin
eikä koskaan konkreettisen virhetyypin muuttujaa.

## Geneerisyys

Go 1.18 toi tyyppiparametrit. Funktio tai tyyppi saa tyyppiparametrin
hakasulkeissa, ja *rajoite* (*constraint*) on rajapinta, joka kertoo,
mitä tyypillä voi tehdä. `any` sallii kaiken, `comparable` sallii
`==`-vertailun, ja `cmp.Ordered` sallii järjestysvertailut.

```{.go tiedosto="esimerkit/07-geneerinen.go" osa="funktiot"}
```

`~int` tarkoittaa kaikkia tyyppejä, joiden pohjatyyppi on `int`.
Ilman tildeä oma tyyppi `Sentit` ei kelpaisi. Geneerinen tyyppi
määritellään samoin:

```{.go tiedosto="esimerkit/07-geneerinen.go" osa="tyyppi"}
```

```{.tuloste tiedosto="esimerkit/07-geneerinen.odotettu"}
```

Go:n geneerisyys on tarkoituksella rajattu: metodeilla ei voi olla omia
tyyppiparametreja, erikoistamista ja käännösaikaista laskentaa ei ole,
ja tyyppiparametrin nolla-arvo saadaan vain `var nolla T`-lauseella.
Toteutus jakaa koodia saman muotoisten tyyppien kesken
(*GC shape stenciling*), joten geneerinen funktio voi olla hieman
hitaampi kuin käsin kirjoitettu.

## Funktionaaliset optiot

Koska oletusparametreja ja ylikuormitusta ei ole, laajennettava
konstruktori tehdään *funktionaalisilla optioilla*. Optio on funktio,
joka muuttaa rakennettavaa oliota:

```{.go tiedosto="esimerkit/07-optiot.go" osa="optiot"}
```

```{.go tiedosto="esimerkit/07-optiot.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-optiot.odotettu"}
```

Uuden option lisääminen ei muuta kutsujien koodia. Yksinkertaisempi
vaihtoehto on julkinen asetusrakenne (`Config`), jonka nolla-arvot
tarkoittavat oletuksia.

## Käytännössä

- **Rajapinnat kuluttajan puolelle.** Paketti palauttaa konkreettisen
  tyypin, ja käyttäjä määrittelee pienen rajapinnan niistä metodeista,
  joita se tarvitsee. Tästä seuraa sääntö "ota vastaan rajapintoja,
  palauta rakenteita". Testissä rajapinnan tilalle on helppo tehdä
  korvike.
- **Pienet rajapinnat.** Yhden tai kahden metodin rajapinnalla on monta
  toteuttajaa. Suuret rajapinnat kootaan pienistä upottamalla:
  `io.ReadWriteCloser`.
- **Ei rajapintaa yhdelle toteutukselle.** Rajapinta luodaan, kun
  toteutuksia tai käyttäjän tarpeita on useampi, ei etukäteen kuten
  Javassa.
- **`any` vasta viimeisenä keinona.** Tyyppiparametri säilyttää
  tyyppitarkistuksen, `any` siirtää virheet ajonaikaan.
- **Geneerisyys kokoelmiin ja algoritmeihin**, rajapinnat
  käyttäytymiseen. Jos funktio vain kutsuu metodia, rajapinta riittää.
- **Upota harkiten.** Julkisen rakenteen upotus ylentää kaikki upotetun
  tyypin metodit osaksi omaa rajapintaasi. `sync.Mutex`-upotus
  paljastaisi `Lock`-metodin kutsujille, joten lukko on nimetty kenttä.
- **Vastaanottajan nimi** on lyhyt ja johdonmukainen (`t *Tili`), ei
  `this` tai `self`.
- **Hinta.** Rajapintakutsu on epäsuora ja estää yleensä inline-
  laajennuksen; kuumassa silmukassa konkreettinen tyyppi tai
  tyyppiparametri on nopeampi.

## Itsearviointi

- Osaat suunnitella tyypin, jonka nolla-arvo on käyttökelpoinen, ja
  kirjoittaa konstruktorin tyypille, jolla on invariantti.
- Osaat käyttää upotusta delegointiin ja kertoa, miksi se ei ole
  periytymistä.
- Osaat määritellä pienen rajapinnan kuluttajan tarpeesta ja koostaa
  toteutuksia `io.Reader`- ja `io.Writer`-rajapintojen ympärille.
- Osaat selittää metodijoukot ja nil-rajapinnan sudenkuopan.
- Osaat kirjoittaa geneerisen funktion ja tyypin rajoitteineen.
- Osaat toteuttaa funktionaaliset optiot.
