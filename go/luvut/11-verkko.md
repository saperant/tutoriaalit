# Verkkopalvelut net/http-paketilla

Go:n standardikirjasto sisältää tuotantokelpoisen HTTP-palvelimen ja
-asiakkaan. Monet Go-palvelut eivät käytä kehystä lainkaan. Tämä luku
näyttää Go:n välineet ja idiomit. HTTP-protokolla, REST-rajapintojen
suunnittelu, tunnistautuminen ja tietokannat kuuluvat taitoihin
*Verkko-ohjelmointi* ja *Taustapalvelut*.

## Käsittelijät ja reititys

Palvelimen keskeinen rajapinta on

```
type Handler interface {
	ServeHTTP(ResponseWriter, *Request)
}
```

`http.HandlerFunc` muuntaa tavallisen funktion käsittelijäksi.
`http.ServeMux` reitittää pyynnöt. Go 1.22 toi reititysmalleihin metodin
ja polkuparametrit: `"GET /muistiinpanot/{id}"`, josta parametri luetaan
`r.PathValue("id")`-kutsulla. Väärä metodi tuottaa automaattisesti
vastauksen 405.

```{.go tiedosto="esimerkit/11-palvelu.go" osa="tyypit"}
```

```{.go tiedosto="esimerkit/11-palvelu.go" osa="reitit"}
```

Rakenteen kenttien *tagit* (`` `json:"otsikko"` ``) ohjaavat
`encoding/json`-pakettia: kentän nimi JSONissa ja `omitempty` tyhjän
arvon pois jättämiseen. Vain julkiset kentät koodataan.

## Pyynnön käsittely

Käsittelijä lukee pyynnön, validoi sen, muuttaa tilaa lukon suojassa ja
kirjoittaa vastauksen. Jokainen pyyntö käsitellään omassa
goroutinessaan, joten jaettu tila tarvitsee lukon.

```{.go tiedosto="esimerkit/11-palvelu.go" osa="kasittelijat"}
```

- `http.MaxBytesReader` rajaa rungon koon. Ilman rajaa asiakas voi
  lähettää gigatavuja.
- `DisallowUnknownFields` hylkää tuntemattomat kentät, jolloin
  kirjoitusvirheet eivät katoa hiljaa.
- Otsakkeet asetetaan ennen `WriteHeader`-kutsua. Ensimmäinen `Write`
  lähettää otsakkeet tilakoodilla 200, jos tilaa ei ole asetettu.
- Validointivirhe palauttaa tilakoodin 4xx ja koneluettavan viestin.

## Välikerros

Välikerros (*middleware*) on funktio, joka saa käsittelijän ja palauttaa
uuden käsittelijän. Ketju koostetaan kääreistä: lokitus, tunnistautuminen,
aikarajat, paniikin käsittely.

```{.go tiedosto="esimerkit/11-palvelu.go" osa="valikerros"}
```

## Testaus ja asiakas

`httptest.NewServer` käynnistää oikean palvelimen paikalliseen porttiin.
`httptest.NewRecorder` kutsuu käsittelijää suoraan ilman verkkoa, mikä
sopii yksikkötesteihin. Esimerkki ajaa pyynnöt oikean asiakkaan kautta:

```{.go tiedosto="esimerkit/11-palvelu.go" osa="asiakas"}
```

```{.tuloste tiedosto="esimerkit/11-palvelu.odotettu"}
```

`http.Client`-oliolla on oltava aikakatkaisu. Oletusasiakas
`http.DefaultClient` ja funktiot `http.Get` ja `http.Post` odottavat
ikuisesti, jos palvelin ei vastaa. Vastauksen runko suljetaan aina,
muuten yhteys ei palaa yhteysaltaaseen. Asiakas on säieturvallinen, ja
sitä käytetään uudelleen, jotta yhteydet säilyvät.

## Tuotantokelpoinen palvelin

`http.ListenAndServe` ei aseta aikakatkaisuja, joten hidas tai
vihamielinen asiakas voi pitää yhteyksiä auki loputtomasti. Palvelin
luodaan siksi `http.Server`-rakenteena. Hallittu sammutus lopettaa
uusien yhteyksien vastaanoton ja odottaa, että käsittelyssä olevat
pyynnöt valmistuvat:

```{.go tiedosto="esimerkit/11-sammutus.go" osa="palvelin"}
```

```{.go tiedosto="esimerkit/11-sammutus.go" osa="sammutus"}
```

```{.tuloste tiedosto="esimerkit/11-sammutus.odotettu"}
```

Konttiympäristö lähettää prosessille `SIGTERM`-signaalin ennen
lopettamista. `signal.NotifyContext` muuntaa signaalin kontekstin
peruutukseksi, ja sammutus alkaa siitä.

## Käytännössä

- **Käsittelijä on ohut.** Se jäsentää pyynnön, kutsuu
  sovelluslogiikkaa ja muotoilee vastauksen. Logiikka on omassa
  paketissaan, ja sitä voi testata ilman HTTP:tä.
- **Riippuvuudet rakenteeseen, ei globaaleihin.** Käsittelijät ovat
  rakenteen metodeja (`p.luo`), ja rakenne saa tietokannan, lokin ja
  asetukset konstruktorissa.
- **Pyynnön konteksti eteenpäin.** `r.Context()` perutaan, kun asiakas
  katkaisee yhteyden. Välitä se tietokanta- ja verkkokutsuille, jotta
  turha työ loppuu.
- **Aikakatkaisut kaikkialle**: palvelimen `ReadHeaderTimeout` ja
  muut aikarajat, asiakkaan `Timeout` ja pyyntökohtaiset kontekstit.
- **Rajoita syötteen koko ja validoi.** `MaxBytesReader`, tuntemattomien
  kenttien hylkäys ja eksplisiittinen validointi rajalla.
- **Kehys tarvittaessa.** Reititin `chi` ja kehykset kuten `echo` ja
  `gin` tuovat valmiita välikerroksia, mutta Go 1.22:n `ServeMux`
  riittää useimpiin palveluihin. gRPC-palveluihin käytetään
  `google.golang.org/grpc`-kirjastoa.
- **Hinta.** Goroutine pyyntöä kohden on halpa. `encoding/json` käyttää
  heijastusta ja on suurten vastausten pullonkaula; koodin tuottavat
  vaihtoehdot ja `json.Encoder`-virta auttavat, kun mittaus osoittaa
  tarpeen.

## Itsearviointi

- Osaat kirjoittaa HTTP-käsittelijöitä ja reitittää pyyntöjä Go 1.22:n
  `ServeMux`-malleilla.
- Osaat koodata ja purkaa JSONia rakenteiden tageilla ja validoida
  pyynnön turvallisesti.
- Osaat kirjoittaa välikerroksen ja koostaa niistä ketjun.
- Osaat testata palvelua `httptest`-paketilla ja käyttää
  `http.Client`-asiakasta aikakatkaisun kanssa.
- Osaat konfiguroida `http.Server`-palvelimen aikarajat ja toteuttaa
  hallitun sammutuksen.
