# Vikasietoisuus

Kun palvelu kutsuu toista, riippuvuuden viat muuttuvat sen omiksi
vioiksi. Hidas varasto tekee myynnistä hitaan, ja kaatunut varasto voi
kaataa myynnin, jos myynnin säikeet jäävät odottamaan vastausta, joka
ei koskaan tule. Michael Nygardin kirja *Release It!* (2007) nimesi
mallit, joilla tätä vastaan suojaudutaan: aikaraja, uudelleenyritys,
katkaisija ja laipio. Tämä luku rakentaa ne myynnin saldokyselyyn.
Samat mallit sokettitasolla toteutettuina ovat taidossa
*Verkko-ohjelmointi*.

## Asiakas

Myynti kysyy saldon varastopalvelulta:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/varasto/VarastoPalvelin.java" osa="varasto"}
```

Asiakas erottaa kaksi virheluokkaa. *Pysyvä* virhe (tuntematon tuote,
404) ei korjaannu yrittämällä uudelleen. *Ohimenevä* virhe
(aikakatkaisu, katkennut yhteys, 503) voi korjaantua:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/myynti/SaldoAsiakas.java" osa="saldo"}
```

## Aikaraja

Jokaisella etäkutsulla on oltava aikaraja. Monen HTTP-asiakkaan oletus
on ääretön odotus, ja silloin yksi jumittunut riippuvuus sitoo kutsujan
säikeet yksi kerrallaan, kunnes kutsuja ei enää vastaa kenellekään.
Yhteyden muodostukselle ja vastaukselle annetaan erilliset rajat:
yhteys muodostuu terveeseen palveluun millisekunneissa, mutta vastaus
voi perustellusti kestää kauemmin.

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/myynti/SaldoAsiakasTest.java" osa="aikaraja"}
```

Aikarajan pituus johdetaan käyttäjän odotuksesta, ei riippuvuuden
tavallisesta vasteajasta. Jos sivun pitää vastata sekunnissa ja sen
takana on kolme peräkkäistä kutsua, jokaisella on alle sekunti.
*Määräajan välittäminen* (*deadline propagation*) vie jäljellä olevan
ajan kutsuketjussa eteenpäin: gRPC tekee tämän oletuksena, ja HTTP:ssä
sille käytetään omaa otsaketta.

## Uudelleenyritys

Ohimenevä virhe kannattaa yrittää uudelleen, mutta ei heti eikä
loputtomasti. Jos sata asiakasta yrittää uudelleen samalla hetkellä,
juuri toipumassa oleva palvelu kaatuu uudelleen
(*uudelleenyritysten myrsky*). Siksi odotus kasvaa eksponentiaalisesti
ja on satunnainen:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/kestavyys/Uudelleenyritys.java" osa="uudelleenyritys"}
```

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/myynti/SaldoAsiakasTest.java" osa="uudelleen"}
```

Uudelleenyritys on turvallinen vain idempotentille kutsulle. Saldon
kysely on luku, joten sen voi toistaa. Tilauksen lähettäminen ilman
idempotenssiavainta ei ole. Uudelleenyrityksiä on myös syytä rajata
koko järjestelmän tasolla: jos jokainen ketjun kolmesta kerroksesta
yrittää kolmesti, alin palvelu saa 27 pyyntöä yhden sijaan.
*Uudelleenyritysbudjetti* sallii esimerkiksi enintään 10 %
uudelleenyrityksiä suhteessa onnistuneisiin kutsuihin.

Spring Framework 7 sisältää uudelleenyrityksen valmiina:
`@Retryable`-merkintä ja `RetryTemplate` toteuttavat saman
eksponentiaalisen odotuksen ja satunnaisuuden.

## Katkaisija

Kun riippuvuus on alhaalla, jokainen kutsu odottaa aikarajan verran ja
epäonnistuu. *Katkaisija* (*circuit breaker*) laskee epäonnistumisia ja
"laukeaa", kun niitä on liikaa: sen jälkeen kutsut epäonnistuvat heti,
lähtemättä verkkoon. Hetken kuluttua katkaisija päästää yhden
koekutsun läpi (puoliavoin tila), ja jos se onnistuu, katkaisija
sulkeutuu.

```{.dot otsikko="Katkaisijan tilat. Suljettuna kutsut kulkevat läpi ja virheet lasketaan, avoimena kutsut hylätään heti, ja puoliavoimena koekutsu ratkaisee, kumpaan tilaan palataan."}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=1.0;
  s [label="SULJETTU\nkutsut läpi"]; a [label="AVOIN\nkutsut hylätään heti"];
  p [label="PUOLIAVOIN\nkoekutsu läpi"];
  s -> a [label="virheitä yli rajan"];
  a -> p [label="odotusaika kulunut"];
  p -> s [label="koekutsu onnistuu"];
  p -> a [label="koekutsu epäonnistuu"];
}
```

Resilience4j:n katkaisija määritellään liukuvalla ikkunalla:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/myynti/Katkaisijat.java" osa="katkaisija"}
```

