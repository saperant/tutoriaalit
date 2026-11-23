# Virheenkäsittely {.runko-virheet}

Go:ssa virhe on tavallinen arvo, joka toteuttaa rajapinnan

```
type error interface {
	Error() string
}
```

Funktio, joka voi epäonnistua, palauttaa virheen viimeisenä
paluuarvonaan, ja kutsuja tarkistaa sen heti. Poikkeuksia ei ole.
Virheiden käsittely on näkyvää, ja jokaisen kutsun kohdalla päätetään,
mitä virheelle tehdään.

## Virheiden luominen ja kääriminen

`errors.New` luo virheen viestistä. `fmt.Errorf` muotoilee viestin, ja
muotoilukoodi `%w` *kääri* (*wrap*) alkuperäisen virheen, jolloin se
säilyy ketjussa tutkittavana. Jokainen kerros lisää tiedon siitä, mitä
se oli tekemässä:

```{.go tiedosto="esimerkit/08-virheet.go" osa="kerrokset"}
```

Viestin muoto `"mitä tehtiin: syy"` tuottaa luettavan ketjun:
`asetusten lataus: palvelu.conf: rivi 2: strconv.Atoi: ...`. Viesti
kirjoitetaan pienellä alkukirjaimella ja ilman loppupistettä, koska se
päätyy usein toisen viestin keskelle.

## Virheiden tutkiminen

Kutsuja tutkii virhettä kahdella funktiolla, jotka käyvät läpi koko
käärintäketjun:

- `errors.Is(err, kohde)` vertaa *vartijavirheeseen* (*sentinel
  error*), joka on pakettitason muuttuja, kuten `io.EOF` tai
  `fs.ErrNotExist`.
- `errors.As(err, &kohde)` etsii ketjusta tiettyä tyyppiä olevan virheen
  ja sijoittaa sen muuttujaan, jolloin sen kenttiä voi lukea.

Oma virhetyyppi kantaa lisätietoa. `Unwrap`-metodi liittää sen
ketjuun:

```{.go tiedosto="esimerkit/08-virheet.go" osa="tyypit"}
```

```{.go tiedosto="esimerkit/08-virheet.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-virheet.odotettu"}
```

Vertailu `err == ErrEiLoydy` ei toimisi käärityn virheen kanssa, ja
tyyppivarmistus `err.(*RiviVirhe)` ei löytäisi ketjun syvemmältä. Siksi
`errors.Is` ja `errors.As` ovat ainoat oikeat tavat.

## Useampi virhe

`errors.Join` (Go 1.20) yhdistää virheet. Se on hyödyllinen
validoinnissa, jossa kaikki virheet halutaan raportoida kerralla, ja
siivouksessa, jossa sekä varsinainen että sulkemisvirhe säilytetään
(luku 4):

```{.go tiedosto="esimerkit/08-virheet.go" osa="validointi"}
```

`errors.Is` ja `errors.As` tutkivat myös yhdistetyn virheen kaikki
osat.

## Paniikki ja recover

`panic` keskeyttää funktion, suorittaa lykätyt kutsut ja purkaa pinoa,
kunnes ohjelma kaatuu tai `recover` pysäyttää purkamisen. Ajonaikaiset
virheet, kuten indeksi rajojen ulkopuolella, nil-osoitin ja kirjoitus
nil-karttaan, aiheuttavat paniikin.

Paniikki on tarkoitettu ohjelmointivirheille, ei odotettaville
virhetilanteille. Yleinen hyväksytty käyttö on `Must`-funktio, joka
paniikoi alustuksessa vakioarvon virheestä:

```{.go tiedosto="esimerkit/08-must.kaatuu.go"}
```

```{.tuloste tiedosto="esimerkit/08-must.virhe"}
```

`recover` toimii vain lykätyssä funktiossa. Sitä käytetään
rajapinnoilla, joilla yksittäisen tehtävän ohjelmointivirhe ei saa
kaataa koko palvelua. `net/http`-palvelin tekee näin jokaiselle
pyynnölle.

```{.go tiedosto="esimerkit/08-recover.go" osa="turvallinen"}
```

```{.tuloste tiedosto="esimerkit/08-recover.odotettu"}
```

Paniikki toisessa goroutinessa kaataa koko ohjelman, eikä
pääohjelman `recover` voi pysäyttää sitä. Jokainen goroutine, jonka
paniikki on siedettävä, tarvitsee oman `recover`-käsittelynsä.

## Käytännössä

- **Käsittele virhe kerran.** Joko käsittele virhe (korjaa,
  käytä oletusta, raportoi) tai palauta se kontekstin kanssa, mutta älä
  molempia. Kirjaaminen lokiin ja palauttaminen tuottaa saman virheen
  lokiin monta kertaa.
- **Lisää konteksti, älä toista sitä.** Kukin kerros kertoo oman
  tekemisensä (`"asetusten lataus: %w"`). Funktion omat parametrit
  kuuluvat sen omaan viestiin, ei kutsujan.
- **`%w` vai `%v`?** `%w` tekee alemman kerroksen virheestä osan omaa
  rajapintaasi: kutsuja voi alkaa riippua siitä. Kun toteutuksen
  yksityiskohta halutaan piilottaa, käytä `%v`.
- **Vartijavirhe vai virhetyyppi?** Vartijavirhe riittää, kun kutsuja
  tarvitsee vain tiedon virheen lajista (`ErrEiLoydy`). Virhetyyppi
  tarvitaan, kun kutsuja tarvitsee tietoja (rivinumero, HTTP-tila).
- **Älä vertaa virheiden tekstiä.** Viesti on ihmisille ja voi muuttua.
- **Älä jätä virhettä huomiotta hiljaa.** Jos virhe tarkoituksella
  ohitetaan, kirjoita `_ =` ja kommentti. `errcheck`- ja
  `staticcheck`-työkalut löytävät unohdetut virheet.
- **Paniikki on bugi.** Kirjastofunktio ei paniikoi syötteen takia,
  eikä paniikki ylitä paketin rajaa. `Must`-funktiot ovat poikkeus
  alustuksessa.
- **Hinta.** Virheen palauttaminen on tavallinen paluuarvo, ja
  onnistunut polku on lähes ilmainen. `fmt.Errorf` allokoi, mikä
  merkitsee vain hyvin kuumissa poluissa, joissa virhe on yleinen
  (esim. `io.EOF` on valmiiksi luotu vartijavirhe). Paniikki ja
  `recover` ovat moninkertaisesti kalliimpia kuin virheen palautus.

## Itsearviointi

- Osaat palauttaa ja kääriä virheitä `fmt.Errorf`-funktiolla ja
  `%w`-koodilla niin, että ketju on luettava.
- Osaat tutkia virheitä `errors.Is`- ja `errors.As`-funktioilla ja
  kertoa, miksi `==` ja tyyppivarmistus eivät riitä.
- Osaat määritellä oman virhetyypin `Unwrap`-metodeineen ja päättää,
  milloin vartijavirhe riittää.
- Osaat yhdistää virheitä `errors.Join`-funktiolla.
- Osaat kertoa, milloin paniikki on oikea reaktio ja miten `recover`
  rajaa paniikin vaikutuksen.
