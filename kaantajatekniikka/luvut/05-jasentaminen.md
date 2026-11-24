# Jäsentäminen

**Jäsennin** (*parser*) tarkistaa, että tokenien jono noudattaa
kielioppia, ja rakentaa siitä syntaksipuun. Jäsennysmenetelmiä on
kaksi pääperhettä:

- **Ylhäältä alas** (*top-down*, LL): aloitetaan kieliopin
  alkusymbolista ja valitaan säännöt seuraavien tokenien perusteella.
  Käsin kirjoitettuna tämä on *rekursiivisesti etenevä jäsennin*
  (*recursive descent*).
- **Alhaalta ylös** (*bottom-up*, LR): kootaan tokeneista pinossa
  isompia rakenteita ja *redusoidaan* ne säännöiksi. Taulukot tuottaa
  generaattori, kuten yacc, Bison tai Menhir.

Lähes kaikki tuotantokääntäjät (GCC:n C- ja C++-etuosa, Clang, Go,
Rust, V8, javac) käyttävät käsin kirjoitettua rekursiivisesti etenevää
jäsennintä. Syyt ovat käytännöllisiä: koodi on luettavaa, virheilmoitukset
voi räätälöidä, ja kielen erikoistapaukset on helppo käsitellä.

## Rekursiivisesti etenevä jäsennin

