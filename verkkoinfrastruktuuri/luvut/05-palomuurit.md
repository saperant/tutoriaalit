# Palomuurit ja osoitteenmuunnos

Palomuuri päättää, mikä liikenne saa kulkea segmenttien välillä ja
mikä saa tulla laitteeseen. Hyvä palomuuri on suunnitelman toteutus:
sallittujen virtojen luettelo kirjoitetaan sääntöinä, ja kaikki muu
estetään. Tässä luvussa rakennetaan vyöhykepalomuuri reitittimeen,
osoitteenmuunnokset (NAT) ja palvelimen oma palomuuri nftablesilla, joka
on Linuxin nykyinen pakettisuodatin (iptablesin seuraaja).

## Tilallinen suodatus

Varhaiset palomuurit tarkastelivat jokaista pakettia erikseen, jolloin
vastauspaketeille piti avata oma sääntönsä. Tilallinen palomuuri seuraa
yhteyksiä (*connection tracking*, conntrack): kun ensimmäinen paketti on
hyväksytty, yhteyden loput paketit ja siihen liittyvät virheilmoitukset
tunnistetaan tilasta `established` tai `related`. Säännöt kirjoitetaan
siis vain yhteyden avaavalle suunnalle.

nftablesin rakenne on taulu → ketju → säännöt. Ketju kiinnitetään
koukkuun (*hook*): `input` (laitteelle tulevat), `forward` (laitteen
läpi kulkevat), `output` (laitteelta lähtevät), `prerouting` ja
`postrouting` (ennen ja jälkeen reitityspäätöksen; NAT). Ketjun
oletuspolitiikka (`policy drop`) ratkaisee paketit, joihin mikään sääntö
ei osu.

## Vyöhykepalomuuri

Reitittimellä on kolme vyöhykettä: lähiverkko (`lan`), palvelinverkko
(`dmz`) ja internet (`wan`). Sallitut virrat ovat:

| Mistä | Mihin | Mitä |
|-------|-------|------|
| lan | wan | kaikki (osoitteenmuunnoksella) |
| lan | dmz | kaikki |
| wan | dmz | vain julkaistu verkkopalvelin, portti 80 |
| dmz | lan | ei mitään |

Säännöt seuraavat taulukkoa:

```{.bash tiedosto="esimerkit/05-palomuuri.sh" osa="saannot"}
```

Huomioita säännöistä:

- `ct state established,related accept` on ensimmäinen sääntö: valtaosa
  paketeista kuuluu jo hyväksyttyihin yhteyksiin, ja ne käsitellään
  yhdellä tarkistuksella.
- `ct state invalid drop` pudottaa paketit, jotka eivät kuulu mihinkään
  järkevään yhteyteen, kuten irralliset TCP-kuittaukset.
- Internetistä DMZ:aan sallitaan vain paketit, joiden kohde on muunnettu
  porttiohjauksella (`ct status dnat`). Hyökkääjä ei pääse DMZ:aan
  osoittamalla sen yksityistä osoitetta suoraan.
- Viimeinen sääntö laskee estetyt paketit. Laskurit ja tarvittaessa
  lokitus (`log prefix "esto: " limit rate 5/second`) ovat vianetsinnän
  perusta.

```{.bash tiedosto="esimerkit/05-palomuuri.sh" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/05-palomuuri.odotettu"}
```

Tulosteesta näkee molemmat osoitteenmuunnokset: internetin palvelin näkee
työaseman yhteyden tulevan palomuurin julkisesta osoitteesta
(`203.0.113.1`), ja DMZ:n verkkopalvelin näkee internetistä tulevan
asiakkaan oikean osoitteen.

## Osoitteenmuunnos

- **SNAT ja naamiointi** (*masquerade*) korvaavat lähtevän liikenteen
  lähdeosoitteen palomuurin osoitteella. Näin yksityiset osoitteet
  pääsevät internetiin yhden julkisen osoitteen takaa. `masquerade`
  käyttää lähtöliitännän kulloistakin osoitetta ja sopii dynaamiselle
  yhteydelle; kiinteällä osoitteella `snat to` on kevyempi.
- **DNAT** eli porttiohjaus muuttaa saapuvan liikenteen kohdeosoitteen,
  jolloin sisäverkon palvelu julkaistaan palomuurin osoitteessa.

