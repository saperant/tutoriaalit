# Yhdyskäytävä, palveluverkko ja sopimukset

Kun palveluja on monta, kaksi kysymystä tulee vastaan. Miten asiakkaat
löytävät palvelut, ja kuka hoitaa yhteiset asiat, kuten todennuksen ja
pyyntörajoituksen? Ja miten tiimi voi muuttaa palvelunsa rajapintaa
tietäen, ettei se riko muiden palveluja? Ensimmäiseen vastaavat
yhdyskäytävä ja palveluverkko, toiseen sopimustestit.

## API-yhdyskäytävä

*API-yhdyskäytävä* (*API gateway*) on järjestelmän ainoa sisäänkäynti
ulkoisille asiakkaille. Se reitittää pyynnön oikealle palvelulle ja
hoitaa samalla asiat, jotka muuten toistuisivat jokaisessa palvelussa.
Esimerkin yhdyskäytävä tekee viisi asiaa:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/yhdyskaytava/Yhdyskaytava.java" osa="kasittele"}
```

1. **Todennus**: pyyntö ilman kelvollista avainta hylätään ennen kuin
   se kuormittaa yhtään palvelua.
2. **Pyyntörajoitus** asiakaskohtaisesti.
3. **Reititys** polun pisimmän osuvan alun mukaan.
4. **Korrelaatiotunnus**: jos asiakas ei lähettänyt tunnusta,
   yhdyskäytävä luo sen, ja se kulkee jokaiseen palveluun ja takaisin.
5. **Aikaraja ja virheiden muunto**: hidas palvelu on 504, kaatunut
   palvelu 502.

Pyyntörajoitin on *merkkiämpäri*, joka sallii lyhyet purskeet mutta
rajoittaa keskimääräisen tahdin:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/yhdyskaytava/Rajoitin.java" osa="rajoitin"}
```

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/yhdyskaytava/YhdyskaytavaTest.java" osa="kaynnistys"}
```

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/yhdyskaytava/YhdyskaytavaTest.java" osa="testit"}
```

Tuotannossa yhdyskäytävä on valmis tuote: Kong, Envoy Gateway, NGINX,
Spring Cloud Gateway tai pilvipalvelun hallittu yhdyskäytävä.
Kubernetesissa reititys kuvataan Gateway API -resursseilla. Rajoittimen
tila on silloin jaettu yhdyskäytävän kopioiden kesken (esimerkiksi
Redisissä), muuten kolme kopiota sallii kolminkertaisen tahdin.

Yhdyskäytävään ei kuulu liiketoimintalogiikkaa. Kun yhdyskäytävä alkaa
yhdistellä vastauksia ja päättää hinnoista, se on palannut SOA:n
älykkääksi väyläksi.

## Taustapalvelu käyttöliittymälle

Mobiilisovellus, selainsovellus ja kumppanien rajapinta tarvitsevat
eri tietoja eri muodoissa. Yksi yleiskäyttöinen rajapinta palvelee
niitä kaikkia huonosti. *Backend for frontend* (BFF) on
käyttöliittymäkohtainen ohut palvelu, joka kokoaa juuri sen näkymien
tarvitseman tiedon muista palveluista. BFF:n omistaa käyttöliittymää
tekevä tiimi, joten se voi muuttaa sitä käyttöliittymän tahdissa.
GraphQL-palvelin on BFF:n yleinen toteutustapa.

## Palveluverkko

Yhdyskäytävä hoitaa liikenteen, joka tulee järjestelmään ulkoa
(*pohjois–etelä*). Palvelujen välinen liikenne (*itä–länsi*) tarvitsee
samoja asioita: salauksen ja palvelujen tunnistuksen (mTLS),
aikarajat, uudelleenyritykset, katkaisijat ja mittarit.
*Palveluverkko* (*service mesh*, esim. Istio tai Linkerd) siirtää ne
pois sovelluskoodista: jokaisen palvelun viereen ajetaan välityspalvelin
(*sivuvaunu*, *sidecar*) tai jokaiselle solmulle yhteinen välittäjä,
joka käsittelee kaiken liikenteen. Asetukset kirjoitetaan keskitetysti.