Pysyvä virhe (tuntematon tuote) ei kerro riippuvuuden terveydestä,
joten se jätetään laskematta. Uudelleenyritys on katkaisijan
ulkopuolella, jotta jokainen yritys lasketaan ja avoin katkaisija
lopettaa myös uudelleenyritykset:

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/myynti/SaldoAsiakasTest.java" osa="katkaisija"}
```

Katkaisija hyödyttää molempia osapuolia. Kutsuja vastaa heti eikä
sido säikeitään, ja kaatunut palvelu saa toipua ilman jatkuvaa
pyyntötulvaa.

## Mitä tehdään, kun kutsu epäonnistuu

Virhe ei aina ole oikea vastaus käyttäjälle. Vaihtoehdot ovat:

- **Varavastaus** (*fallback*): välimuistista edellinen saldo, oletus
  "saatavuus tarkistetaan tilauksen jälkeen" tai tyhjä suosituslista.
- **Heikennetty toiminto** (*graceful degradation*): tilauksen voi
  tehdä, mutta toimitusaika-arvio puuttuu.
- **Virhe nopeasti**: jos tieto on välttämätön (maksun hyväksyntä),
  selkeä virhe heti on parempi kuin minuutin odotus.

Valinta on liiketoimintapäätös, ja se tehdään riippuvuuskohtaisesti.

## Laipio ja kuorman pudotus

*Laipio* (*bulkhead*) jakaa resurssit niin, ettei yksi riippuvuus voi
viedä niitä kaikkia: varastokutsuille enintään 20 samanaikaista
pyyntöä, maksukutsuille omat 20. Virtuaalisäikeiden kanssa säikeet eivät
lopu, mutta muut resurssit (yhteysaltaat, muisti, riippuvuuden
kapasiteetti) loppuvat edelleen, joten raja kirjoitetaan
samanaikaisuuden rajana (Resilience4j:n `Bulkhead`, Spring 7:n
`@ConcurrencyLimit`).

*Kuorman pudotus* (*load shedding*) on palvelimen puolen vastine:
ylikuormittunut palvelu vastaa osaan pyynnöistä heti 503 ja
`Retry-After`, jotta loput saavat vastauksen ajoissa. Ilman sitä
jokainen pyyntö hidastuu, kunnes kaikki ylittävät aikarajansa ja työ
menee hukkaan.

## Käytännössä

- **Aikaraja jokaiseen etäkutsuun**, yhteydelle ja vastaukselle
  erikseen, ja ketjussa jäljellä olevan ajan mukaan.
- **Yritä uudelleen vain ohimenevää virhettä ja idempotenttia
  kutsua**, eksponentiaalisella odotuksella, satunnaisuudella ja
  ylärajalla. Rajaa uudelleenyritykset yhteen kerrokseen.
- **Katkaisija jokaiseen riippuvuuteen**, jonka kaatuminen ei saa kaataa
  kutsujaa. Pysyvät virheet eivät laukaise katkaisijaa.
- **Päätä varavastaus etukäteen.** Mitä käyttäjä näkee, kun varasto ei
  vastaa? Kirjaa se ja testaa se.
- **Mittaa ja hälytä.** Katkaisijan tila, uudelleenyritysten määrä ja
  aikakatkaisut ovat palvelun tärkeimpiä mittareita.
- **Hinnat:** uudelleenyritys monistaa kuorman ja lisää viivettä;
  katkaisija hylkää pyyntöjä, jotka olisivat ehkä onnistuneet; jokainen
  suoja on asetus, joka on viritettävä ja testattava.

## Itsearviointi

- Osaat asettaa etäkutsulle aikarajat ja johtaa niiden pituuden
  käyttäjän odotuksesta.
- Osaat toteuttaa uudelleenyrityksen eksponentiaalisella odotuksella ja
  satunnaisuudella ja rajata sen ohimeneviin virheisiin.
- Osaat selittää katkaisijan tilat ja konfiguroida Resilience4j:n
  katkaisijan.
- Osaat valita riippuvuuskohtaisesti varavastauksen, heikennetyn
  toiminnon tai nopean virheen.
- Osaat selittää laipion ja kuorman pudotuksen ja sen, mitä ne
  suojaavat.
