# Istunnot ja evästeet

Kirjautumisen jälkeen palvelin tunnistaa käyttäjän istunnosta.
Istuntotunniste on yhtä arvokas kuin salasana: sen haltija on
käyttäjä niin kauan kuin istunto on voimassa. Tämä luku käy läpi
tunnisteen luonnin, säilytyksen evästeessä, vanhenemisen,
kiinnityshyökkäyksen ja uloskirjautumisen.

## Tunniste ja varasto

Tunnisteen on oltava **arvaamaton**: vähintään 128 bittiä
kryptografisesta satunnaislähteestä (`crypto.randomBytes`, ei
`Math.random`). Esimerkin tunnisteessa on 256 bittiä. Varasto pitää
kaksi aikarajaa: **joutoaika** (istunto päättyy, jos sitä ei käytetä)
ja **enimmäisaika** (istunto päättyy joka tapauksessa).

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.ts" osa="varasto"}
```

Palvelimen istuntovarasto (muisti, Redis, tietokanta) on yleensä
parempi kuin allekirjoitettu tila evästeessä tai JWT:ssä, koska
istunnon voi mitätöidä heti: uloskirjautuminen, salasanan vaihto ja
ylläpitäjän "kirjaa ulos kaikkialta" toimivat. Tilaton token on
voimassa vanhenemiseensa asti (luku 9).

## Evästeen attribuutit

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.ts" osa="eväste"}
```

| Attribuutti | Vaikutus |
|-------------|----------|
| `Secure` | vain HTTPS-yhteydellä; salakuuntelija ei näe |
| `HttpOnly` | skripti ei voi lukea (`document.cookie`); XSS ei vie tunnistetta |
| `SameSite=Lax` | ei kulje toisen sivuston aloittamissa pyynnöissä (luku 4) |
| `Path=/` | koko sivustolle |
| ei `Domain`-attribuuttia | vain tälle isännälle, ei aliverkkotunnuksille |
| `__Host-`-etuliite | selain hyväksyy evästeen vain, jos `Secure`, `Path=/` ja ei `Domain`: aliverkkotunnus ei voi asettaa eikä korvata sitä |
| ei `Max-Age`/`Expires` | istuntoeväste: poistuu, kun selain suljetaan |

`__Host-`-etuliite torjuu *evästeen injektion*: jos hyökkääjä hallitsee
aliverkkotunnusta (esimerkiksi käyttäjien omat sivut), hän voisi
muuten asettaa koko verkkotunnukselle evästeen, jonka nimi on sama
kuin istuntoevästeen.

## Istunnon kiinnitys

Kiinnityshyökkäyksessä (*session fixation*) hyökkääjä hankkii
anonyymin istuntotunnisteen ja saa uhrin käyttämään sitä: linkillä,
jossa tunniste on osoitteessa, tai evästeen injektiolla. Kun uhri
kirjautuu, haavoittuva palvelu liittää käyttäjän samaan
tunnisteeseen, jonka hyökkääjä jo tuntee:

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.ts" osa="kirjaudu"}
```

Torjunta on **kiertää tunniste**: kirjautuminen ja oikeuksien muutos
(esimerkiksi ylläpitotilaan siirtyminen tai monivaiheisen tunnistuksen
läpäisy) luovat aina uuden tunnisteen ja poistavat vanhan. Lisäksi
tunnistetta ei koskaan hyväksytä osoitteesta.

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.test.ts" osa="kiinnitys"}
```

## Vanheneminen ja uloskirjautuminen

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.test.ts" osa="vanheneminen"}
```

Uloskirjautuminen poistaa istunnon **palvelimelta**. Pelkkä evästeen
poisto selaimesta ei riitä: jos tunniste on vuotanut (jaettu kone,
välityspalvelimen loki), se toimisi edelleen.

## Käytännössä

- **Satunnainen, pitkä, palvelimella säilytetty tunniste** on
  yksinkertaisin turvallinen istunto. Kehysten istuntomoduulit
  (express-session, Spring Session) tekevät tämän; tarkista silti
  evästeen attribuutit.
- **Kierrä tunniste** kirjautuessa ja aina, kun oikeudet nousevat.
- **Aikarajat riskin mukaan.** Verkkopankki: joutoaika minuutteja,
  enimmäisaika tunteja. Uutissivuston "muista minut": viikkoja,
  mutta arkaluontoiset toiminnot (salasanan tai sähköpostin vaihto,
  maksut) vaativat uudelleentunnistuksen.
- **Mitätöi istunnot**, kun salasana vaihdetaan tai tili
  palautetaan, ja näytä käyttäjälle aktiiviset istunnot.
- **Hinta:** palvelimen istuntovarasto on yksi tietokantahaku per
  pyyntö. Se on lähes aina pienempi kuin JWT:n kumoamisen
  monimutkaisuus.

## Itsearviointi

- Osaat luoda riittävän satunnaisen istuntotunnisteen ja selittää,
  miksi `Math.random` ei kelpaa.
- Osaat valita istuntoevästeen attribuutit ja kertoa, mitä
  `__Host-`-etuliite takaa.
- Osaat selittää istunnon kiinnityksen ja torjua sen kiertämällä
  tunnisteen.
- Osaat toteuttaa jouto- ja enimmäisajan sekä uloskirjautumisen, joka
  mitätöi istunnon palvelimella.