| | Kirjasto (Resilience4j) | Palveluverkko |
|---|---|---|
| Kielet | yksi kieli kerrallaan | kaikki samalla tavalla |
| Hienojakoisuus | metodi, liiketoimintatieto | pyyntö, HTTP-tason tieto |
| Varavastaus | mahdollinen | ei (ei tunne sovellusta) |
| Operointi | ei mitään uutta | uusi infrastruktuurikerros |

Palveluverkko on perusteltu, kun palveluja on paljon ja ne on kirjoitettu
usealla kielellä. Muuten kirjasto riittää, ja sitä on helpompi testata.

## Sopimustestaus

Kun myynti kutsuu varastoa, kumpikin tiimi testaa oman koodinsa, mutta
kumpikaan testi ei huomaa, jos varasto muuttaa vastauksen muotoa
tavalla, joka rikkoo myynnin. Kaikkien palvelujen yhteiset
päästä-päähän-testit huomaisivat, mutta ne ovat hitaita, hauraita ja
pakottavat palvelut julkaistavaksi yhdessä: hajautetun monoliitin
oire.

*Kuluttajavetoinen sopimus* (*consumer-driven contract*) ratkaisee tämän
kahdella nopealla testillä. Kuluttaja kirjaa sopimukseen pyynnöt, joita
se tekee, ja vastausten osat, joista se riippuu:

```{.json tiedosto="esimerkit/etakutsut/src/test/resources/sopimukset/myynti-varasto.json"}
```

Kuluttajan testi ajaa myynnin oikean asiakaskoodin sopimuksesta
tehtyä valepalvelua vastaan:

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/sopimus/SopimusTest.java" osa="kuluttaja"}
```

Tuottajan testi ajaa samat pyynnöt oikeaa varastopalvelua vastaan.
Ennen jokaista pyyntöä tuottaja asettaa sopimuksen nimeämän *tilan*
("kahvinkeittimiä on kolme"):

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/sopimus/SopimusTarkistin.java" osa="tarkista"}
```

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/sopimus/SopimusTest.java" osa="tuottaja"}
```

Tarkistin vertaa vain kenttiä, joita kuluttaja käyttää, ja niiden
tyyppejä, ei arvoja. Varasto saa lisätä kenttiä vapaasti, mutta kentän
`saldo` uudelleennimeäminen kaataa varaston oman käännöksen ennen kuin
myynti hajoaa tuotannossa.

Tuotannossa sopimukset jaetaan *sopimusvälittäjän* (*contract broker*)
kautta: kuluttajan putki julkaisee sopimuksen, tuottajan putki
tarkistaa kaikki voimassa olevat sopimukset, ja julkaisun portti
(Pactin `can-i-deploy`) kertoo, voiko version julkaista. Pact on
monikielinen standardityökalu, ja Spring Cloud Contract tekee saman
Spring-ekosysteemissä.

## Käytännössä

- **Yhdyskäytävä hoitaa poikkileikkaavat asiat**: todennuksen,
  rajoituksen, korrelaatiotunnuksen ja aikarajat. Liiketoimintalogiikka
  kuuluu palveluihin.
- **BFF jokaiselle selvästi erilaiselle käyttöliittymälle**, ja sen
  omistaa käyttöliittymän tiimi.
- **Palveluverkko vasta tarpeeseen.** Kirjasto riittää, kun palveluja
  on vähän ja ne on kirjoitettu samalla kielellä.
- **Sopimustestit päästä-päähän-testien tilalle palvelujen välillä.**
  Kuluttaja kirjaa vain sen, mitä se käyttää, ja tuottaja tarkistaa
  kaikki kuluttajansa jokaisessa käännöksessä.
- **Hinnat:** yhdyskäytävä on kriittinen ja kuormitettu komponentti,
  jonka on oltava replikoitu; palveluverkko lisää viivettä ja
  operointia; sopimukset ovat ylläpidettävää koodia.

## Itsearviointi

- Osaat luetella API-yhdyskäytävän tehtävät ja perustella, miksi
  liiketoimintalogiikka ei kuulu sinne.
- Osaat toteuttaa merkkiämpäriin perustuvan pyyntörajoittimen ja
  selittää sen käytöksen purskeissa.
- Osaat selittää BFF-mallin ja palveluverkon ja verrata
  palveluverkkoa sovelluskirjastoon.
- Osaat kirjoittaa kuluttajavetoisen sopimuksen ja sen kuluttaja- ja
  tuottajatestit.
