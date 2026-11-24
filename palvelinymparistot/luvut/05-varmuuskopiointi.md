# Varmuuskopiointi

Varmuuskopio on ainoa suoja tilanteissa, joissa data katoaa kaikista
kopioista kerralla: ylläpitäjä poistaa väärän hakemiston, sovellusvika
korruptoi tietokannan, kiristyshaittaohjelma salaa levyt tai konesali
palaa. RAID, replikointi ja tilannevedokset eivät suojaa näiltä, koska
ne kopioivat virheen välittömästi.

## Tavoitteet: RPO ja RTO

Varmuuskopioinnin suunnittelu alkaa palvelun vaatimuksista, ei
työkalusta:

- **RPO** (recovery point objective): kuinka paljon dataa saa
  menettää. Jos RPO on 15 minuuttia, kopioiden väli ei saa olla tätä
  pidempi.
- **RTO** (recovery time objective): kuinka nopeasti palvelun on
  palattava. Palautuksen siirto, purku, tarkistus ja palvelun käynnistys
  on mahduttava aikaan.

```{.python tiedosto="esimerkit/05-rpo-rto.py" osa="arvio"}
```

```{.tuloste tiedosto="esimerkit/05-rpo-rto.odotettu"}
```

Yökopio ei riitä verkkokaupalle, jonka tilauksia ei saa menettää
tuntien edestä, ja suuren arkiston palautus pilvestä kestää päiviä.
Lyhyt RPO saavutetaan yhdistämällä täysi kopio ja jatkuvasti siirrettävä
muutosloki (tietokannan WAL- tai binlog-arkistointi), jolloin
palautuksessa toistetaan loki haluttuun hetkeen asti
(*point-in-time recovery*).

## Säännöt 3-2-1 ja 3-2-1-1-0

Klassinen nyrkkisääntö: **kolme** kopiota datasta, **kahdella** eri
tallennusvälineellä, joista **yksi** toisessa paikassa. Nykyinen
laajennus lisää kaksi ehtoa:

- **1**: yksi kopio on muuttumaton tai irti verkosta, jotta
  kiristyshaittaohjelma ja tunnuksilla varustettu hyökkääjä eivät voi
  poistaa sitä.
- **0**: palautustesteissä nolla virhettä.

Muuttumattomuus toteutetaan esimerkiksi objektitallennuksen
lukitusominaisuudella (S3 Object Lock), varmuuskopiopalvelimella, jonne
tuotantokone voi vain lisätä kopioita (append-only), tai nauhalla
kassakaapissa.

## Kopiotyypit

| Tyyppi | Mitä kopioidaan | Palautus |
|--------|-----------------|----------|
| Täysi | Kaikki | Yksi kopio |
| Inkrementaalinen | Muutokset edellisestä kopiosta | Täysi + kaikki inkrementit |
| Differentiaalinen | Muutokset edellisestä täydestä | Täysi + viimeisin differentiaalinen |
| Synteettinen täysi / deduplikoiva | Muutokset, mutta jokainen kopio näyttää täydeltä | Yksi kopio |

Nykyaikaiset työkalut ovat viimeistä tyyppiä. Klassinen toteutus on
rsync kovilla linkeillä: jokainen kopio on täysi hakemistopuu, mutta
muuttumattomat tiedostot ovat linkkejä edellisen kopion tiedostoihin:

```{.bash tiedosto="esimerkit/05-rsync-kopiot.sh" osa="kopio"}
```

```{.bash tiedosto="esimerkit/05-rsync-kopiot.sh" osa="tarkastelu"}
```

```{.bash tiedosto="esimerkit/05-rsync-kopiot.sh" osa="palautus"}
```

```{.tuloste tiedosto="esimerkit/05-rsync-kopiot.odotettu"}
```

Tietokannan dumppi on kolmessa kopiossa yhtenä tiedostona (linkkejä
on kolme), ja toinen ja kolmas kopio vievät vain muuttuneiden
tiedostojen tilan. Poistettu raportti palautetaan edellisestä kopiosta.

rsync päättelee muuttuneet tiedostot koon ja muokkausajan perusteella.
Jos ohjelma muuttaa tiedostoa niin, että koko pysyy samana ja
muokkausaika ei muutu (tai muuttuu saman sekunnin aikana), muutos jää
kopioimatta. Valitsin `--checksum` vertaa sisältöä, mutta lukee kaiken
datan joka kerta.

