# Segmentointi ja yhdyskäytävä

Nollaluottamus ei poista tarvetta rajata, mihin kukin pääsee
verkossa. Se poistaa vain oletuksen, että rajan sisäpuolella oleva
on luotettava. Verkon segmentointi ja yhdyskäytävä ovat
syvyyssuuntaista puolustusta: ne pysäyttävät suuren osan hyökkäyksistä
halvalla, mutta palvelut eivät saa nojata pelkästään niihin.

## Yhdyskäytävä reunalla

API-yhdyskäytävä on järjestelmän ainoa julkinen sisäänkäynti (ks.
*Palveluarkkitehtuurit*). Tietoturvan kannalta sen tehtävä on karsia
ennen kuin pyyntö kuormittaa palveluja:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/reuna/Yhdyskaytava.java" osa="kasittele"}
```

1. **Sisäiset otsakkeet poistetaan.** Jos yhdyskäytävä välittää
   käyttäjän identiteetin otsakkeessa, ulkopuolinen ei saa asettaa
   samaa otsaketta itse.
2. **Todennus.** Token tarkistetaan reunalla, jotta todentamaton
   liikenne ei pääse sisään lainkaan.
3. **Nopeusrajoitus identiteettiä kohti.** IP-osoitteen mukainen
   rajoitus ei pysäytä hajautettua hyökkäystä eikä erottele
   käyttäjiä saman NAT-osoitteen takana.
4. **Skeemavalidointi.** Tuntemattomat kentät, väärät tyypit ja
   arvoalueen ylitykset hylätään ennen kuin ne päätyvät palveluun.
   Tuntematon kenttä `hinta` olisi tyypillinen massamäärityksen
   yritys.

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/reuna/YhdyskaytavaTest.java" osa="otsakkeet"}
```

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/reuna/YhdyskaytavaTest.java" osa="hylkaykset"}
```

Näytösajossa yhdyskäytävä saa viisi pyyntöä:

```{.tuloste tiedosto="esimerkit/naytos/10-reuna.odotettu" asti="429"}
```

## Todennus reunalla vai jokaisessa palvelussa

Yleinen virhe on olettaa, että koska yhdyskäytävä todentaa, palvelun
ei tarvitse. Palvelu luottaa yhdyskäytävän asettamaan otsakkeeseen
kenen tahansa tuomana:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/reuna/Tilauspalvelu.java" osa="ohitus"}
```

Kun hyökkääjä on sisäverkossa, se kutsuu palvelua suoraan
yhdyskäytävän ohi:

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/reuna/YhdyskaytavaTest.java" osa="ohitusTesti"}
```

```{.tuloste tiedosto="esimerkit/naytos/10-reuna.odotettu" alkaen="suora kutsu"}
```

Korjattu palvelu hyväksyy otsakkeen vain, jos sen toi yhdyskäytävä,
ja kutsujan identiteetti tulee mTLS-yhteydestä. Vielä vahvempi
ratkaisu on, että yhdyskäytävä välittää allekirjoitetun tokenin
(luku 6), jonka palvelu tarkistaa itse. Silloin palvelu ei luota
yhdyskäytävään käyttäjän identiteetin osalta lainkaan.

## Verkon segmentointi

Konttialustalla segmentointi tehdään verkkokäytännöillä. Seuraava
Kubernetesin NetworkPolicy sallii laskutukseen liikenteen vain
tilauspalvelusta ja hallinnasta. Se on tekstinä esitetty esimerkki,
jota ei testata:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: laskutus-sisaan
  namespace: kauppa
spec:
  podSelector:
    matchLabels: {app: laskutus}
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchExpressions:
              - {key: app, operator: In, values: [tilaus, hallinta]}
      ports:
        - {port: 8443, protocol: TCP}
```

Verkkokäytäntö perustuu tunnisteisiin ja IP-osoitteisiin, ei
kryptografiaan: se ei todista, kuka kutsuu. Se kuitenkin estää
murretun suosituspalvelun yhteydet laskutukseen kokonaan, joten
hyökkääjä ei pääse edes yrittämään. Lähtevä liikenne rajataan
samoin: palvelu, jonka ei tarvitse puhua internetiin, ei saa avata
yhteyttä sinne, mikä vaikeuttaa tietojen vientiä ja komentopalvelimen
käyttöä.

