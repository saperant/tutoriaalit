# Varmenteiden kierto ja kumoaminen

Lyhytikäiset varmenteet vaihtuvat jatkuvasti, ja varmentajakin
vaihdetaan aikanaan: avainpituus vanhenee, juuriavain epäillään
vuotaneeksi tai organisaatio muuttuu. Kierron pitää onnistua ilman,
että palvelut pysähtyvät.

## Vaihto lennossa

Palvelun TLS-kontekstin avainhallinta ja luottamushallinta voidaan
kääriä niin, että ne kysyvät joka kättelyssä kulloisetkin arvot.
Uudet yhteydet käyttävät heti uutta varmennetta, eikä palvelua
käynnistetä uudelleen:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/VaihdettavaTls.java" osa="vaihto"}
```

Spring Bootissa sama saadaan SSL-nipun asetuksella `reload-on-update`
(luku 11), ja SPIFFE-kirjastot tekevät sen automaattisesti, kun
työkuorman API antaa uuden SVID:n.

## Varmentajan kierto kolmessa vaiheessa

Varmentajan kierto on vaarallisempi kuin varmenteen, koska luottamus
muuttuu koko kokonaisuudessa. Turvallinen järjestys:

1. **Uusi juuri lisätään kaikkien luottamusnippuun.** Kukaan ei vielä
   käytä uuden juuren varmenteita.
2. **Palvelut saavat uuden juuren myöntämät varmenteet.** Koska kaikki
   luottavat jo molempiin, kumpikin varmenne kelpaa.
3. **Vanha juuri poistetaan nipusta**, kun yksikään sen myöntämä
   varmenne ei ole enää voimassa.

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/KiertoTest.java" osa="kierto"}
```

Näytösajo kutsuu tilauspalvelua jokaisessa vaiheessa kahdella
laskutuksen varmenteella, vanhan ja uuden varmentajan myöntämällä.
Sarake *nippu* kertoo, mihin juuriin kaikki sillä hetkellä luottavat,
ja *palvelin*, kumman varmentajan varmennetta tilauspalvelu esittää:

```{.tuloste tiedosto="esimerkit/naytos/05-kierto.odotettu"}
```

Vaiheissa 1 ja 2 molemmat varmenteet kelpaavat, joten palvelut voi
päivittää yksi kerrallaan missä järjestyksessä tahansa. Viimeinen rivi
on virhetilanne, jossa vaihe 1 on ohitettu.

Jos vaihe 1 jää tekemättä, ensimmäinen uuden varmenteen saanut
palvelu katkaisee yhteydet kaikkiin, jotka eivät vielä tunne uutta
juurta. Testi `liianAikainenPoistoKatkaiseeYhteydet` osoittaa tämän.
Vaiheiden välissä odotetaan vähintään yksi varmenteen elinikä ja
välimuistien päivitysväli.

## Kumoaminen

PKI:n perinteiset kumoamiskeinot ovat kumoamislista (CRL) ja OCSP.
Molemmissa vastaanottaja kysyy varmentajalta, onko varmenne kumottu.
Käytännössä niissä on ongelmia: listat kasvavat, kysely hidastaa
kättelyä ja vastaanottaja joutuu päättämään, mitä tehdä, jos
varmentaja ei vastaa. Useimmat toteutukset sallivat silloin yhteyden,
jolloin kumoaminen ei toimi juuri kun sitä tarvittaisiin.

Työkuormien varmenteissa kumoaminen korvataan lyhyellä eliniällä:

- **Murrettu palvelu:** estetään sen uudet varmenteet (SPIREssä
  työkuorman rekisteröinti poistetaan), jolloin vanha vanhenee
  tunnissa. Välitön eristys tehdään valtuutuksessa (luku 13).
- **Vuotanut välivarmentaja:** se poistetaan luottamusnipusta, ja
  palvelut saavat uudet varmenteet toiselta välivarmentajalta.
- **Vuotanut juuri:** koko luottamusalueen kierto. Siksi juuren
  avain on laitteistossa ja varmenteita myöntävät välivarmentajat.

## Käytännössä

- **Automatisoi kaikki uusiminen.** Käsin uusitut varmenteet
  vanhenevat aina jossain kohtaa yllättäen, ja katko on tavallisin
  varmenteisiin liittyvä häiriö.
- **Valvo jäljellä olevaa elinikää.** Hälytys, kun palvelun varmenne
  on vanhenemassa eikä uutta ole tullut, löytää pysähtyneen
  automaation ennen katkoa.
- **Harjoittele varmentajan kiertoa.** Kierto, jota ei ole koskaan
  tehty, epäonnistuu silloin kun sitä tarvitaan. Tee se säännöllisesti
  testiympäristössä.
- **Pidä luottamusnippu pienenä.** Jokainen nipun juuri voi myöntää
  minkä tahansa identiteetin.

## Itsearviointi

- Osaat vaihtaa palvelun varmenteen ja luottamusnipun ilman
  uudelleenkäynnistystä.
- Osaat kiertää varmentajan kolmessa vaiheessa ja kertoa, mitä
  tapahtuu, jos vaihe jää välistä.
- Osaat perustella, miksi lyhyt elinikä korvaa työkuormilla
  kumoamislistat ja OCSP:n.
- Osaat kuvata toimenpiteet, kun varmenne, välivarmentaja tai juuri
  vuotaa.