NAT ei ole palomuuri. Se piilottaa sisäverkon osoitteet sivuvaikutuksena,
mutta varsinainen suojaus on `forward`-ketjun oletuksena estävä
politiikka. IPv6:ssa NATia ei tarvita, koska osoitteita riittää,
joten tilallisen palomuurin säännöt ovat siellä ainoa suoja.

## Palvelimen oma palomuuri

Verkkopalomuuri suojaa segmenttien rajoja, mutta saman segmentin
laitteet näkevät toisensa. Siksi jokaisella palvelimella on myös oma
`input`-ketjunsa. Esimerkissä SSH on auki vain ylläpitokoneille, ja
muiden uusien SSH-yhteyksien määrä on rajoitettu lähdeosoitteittain:

```{.bash tiedosto="esimerkit/05-rajoitus.sh" osa="saannot"}
```

`yllapitokoneet` on nimetty joukko (*set*). Sen jäseniä voi lisätä ja
poistaa ilman, että sääntöihin kosketaan, ja haku on nopea suurellakin
joukolla. `ssh_yritykset` on dynaaminen joukko, johon jokaiselle
lähdeosoitteelle syntyy oma rajoittimensa:

```{.bash tiedosto="esimerkit/05-rajoitus.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/05-rajoitus.odotettu"}
```

Hyökkääjä sai kolme yhteyttä, sitten loput pudotettiin. Ylläpitokone
ei ole rajoituksen piirissä. Kun hyökkääjän osoite lisätään joukkoon, se
pääsee taas läpi: joukon muutos tuli voimaan heti.

## Sääntöjen ylläpito

Palomuurin säännöt ovat koodia, ja niitä hallitaan kuin koodia:

- Säännöstö on tiedostossa versionhallinnassa ja ladataan
  kokonaisuutena `nft -f`:llä. Lataus on atominen: joko koko uusi
  säännöstö tulee voimaan tai ei mitään.
- Jokaisella säännöllä on kommentti tai muutospyynnön tunniste, josta
  näkee, miksi se on olemassa ja kuka sen tarvitsee.
- Säännöt tarkistetaan säännöllisesti. Laskuri, joka ei ole kasvanut
  vuoteen, kertoo säännöstä, jota ei enää tarvita.
- Muutos testataan ennen käyttöönottoa: `nft -c -f säännöt.nft`
  tarkistaa syntaksin, ja hyväksymistestit kuten yllä varmistavat, että
  sallitut virrat toimivat ja muut on estetty.
- Etämuutoksissa käytetään ajastettua palautusta: jos uusi säännöstö
  katkaisee oman yhteyden, vanha palautetaan automaattisesti
  muutaman minuutin kuluttua.

## Käytännössä

- **Oletuksena esto.** Jokainen ketju päättyy `policy drop` -politiikkaan,
  ja sallitut virrat luetellaan. Sallivaa palomuuria, josta estetään
  tunnetut huonot asiat, ei voi koskaan todeta valmiiksi.
- **Vähimmät oikeudet virroille.** Sääntö sallii tietyn lähteen, kohteen
  ja palvelun, ei kokonaisia verkkoja kaikille porteille.
- **Kaksi kerrosta.** Verkon palomuuri vyöhykkeiden välillä ja
  isäntäkohtainen palomuuri jokaisella palvelimella. Kumpikaan ei yksin
  riitä.
- **Tila ensin.** `established,related` ensimmäisenä, `invalid` pudotetaan.
- **Joukot sääntöjen sijaan.** Osoitelistat nimettyinä joukkoina; säännöt
  pysyvät lyhyinä ja luettavina.
- **Ulospäin suodatus.** Myös lähtevää liikennettä rajataan: palvelin,
  joka ei tarvitse internetiä, ei pääse sinne. Se katkaisee haittaohjelman
  yhteyden ohjauspalvelimeensa.

## Itsearviointi

- Osaat selittää tilallisen suodatuksen ja nftablesin taulut, ketjut ja
  koukut.
- Osaat kirjoittaa vyöhykepalomuurin oletuksena estävällä politiikalla
  sallittujen virtojen taulukosta.
- Osaat toteuttaa SNAT:n ja porttiohjauksen ja selittää, miksi NAT ei ole
  palomuuri.
- Osaat suojata palvelimen omalla palomuurilla, nimetyillä joukoilla ja
  lähdekohtaisella rajoituksella sekä ylläpitää säännöstöä koodina.