Verkkokäytäntö rajaa, kuka saa yhteyden. Sen, mitä murrettu kontti
pystyy itse tekemään (pääkäyttäjyys, tiedostojärjestelmän kirjoitus,
järjestelmäkutsut), rajaa työkuorman koventaminen taidossa *Kontit ja
pilvi-infrastruktuuri*. Sen, että klusteriin pääsee vain
allekirjoitettu ja tarkastettu kuva, varmistaa pääsynvalvoja, jonka
vaatimukset tulevat taidosta *Tietoturva kehitystyössä*.

## Viestinvälityksen suojaus

Kaikki palvelujen välinen liikenne ei ole kutsuja. Kun tilauspalvelu
julkaisee tapahtuman ja laskutus kuluttaa sen (*Palveluarkkitehtuurit*),
välissä on viestinvälitin, ja mTLS todentaa vain kummankin yhteyden
välittimeen. Laskutus tietää puhuvansa välittimelle; se ei tiedä,
kuka viestin julkaisi. Murrettu suosituspalvelu, jolla on yhteys
välittimeen, voisi julkaista tilausaiheeseen omia viestejään.

Suojaus on kolmessa kerroksessa:

| Kerros | Mitä tehdään | Mitä se torjuu |
|--------|--------------|----------------|
| välitin | palvelut todennetaan identiteetillä (mTLS); aihekohtaiset oikeudet: kuka saa julkaista, kuka tilata | väärä palvelu ei pääse aiheeseen |
| viesti | tuottaja allekirjoittaa kuoren; kuluttaja tarkistaa tuottajan, eheyden, iän ja toiston | väärennös ja muutos, vaikka välitin tai sen oikeudet pettäisivät |
| sisältö | arkaluonteinen runko salataan vastaanottajalle (luku 7) | välittimen levyn ja varmuuskopioiden lukija |

Viestitason tarkistus on sama periaate kuin tokenin `aud` ja `iss`
luvussa 6: kuluttaja ei luota kuljetukseen vaan todisteeseen, joka
kulkee viestin mukana.

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Viestit.java" osa="kuori"}
```

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Viestit.java" osa="kuluttaja"}
```

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/ViestitTest.java" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/naytos/10-viestit.odotettu"}
```

Toiston esto on turvallisuuden lisäksi oikeellisuutta: välittimet
toimittavat viestin vähintään kerran, joten kuluttajan on joka
tapauksessa oltava idempotentti. Nähtyjen tunnisteiden joukko
tallennetaan samassa transaktiossa kuin viestin vaikutus, ja siitä
poistetaan enimmäisikää vanhemmat. Myös käsittelemättä jääneiden
viestien jono (*dead letter queue*) sisältää asiakasdataa, ja sen
lukuoikeus rajataan kuten varsinaisen aiheen.

## Käytännössä

- **Jokainen palvelu todentaa ja valtuuttaa itse.** Yhdyskäytävä
  karsii, mutta palvelu päättää.
- **Poista sisäiset otsakkeet reunalla** ja aseta ne vasta
  todennuksen jälkeen. Sama koskee palveluverkon sivuvaunuja.
- **Validoi skeemaa vasten.** Tuntemattomien kenttien hylkäys estää
  massamäärityksen ja paljastaa asiakkaan ja palvelun
  sopimusvirheet aikaisin.
- **Oletuksena estävät verkkokäytännöt.** Nimiavaruuden ensimmäinen
  käytäntö estää kaiken, ja sallitut yhteydet lisätään nimeltä.
  Lähtevä liikenne rajataan samoin.
- **Hallintarajapinnat omaan verkkoonsa.** Actuator, metriikat ja
  ylläpidon rajapinnat eivät kuulu julkiseen yhdyskäytävään.
- **Aihekohtaiset oikeudet välittimeen**, ja viestin aitous
  tarkistetaan kuluttajassa. "Kaikki sisäiset palvelut saavat
  julkaista kaikkialle" on sama virhe kuin jaettu API-avain.

## Itsearviointi

- Osaat kuvata yhdyskäytävän tietoturvatehtävät: otsakkeiden
  siivous, todennus, nopeusrajoitus ja skeemavalidointi.
- Osaat selittää, miksi palvelu ei saa luottaa yhdyskäytävän
  asettamaan otsakkeeseen tarkistamatta, kuka sen toi.
- Osaat kirjoittaa verkkokäytännön, joka sallii vain nimetyt yhteydet.
- Osaat perustella lähtevän liikenteen rajaamisen.
