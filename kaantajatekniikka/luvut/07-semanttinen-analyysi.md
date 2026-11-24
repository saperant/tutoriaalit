# Semanttinen analyysi

Jäsennin takaa, että ohjelma on kieliopin mukainen. **Semanttinen
analyysi** tarkistaa säännöt, joita kielioppi ei ilmaise: jokainen
nimi viittaa esittelyyn, operaattorit saavat oikeantyyppiset operandit,
funktioita kutsutaan oikealla määrällä argumentteja ja jokainen polku
palauttaa arvon. Samalla se kirjoittaa puuhun tiedot, joita myöhemmät
vaiheet tarvitsevat: mihin muuttujaan kukin nimi viittaa ja mikä on
kunkin lausekkeen tyyppi.

Analyysi on yksi rekursiivinen läpikäynti puun yli. Siinä on kaksi
pääosaa: **nimien sidonta** (*name resolution*) ja
**tyyppitarkistus** (*type checking*).

## Symbolitaulu ja näkyvyysalueet

**Symbolitaulu** kuvaa nimet niiden merkityksiksi. Koska Kidessä
lohkot avaavat uusia näkyvyysalueita, taulu on pino hajautustauluja:
uusi alue lisätään pinoon lohkon alussa ja poistetaan lopussa, ja nimeä
etsitään sisimmästä alueesta ulospäin.

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="symbolit"}
```

Nimen merkitys on *muuttujan numero* funktion sisällä. Analyysi
numeroi muuttujat esittelyjärjestyksessä (parametrit ensin) ja kirjoittaa
numeron jokaiseen `Nimi`-solmuun. Myöhemmille vaiheille nimet ovat
pelkkiä numeroita, eikä niiden tarvitse tietää näkyvyysalueista
mitään: kaksi samannimistä muuttujaa eri lohkoissa ovat eri numeroita.

Esittely lisää nimen nykyiselle alueelle, sijoitus etsii olemassa
olevan muuttujan, ja `if`, `while` ja lohko avaavat ja sulkevat alueen.
Esittely näyttää tältä:

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="esittely"}
```

Esittelyssä arvo tarkistetaan *ennen* kuin uusi nimi lisätään. Siksi
`var x = x + 10;` sisemmässä lohkossa viittaa oikealla puolella ulompaan
muuttujaan. Valinta on kielen suunnittelupäätös: Rust toimii samoin,
C:ssä uusi muuttuja on näkyvissä jo omassa alustimessaan (ja sen arvo on
silloin määrittelemätön).

```{.rust tiedosto="esimerkit/ohjelmat/nakyvyys.kide"}
```

```{.tuloste tiedosto="esimerkit/ohjelmat/nakyvyys.odotettu"}
```

Funktiot ovat omassa taulussaan, joka täytetään ennen funktioiden
runkojen tarkistusta. Siksi funktio voi kutsua myöhemmin määriteltyä
funktiota, ja keskinäinen rekursio toimii ilman C:n kaltaisia
esittelyjä. Samassa ensimmäisessä läpikäynnissä tarkistetaan, että
funktion nimi on yksikäsitteinen ja että `main() -> int` on olemassa.

## Tyyppitarkistus

Lausekkeen tyyppi lasketaan alhaalta ylös: lehtien tyypit tunnetaan
(luku on `int`), ja operaattorin tyyppi määräytyy operandien tyypeistä
luvun 2 sääntöjen mukaan. Tulos kirjoitetaan solmuun. Binäärioperaatiot
on siirretty omaan funktioonsa, joka tarkistaa operandit operaattorin
mukaan (aritmetiikka `int`, vertailut `int` ja tulos `bool`, `&&` ja
`||` `bool`, yhtäsuuruus samat tyypit):

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="lauseke"}
```

Kidessä tyypit ovat pelkkiä vakioita, joten tyyppien vertailu on
yhtäsuuruusvertailu. Monimutkaisemmissa kielissä tyypit ovat puita
(funktiotyypit, geneeriset tyypit), ja tyyppipäättely ratkaisee
yhtälöitä *unifikaatiolla* (Hindley–Milner ML-kielissä ja Haskellissa,
paikallinen päättely Rustissa ja C++:n `auto`).

Funktiokutsu tarkistaa nimen, argumenttien määrän ja jokaisen
argumentin tyypin. Kutsun tyyppi on funktion paluutyyppi silloinkin,
kun argumenteissa oli virhe, jotta virhe ei leviä ympäröivään
lausekkeeseen:

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="kutsu"}
```

