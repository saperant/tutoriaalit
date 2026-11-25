# Istunnot ja evästeet

Kirjautumisen jälkeen palvelin tunnistaa käyttäjän istunnosta.
Istuntotunniste on yhtä arvokas kuin salasana: sen haltija on
käyttäjä niin kauan kuin istunto on voimassa. *Tietoturvan perusteet*
esitteli istunnon ja sen kiinnityksen periaatteen. Tämä luku
toteuttaa ne palvelimella: tunnisteen luonti, säilytys evästeessä
selaimen suojausmääritteineen, vanheneminen, kierto kirjautuessa ja
uloskirjautuminen.

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

```{.dot otsikko="Istunnon kiinnitys. Hyökkääjä ei varasta tunnistetta vaan antaa sen: kun palvelu liittää kirjautuneen käyttäjän vanhaan tunnisteeseen (5), hyökkääjän hallussa oleva X on kirjautunut istunto."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  u0 [label="uhri", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  uL [pos="0.00,-2.92!"];
  u0 -> uL [arrowhead=none, style=dotted];
  h0 [label="hyökkääjä", shape=box, style="rounded,filled", width=0, height=0.3, pos="2.35,0!"];
  hL [pos="2.35,-2.92!"];
  h0 -> hL [arrowhead=none, style=dotted];
  p0 [label="palvelu", shape=box, style="rounded,filled", width=0, height=0.3, pos="4.70,0!"];
  pL [pos="4.70,-2.92!"];
  p0 -> pL [arrowhead=none, style=dotted];
  h1 [pos="2.35,-0.51!"]; p1_ [pos="4.70,-0.51!"];
  h1 -> p1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. GET /uusi", pos="3.53,-0.41!"];
  p2 [pos="4.70,-0.87!"]; h2_ [pos="2.35,-0.87!"];
  p2 -> h2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. anonyymi tunniste X", pos="3.53,-0.77!"];
  h3 [pos="2.35,-1.23!"]; u3_ [pos="0.00,-1.23!"];
  h3 -> u3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. linkki /kirjaudu?sid=X", pos="1.18,-1.13!"];
  u4 [pos="0.00,-1.59!"]; p4_ [pos="4.70,-1.59!"];
  u4 -> p4_ [];
  t4 [shape=plain, style="", fontsize=9, label="4. POST /kirjaudu?sid=X (tunnus, salasana)", pos="1.18,-1.49!"];
  p5 [pos="4.70,-1.95!"]; u5_ [pos="0.00,-1.95!"];
  p5 -> u5_ [];
  t5 [shape=plain, style="", fontsize=9, label="5. istunto X kuuluu nyt uhrille", pos="3.53,-1.85!"];
  h6 [pos="2.35,-2.31!"]; p6_ [pos="4.70,-2.31!"];
  h6 -> p6_ [];
  t6 [shape=plain, style="", fontsize=9, label="6. GET /?sid=X", pos="3.53,-2.21!"];
  p7 [pos="4.70,-2.67!"]; h7_ [pos="2.35,-2.67!"];
  p7 -> h7_ [];
  t7 [shape=plain, style="", fontsize=9, label="7. 200: uhrin tiedot", pos="3.53,-2.57!"];
}
```

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.ts" osa="kirjaudu"}
```

Torjunta on **kiertää tunniste**: kirjautuminen ja oikeuksien muutos
(esimerkiksi ylläpitotilaan siirtyminen tai monivaiheisen tunnistuksen
läpäisy) luovat aina uuden tunnisteen ja poistavat vanhan. Lisäksi
tunnistetta ei koskaan hyväksytä osoitteesta.

```{.typescript tiedosto="esimerkit/src/05-istunnot/istunnot.test.ts" osa="kiinnitys"}
```

Näytösajo käy saman kulun läpi ja kokeilee lopuksi, kelpaako eväste
vielä uloskirjautumisen jälkeen (seuraava osio):

```{.tuloste tiedosto="esimerkit/naytos/05-istunnot.odotettu"}
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
