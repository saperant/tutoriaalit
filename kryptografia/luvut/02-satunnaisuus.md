# Satunnaisuus

Lähes kaikki kryptografia nojaa salaisuuksiin, joita hyökkääjä ei voi
arvata: avaimiin, nonceihin, suoloihin ja tunnisteisiin. Jos
satunnaislukugeneraattori on ennustettava, mikään sen päälle rakennettu
ei ole turvallinen, olivatpa algoritmit kuinka hyviä tahansa.

## Kaksi lajia satunnaisuutta

*Tilastollinen* satunnaislukugeneraattori, kuten Pythonin `random`
(Mersenne Twister), tuottaa tasaisesti jakautuneita lukuja
simulaatioihin ja peleihin. Sitä ei ole suunniteltu kestämään
hyökkääjää: sen tila voidaan päätellä tulosteista.

*Kryptografisesti turvallinen* generaattori (CSPRNG) on suunniteltu
niin, ettei tulosteista voi päätellä aiempia eikä tulevia arvoja.
Käyttöjärjestelmä ylläpitää sellaista ja syöttää siihen entropiaa
laitteistosta (ajoitukset, keskeytykset, suorittimen satunnaislähde).
Linuxissa sitä luetaan järjestelmäkutsulla `getrandom()` tai
tiedostosta `/dev/urandom`; Pythonissa `os.urandom()` ja `secrets`.

## Mersenne Twisterin ennustaminen

MT19937 palauttaa jokaisella kutsulla yhden 624 sanan tilansa sanoista
sekoitettuna (*tempering*). Sekoitus on bittitason siirtoja ja
XOR-operaatioita, jotka voi kumota:

```{.python tiedosto="esimerkit/02-mt-ennustus.py" osa="kaanto"}
```

Kun 624 peräkkäistä tulostetta on nähty, tila on tiedossa:

```{.python tiedosto="esimerkit/02-mt-ennustus.py" osa="ennustus"}
```

```{.tuloste tiedosto="esimerkit/02-mt-ennustus.odotettu"}
```

Hyökkäys on todellinen: jos palvelu luo salasanan palautuslinkit
`random`-moduulilla ja hyökkääjä pyytää itselleen riittävän monta
linkkiä, hän voi laskea seuraavan käyttäjän linkin. Sama koskee
JavaScriptin `Math.random()`-funktiota ja Javan `java.util.Random`-luokkaa.

## secrets-moduuli

Python-koodissa kaikki turvallisuuteen liittyvä satunnaisuus tulee
`secrets`-moduulista:

```{.python tiedosto="esimerkit/02-tokenit.py" osa="tokenit"}
```

```{.tuloste tiedosto="esimerkit/02-tokenit.odotettu"}
```

Tunnisteen pituus mitataan *entropiana*: 128 bittiä riittää
arvaamattomaksi tunnisteeksi, avaimille käytetään 128–256 bittiä.
Kuusinumeroisessa PIN-koodissa on vain noin 20 bittiä, joten sen on
oltava lyhytikäinen ja yritysten määrää on rajoitettava. UUID:n
versio 4 on satunnainen, mutta UUID-kirjastot eivät lupaa
kryptografista generaattoria; tunnisteiksi kannattaa käyttää
`secrets`-funktioita.

Muita kieliä: Javassa `SecureRandom`, Go:ssa `crypto/rand`, Rustissa
`rand::rngs::OsRng` tai `getrandom`, selaimessa ja Nodessa
`crypto.getRandomValues()`.

## Käytännössä

- **Oletuksena `secrets`.** `random`-moduulia ei käytetä mihinkään,
  mikä liittyy tunnistukseen, avaimiin tai arvaamattomuuteen. Moni
  kehittäjäryhmä estää `random`-moduulin turvallisuuskoodissa
  staattisella analyysillä (esim. Bandit, ruffin S311-sääntö).
- **Ei omaa siementä.** CSPRNG:tä ei siemennetä ajalla tai prosessin
  numerolla, eikä sen tilaa tallenneta. Testeissä deterministisyys
  saavutetaan injektoimalla generaattori, ei siementämällä tuotantoa.
- **Tarpeeksi pitkät tunnisteet.** Istuntotunnisteet ja
  palautuslinkit vähintään 128 bittiä, ja niillä on vanhenemisaika.
- **Virtuaalikoneet ja sulautetut laitteet.** Juuri käynnistyneellä
  laitteella entropiaa voi olla vähän. `getrandom()` odottaa, kunnes
  generaattori on alustettu; `/dev/urandom` ei vanhoissa ytimissä
  odottanut. Kloonatut virtuaalikoneet voivat jakaa saman tilan, jos
  hypervisor ei sekoita sitä.
- **Hinta:** CSPRNG on hitaampi kuin `random`, mutta tunnisteiden
  luonnissa ero on merkityksetön.

## Itsearviointi

- Osaat selittää, miksi tilastollinen satunnaislukugeneraattori ei
  kelpaa avaimiin ja tunnisteisiin.
- Osaat luoda istuntotunnisteet, avaimet ja kertakoodit
  `secrets`-moduulilla ja arvioida niiden entropian.
- Osaat nimetä kryptografisen satunnaislähteen käyttämissäsi kielissä.