## Tuntematon tyyppi

Jos nimi on tuntematon, sen tyyppi on `Tuntematon`, ja tämä tyyppi
kelpaa kaikkialle. Ilman sitä yksi kirjoitusvirhe tuottaisi virheen
jokaisessa lausekkeessa, jossa nimi esiintyy, ja vielä niissä,
joissa näiden lausekkeiden tulos esiintyy. Sääntö on yhdessä paikassa:

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="odota"}
```

Samaa tekniikkaa kutsutaan monessa kääntäjässä *virhetyypiksi* (rustc:n
`{type error}`, Clangin `<recovery-expr>`). Esimerkki:

```{.rust tiedosto="esimerkit/virheet/tyypit.kide"}
```

```{.tuloste tiedosto="esimerkit/virheet/tyypit.virhe"}
```

Rivin 12 lausekkeessa on kolme virhettä, ja ne raportoidaan kerran
kukin. Kutsu `jaollinen(1)` palauttaa silti `bool`-tyypin, ja `bool +`
on todellinen virhe. Rivi 13 näyttää, miksi vertailut eivät ketjuunnu:
`1 < 2 < 3` on `(1 < 2) < 3`, eli totuusarvon ja luvun vertailu.
C hyväksyy sen ja laskee `1 < 3`; Python tulkitsee sen kahdeksi
vertailuksi; Kide hylkää sen.

## Paluupolut

Funktion jokaisen polun on päätyttävä `return`-lauseeseen. Tarkistus
on pieni rekursiivinen analyysi, joka on *konservatiivinen*: se voi
hylätä ohjelman, joka todellisuudessa aina palauttaa (esimerkiksi
`while true { return 1; }`), mutta ei koskaan hyväksy ohjelmaa, joka
voi pudota funktion lopusta.

```{.cpp tiedosto="esimerkit/kide/tarkistin.cpp" osa="palauttaa"}
```

Rajoitus on väistämätön: ehdon arvo ajonaikana on yleisessä
tapauksessa ratkeamaton (pysähtymisongelma). Kielet valitsevat eri
kompromisseja. Java vaatii samanlaisen tarkistuksen kuin Kide ja
käsittelee vakioehdon `while (true)` erikoistapauksena. C ja C++
hyväksyvät funktion, joka putoaa lopusta, ja sen paluuarvon käyttö on
määrittelemätöntä; GCC varoittaa (`-Wreturn-type`).

Tiedosto `virheet/nimet.kide` kokoaa muut nimivirheet: kahdesti
määritelty funktio, parametrin kanssa samanniminen muuttuja, puuttuva
`return`, lohkon ulkopuolella käytetty muuttuja ja tuntematon funktio:

```{.tuloste tiedosto="esimerkit/virheet/nimet.virhe"}
```

## Käytännössä

- **Sido nimet kerran.** Kun analyysi kirjoittaa jokaiseen nimeen
  viitteen esittelyyn, myöhemmät vaiheet eivät tarvitse
  näkyvyyssääntöjä, ja kielipalvelimen "siirry määrittelyyn" saadaan
  ilmaiseksi.
- **Käytä virhetyyppiä.** Yksi virhe tuottaa yhden ilmoituksen.
- **Kerää esittelyt ennen runkoja.** Kahden läpikäynnin rakenne
  (ensin allekirjoitukset, sitten rungot) poistaa järjestysriippuvuudet.
- **Konservatiivinen analyysi on rehellinen.** Kun tarkistus ei voi
  tietää, se hylkää; virheilmoituksen on silloin kerrottava, mitä
  vaaditaan, ei väitettävä ohjelmaa vääräksi.

## Itsearviointi

- Osaat toteuttaa sisäkkäiset näkyvyysalueet pinona hajautustauluja ja
  sitoa jokaisen nimen esittelyynsä.
- Osaat kirjoittaa tyyppitarkistimen, joka laskee lausekkeiden tyypit
  alhaalta ylös ja raportoi virheet sijainteineen.
- Osaat estää seurannaisvirheet tuntemattomalla tyypillä.
- Osaat selittää, miksi paluupolkujen tarkistus on konservatiivinen ja
  miten eri kielet käsittelevät funktion lopusta putoamisen.