Menetelmän idea on suora: jokaista kieliopin sääntöä vastaa funktio,
joka jäsentää säännön ja palauttaa puun. Säännön vaihtoehto valitaan
**ennakoimalla** (*lookahead*) seuraavaa tokenia. Jäsentimen tila on
vain kohta tokenilistassa; apufunktiot katsovat ja kuluttavat
tokeneita:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="odota"}
```

`odota` on jäsentimen tärkein apufunktio: se kuluttaa odotetun tokenin
tai raportoi virheen. Virheen jälkeen se heittää poikkeuksen, jonka
käsittely kuvataan luvussa 6.

Ohjelma on jono funktioita ja funktio otsikko ja lohko. Funktiot
`ohjelma`, `funktio` ja `tyyppi` seuraavat kielioppia lähes rivi
riviltä: `odota(Laji::Fn)`, `odota(Laji::Tunniste)`, parametrilista
silmukkana `do { ... } while (vastaa(Laji::Pilkku))` ja niin edelleen.

Lauseen vaihtoehto valitaan ensimmäisestä tokenista: `var`, `if`,
`while`, `return`, `print` ja `{` aloittavat kukin eri lauseen.
Esittelyn jäsennys näyttää, miten säännön osat kuluttavat tokenit
järjestyksessä:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="lause"}
```

Muut avainsanalla alkavat lauseet ovat samanlaisia. Ainoa hankala
tapaus on sijoitus: sekä `x = 1;` että `x + 1;` alkavat tunnisteella.
Sijoitus tunnistetaan katsomalla *kahta* tokenia eteenpäin, eli
kielioppi on LL(2) tässä kohdassa:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="sijoitus"}
```

`else if` jäsennetään rekursiivisella kutsulla, joka tuottaa
sisäkkäisen `Jos`-lauseen. Ehdon ympärillä ei ole sulkeita, joten
ehto päättyy siihen, mihin lauseke päättyy; seuraava `{` aloittaa
lohkon. Tämä toimii, koska Kiden lausekkeissa ei ole aaltosulkeita.
Rust ja Go tekevät saman valinnan ja joutuvat siksi kieltämään
tietueliteraalit ehdoissa.

## Lausekkeet Prattin menetelmällä

Lausekkeiden kielioppi on kerrostettu (luku 2): `tai` → `ja` →
`yhtasuuruus` → `vertailu` → `summa` → `tulo` → `unaari`. Suoraan
koodiksi kirjoitettuna siitä tulisi seitsemän lähes samanlaista
funktiota, ja jokainen lauseke kulkisi kaikkien läpi. **Prattin
menetelmä** (*Pratt parsing*, *top-down operator precedence*, 1973)
korvaa kerrokset taulukolla: jokaisella binäärioperaattorilla on
**sitovuus** (*binding power*).

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="sitovuus"}
```

Jäsennin lukee ensin *etuliitteen* (luku, nimi, sulkulauseke tai
unaarinen operaattori) ja jatkaa sitten silmukassa niin kauan kuin
seuraava operaattori sitoo tiukemmin kuin raja `minimi`:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="pratt"}
```

Algoritmi on lyhyt, mutta se kannattaa käydä läpi esimerkillä.
Lausekkeessa `1 - 2 * 3 - 4`:

1. `lauseke(0)` lukee `1`. Seuraava `-` (5) > 0, joten se kuluttaa
   `-` ja kutsuu `lauseke(5)`.
2. `lauseke(5)` lukee `2`. Seuraava `*` (6) > 5, joten se kuluttaa
   `*` ja kutsuu `lauseke(6)`, joka lukee `3` ja palaa, koska `-` (5)
   ei ole > 6. Tulos on `(* 2 3)`.
3. `lauseke(5)` näkee `-` (5), joka ei ole > 5, ja palaa: oikea puoli
   on `(* 2 3)`. Ulompi taso muodostaa `(- 1 (* 2 3))`.
4. `lauseke(0)` näkee jälleen `-` (5) > 0 ja muodostaa
   `(- (- 1 (* 2 3)) 4)`.

Vasen assosiatiivisuus syntyy vertailusta `voima <= minimi`: saman
tason operaattori pysäyttää oikean puolen jäsentämisen. Oikealle
assosiatiivinen operaattori, kuten potenssi `**` monessa kielessä,
saadaan jäsentämällä oikea puoli rajalla `voima - 1`. Unaariset
operaattorit jäsentävät operandinsa rajalla, joka on kaikkia
binäärioperaattoreita suurempi, joten `-a * b` on `(* (- a) b)`.

Presedenssin oikeellisuus testataan kultaisella tulosteella:

```{.rust tiedosto="esimerkit/naytteet/presedenssi.kide"}
```

```{.tuloste tiedosto="esimerkit/naytteet/ast-presedenssi.txt"}
```

Prattin jäsennin on helppo laajentaa: uusi operaattori on yksi rivi
sitovuustauluun. Jälkiliitteiset operaattorit (funktiokutsu,
taulukon indeksi `a[i]`, kentän valinta `a.b`) käsitellään samassa
silmukassa: ne ovat operaattoreita, joilla on suuri sitovuus ja oma
jäsennyskoodinsa. Kidessä funktiokutsu on yksinkertaisuuden vuoksi
etuliitteen osa.

## Moniselitteisyys ja kieliopin luokat

Kaikkia kielioppeja ei voi jäsentää rekursiivisella etenemisellä.
Sääntö `summa = summa "+" tulo` on **vasemmalle rekursiivinen**:
funktio `summa` kutsuisi heti itseään kuluttamatta tokenia, ja
jäsennin jäisi päättymättömään rekursioon. Siksi LL-kieliopeissa
toisto kirjoitetaan silmukkana `tulo { "+" tulo }`, ja Prattin
menetelmä tekee saman.

Toinen klassinen ongelma on **roikkuva else** (*dangling else*): C:n
`if (a) if (b) x; else y;` voidaan jäsentää kahdella tavalla. Kidessä
ongelmaa ei ole, koska `if`-runko on aina lohko. Kielen suunnittelija
voi siis poistaa moniselitteisyyden kieliopista sen sijaan, että
jäsennin ratkaisisi sen sääntönä.

LR-jäsentimet hyväksyvät laajemman joukon kielioppeja (myös vasemmalle
rekursiiviset), ja generaattori ilmoittaa moniselitteisyydet
*konflikteina*. Ne sopivat hyvin kieliin, joiden kielioppi on valmis ja
vakaa, kuten SQL:ään (PostgreSQL käyttää Bisonia).

## Käytännössä

- **Kirjoita jäsennin käsin, jos kieli on sinun.** Rekursiivisesti
  etenevä jäsennin ja Prattin lausekejäsennin riittävät useimpiin
  kieliin, ja ne ovat helppoja debugata.
- **Käytä Prattia lausekkeisiin.** Sitovuustaulukko on luettavampi kuin
  seitsemän kerrosta funktioita, ja uusi operaattori on yksi rivi.
- **Suunnittele kielioppi jäsennettäväksi.** Yhden tokenin ennakointi
  lähes kaikkialla tekee jäsentimestä yksinkertaisen ja nopean, ja
  ihminenkin lukee sellaista kieltä helpommin.
- **Testaa presedenssi ja assosiatiivisuus erikseen.** Kultainen
  S-lauseketuloste paljastaa virheen, jota tulosten vertailu ei
  välttämättä paljasta (esim. `a - b - c` pienillä luvuilla).

## Itsearviointi

- Osaat kirjoittaa rekursiivisesti etenevän jäsentimen kieliopista
  niin, että jokaista sääntöä vastaa funktio.
- Osaat selittää Prattin menetelmän sitovuuksilla ja käydä läpi
  lausekkeen jäsennyksen askel askeleelta.
- Osaat tehdä operaattorista vasemmalle tai oikealle assosiatiivisen.
- Osaat tunnistaa vasemman rekursion ja roikkuvan elsen ja kertoa,
  miten ne poistetaan kieliopista.