## Deduplikoiva kopio: restic

restic jakaa tiedostot sisällön perusteella lohkoiksi, salaa ne ja
tallentaa kunkin lohkon vain kerran. Kopiovarasto voi olla paikallinen
hakemisto, SFTP-palvelin tai objektitallennus:

```{.bash tiedosto="esimerkit/05-restic.sh" osa="alustus"}
```

```{.bash tiedosto="esimerkit/05-restic.sh" osa="kopiot"}
```

```{.bash tiedosto="esimerkit/05-restic.sh" osa="palautus"}
```

```{.bash tiedosto="esimerkit/05-restic.sh" osa="sailytys"}
```

```{.tuloste tiedosto="esimerkit/05-restic.odotettu"}
```

Esimerkissä salasana on ympäristömuuttujassa yksinkertaisuuden vuoksi.
Tuotannossa se luetaan tiedostosta tai salaisuusvarastosta
(`RESTIC_PASSWORD_FILE`), ja se säilytetään myös varmuuskopioiden
ulkopuolella: salattu kopio ilman avainta on hyödytön.

## Säilytys

Kopioita ei säilytetä ikuisesti, mutta pelkkä "viimeiset 30" ei riitä,
jos korruptoituminen huomataan vasta kuukausien päästä. Yleinen
ratkaisu on porrastettu säilytys (isoisä–isä–poika, GFS):

```{.python tiedosto="esimerkit/05-rotaatio.py" osa="gfs"}
```

```{.tuloste tiedosto="esimerkit/05-rotaatio.odotettu"}
```

Neljän vuoden päivittäisistä kopioista säilyy 21: viikon jokainen
päivä, kuukauden viikot, vuoden kuukaudet ja kolmen vuoden vuodet.
Säilytysaikoja rajoittaa myös lainsäädäntö: henkilötietoja ei saa
säilyttää varmuuskopioissakaan pidempään kuin käyttötarkoitus vaatii,
ja kirjanpitoaineistolle on vähimmäisajat.

## Palautustestaus

Palautusta ei saa kokeilla ensimmäistä kertaa silloin, kun sitä
tarvitaan. Säännöllinen palautustesti:

1. Palauttaa satunnaisen kopion erilliseen ympäristöön.
2. Tarkistaa eheyden (`restic check`, tietokannan omat tarkistukset).
3. Käynnistää palvelun palautetulla datalla ja ajaa savutestin.
4. Mittaa keston ja vertaa sitä RTO:hon.
5. Kirjaa tuloksen ja hälyttää epäonnistumisesta.

Kokonaisen palvelun palautusharjoitus (disaster recovery) tehdään
harvemmin, esimerkiksi kerran vuodessa, ja se paljastaa asiat, joita
kopio ei sisällä: salasanat, DNS-tietueet, lisenssiavaimet ja
dokumentaation.

## Käytännössä

- **Aloita RPO:sta ja RTO:sta**, ja valitse tekniikka niiden mukaan.
- **3-2-1-1-0.** Yksi kopio muuttumattomana tai irti verkosta;
  tuotantokoneen tunnuksilla ei voi poistaa kopioita.
- **Kopioi johdonmukainen tila.** Tietokannasta kopioidaan dumppi tai
  tilannevedos, ei käynnissä olevan tietokannan tiedostoja.
- **Salaa ja säilytä avaimet erikseen.**
- **Testaa palautus automaattisesti** ja seuraa sen kestoa.
- **Valvo kopioiden ikää.** Hälytys, jos uusin onnistunut kopio on
  vanhempi kuin RPO.

## Itsearviointi

- Osaat johtaa varmuuskopioinnin vaatimukset RPO:sta ja RTO:sta ja
  arvioida, täyttääkö ratkaisu ne.
- Osaat selittää säännön 3-2-1-1-0 ja keinot muuttumattomaan kopioon.
- Osaat tehdä inkrementaaliset kopiot rsyncillä tai resticillä ja
  palauttaa niistä.
- Osaat määritellä porrastetun säilytyksen ja palautustestauksen.
