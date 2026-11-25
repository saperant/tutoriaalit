# Tietokantamuutokset

Sovelluksen versio voidaan vaihtaa ja perua, koska sovellus on
tilaton: vanha paketti korvataan uudella. Tietokantaa ei voi korvata,
koska sen sisältö on juuri se, mitä ei saa hukata. Tietokannan
rakenteen muutos on siksi jatkuvan toimituksen vaikein osa, ja
useimmat asteittaisen julkaisun epäonnistumiset johtuvat siitä.

Ongelma tiivistyy yhteen vaatimukseen. Edellisen luvun strategioissa
vanha ja uusi sovellusversio ovat ajossa yhtä aikaa, ja ne käyttävät
samaa tietokantaa. **Tietokannan rakenteen on siis joka hetki sovittava
kaikille ajossa oleville sovellusversioille.**

## Migraatiot

Tietokannan rakenne kuuluu versionhallintaan kuten koodi. Rakennetta
ei kuitenkaan tallenneta lopputilana, vaan muutosten sarjana:
jokainen migraatio on numeroitu skripti, joka vie tietokannan yhdestä
versiosta seuraavaan. Tietokannassa on taulu, joka kertoo, mitkä
migraatiot on ajettu. Flyway, Liquibase, Alembic ja useimpien
sovelluskehysten omat työkalut toimivat näin.

Käytännöt ovat vakiintuneet.

- **Migraatiot ajaa putki**, ei ihminen. Sama skripti ajetaan
  jokaisessa ympäristössä samassa järjestyksessä, joten tuotannon ajo
  on jo harjoiteltu testissä ja esituotannossa.
- **Ajettua migraatiota ei muokata.** Korjaus on uusi migraatio.
  Muokattu skripti tarkoittaisi, että ympäristöissä on eri rakenne
  samalla versionumerolla.
- **Migraatiot testataan.** Tyhjästä kannasta uusimpaan versioon
  pääseminen ja tuotannon kaltaisen datan siirto testataan putkessa
  (ks. *Integraatiotestaus ja Testcontainers*).
- **Migraatio ja sitä tarvitseva koodi kulkevat eri käyttöönotoissa**,
  kuten seuraava osio näyttää.

## Laajenna ja supista

Yhteensopivuuden säilyttävä tapa muuttaa rakennetta on jakaa muutos
osiin, joista jokainen on yksinään turvallinen. Mallin nimi on
laajenna–supista (*expand–contract*) tai rinnakkainen muutos
(*parallel change*), ja Scott Ambler ja Pramod Sadalage ovat kuvanneet
sen muunnelmia kirjassa *Refactoring Databases*.

```{.dot otsikko="Laajenna–supista: vanha ja uusi rakenne ovat olemassa rinnan, kunnes mikään ei enää käytä vanhaa"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.2;
  node [margin="0.07,0.05"];
  a [label="1. laajenna\nrakennetta"]; b [label="2. kirjoita\nmolempiin"];
  c [label="3. täytä\nvanhat rivit"]; d [label="4. lue\nuudesta"];
  e [label="5. lopeta\nvanhaan\nkirjoitus"]; f [label="6. supista:\npoista vanha"];
  a -> b -> c -> d -> e -> f;
}
```

Esimerkissä asiakastaulun sarake `nimi` jaetaan sarakkeiksi `etunimi`
ja `sukunimi`. Muutos näyttää yhdeltä `ALTER TABLE` -lauseelta, mutta
vaatii alkuperäisen version V1 lisäksi kolme uutta sovellusversiota.
Jokainen niistä on oma käyttöönottonsa.

```{.python tiedosto="esimerkit/luku09/migraatio.py" osa="versiot"}
```

Tietokannan muutoksia on kolme: laajennus, vanhojen rivien täyttö ja
supistus.

```{.python tiedosto="esimerkit/luku09/migraatio.py" osa="migraatiot"}
```

Polku kertoo, missä järjestyksessä migraatiot ja sovellusversiot
otetaan käyttöön ja mitkä versiot ovat kullakin hetkellä ajossa
rinnan.

```{.python tiedosto="esimerkit/luku09/migraatio.py" osa="polku"}
```

Esimerkki ajaa polun SQLite-tietokantaan. Jokaisella askeleella kaikki
sillä hetkellä ajossa olevat versiot lisäävät rivin ja lukevat kaikki
rivit, ja tulos tarkistetaan. Sen jälkeen kokeillaan kolmea oikopolkua.

```{.tuloste tiedosto="esimerkit/luku09/migraatio.odotettu"}
```

Oikea polku pitää jokaisen version toimivana jokaisella askeleella.
Kolme oikopolkua epäonnistuvat kukin omalla tavallaan.

**Kaikki kerralla.** Jos sarake vaihdetaan yhdellä migraatiolla, vanha
versio, joka on rullaavan päivityksen aikana vielä ajossa, kaatuu
heti, koska sen käyttämää saraketta ei enää ole. Perinteinen ratkaisu
on huoltokatko: kaikki pysäytetään, kanta muutetaan ja uusi versio
käynnistetään. Se toimii, mutta ei sovi jatkuvaan toimitukseen.

**Uusi lukija ennen täyttöä.** Jos versio V3 alkaa lukea uusia
sarakkeita ennen kuin vanhat rivit on täytetty, se ei kaadu. Se
näyttää käyttäjälle puuttuvia nimiä. Tämä on pahempi kuin kaatuminen,
koska mikään hälytys ei laukea.

**Supistus liian aikaisin.** Jos vanha sarake poistetaan, kun V3 on
vielä ajossa ja kirjoittaa siihen, V3 kaatuu. Supistus tehdään vasta,
kun mikään käynnissä oleva versio ei koske vanhaan rakenteeseen.

## Peruminen

Laajenna–supista tekee perumisesta turvallista lähes koko matkan.
Jokaisella askeleella ennen supistusta edellinen sovellusversio toimii
nykyisellä rakenteella, joten sovelluksen voi perua koskematta
tietokantaan. Tämä on mallin tärkein käytännön hyöty: sovellus ja
tietokanta voidaan perua toisistaan riippumatta.

Supistus on ainoa peruuttamaton askel. Poistettua saraketta ei saa
takaisin muuten kuin varmuuskopiosta. Siksi supistus tehdään viimeisenä
ja kiireettä: päivien tai viikkojen päästä, kun on varmaa, ettei
vanhaan palata. Moni tiimi nimeää sarakkeen ensin uudelleen ja poistaa
sen vasta myöhemmin, jolloin unohtunut käyttäjä löytyy ilman tietojen
menetystä.

Migraatiotyökalut tarjoavat usein jokaiselle migraatiolle
vastakkaisen *down*-skriptin. Niihin kannattaa suhtautua varauksella.
Rakenteen voi palauttaa, mutta tietoa ei: jos migraatio poisti
sarakkeen tai yhdisti kaksi, vastakkainen skripti luo tyhjän sarakkeen.
Harvoin ajettu ja harvoin testattu perumisskripti on lisäksi
epäluotettava juuri silloin, kun sitä tarvitaan. Taaksepäin
yhteensopivat migraatiot ja korjaus eteenpäin ovat kestävämpi
perusta.

## Suuret taulut

Pienessä taulussa jokainen askel on hetken työ. Suuressa taulussa
kaksi asiaa muuttuu.

**Lukot.** Osa rakennemuutoksista lukitsee taulun muutoksen ajaksi, ja
satojen miljoonien rivien taulussa se voi tarkoittaa minuuttien tai
tuntien katkoa. Mitkä muutokset lukitsevat, riippuu
tietokantajärjestelmästä ja sen versiosta, ja se on tarkistettava
dokumentaatiosta ja kokeiltava tuotannon kokoisella datalla.
Tavallisia keinoja ovat sarakkeen lisääminen ilman oletusarvoa tai
rajoitetta, indeksin luonti taustalla ja erilliset työkalut, jotka
rakentavat taulusta kopion ja vaihtavat sen paikalleen.

**Täyttö.** Yksi `UPDATE` koko tauluun on pitkä transaktio, joka
kuormittaa kantaa ja replikointia. Täyttö tehdään erissä, muutama
tuhat riviä kerrallaan, taukoja pitäen ja niin, että sen voi
keskeyttää ja jatkaa. Esimerkin ehto `WHERE etunimi IS NULL` tekee
täytöstä toistettavan: uusi ajo jatkaa siitä, mihin edellinen jäi.

Näistä syistä pitkä tietojen täyttö ei kuulu käyttöönoton
migraatioihin, jotka ajetaan putkessa sekunneissa, vaan se ajetaan
erillisenä taustatyönä.

## Sama malli muualla

Laajenna–supista ei koske vain tietokantoja. Sama ongelma on kaikkialla,
missä kaksi osapuolta jakaa rakenteen eivätkä päivity yhtä aikaa.

| Jaettu rakenne | Osapuolet | Laajenna | Supista |
|-------------------|------------------|----------------------|----------------------|
| tietokannan skeema | sovelluksen versiot | lisää sarake tai taulu | poista vanha |
| palvelun rajapinta | palvelu ja asiakkaat | lisää kenttä tai uusi versio | poista vanha, kun kukaan ei kutsu |
| viestin muoto | lähettäjä ja vastaanottajat | vastaanottaja ymmärtää molemmat | lähettäjä lopettaa vanhan |
| asetustiedosto | sovellus ja ympäristöt | sovellus hyväksyy molemmat nimet | poista vanha nimi |
| funktion allekirjoitus | kirjasto ja kutsujat | lisää uusi, merkitse vanha vanhentuneeksi | poista seuraavassa pääversiossa |

Sääntö on kaikissa sama: ensin lisätään, sitten siirretään käyttö,
lopuksi poistetaan, eikä poistoa tehdä ennen kuin on *mitattu*, että
vanhaa ei käytetä. Rajapintojen yhteensopivuutta käsittelee
*Palveluarkkitehtuurit*.

## Rajat

- **Malli on hidas.** Yksi sarakkeen jako vaatii kolme käyttöönottoa
  ja kolme migraatiota. Hinta on kohtuullinen vain, jos käyttöönotot
  ovat halpoja, eli putki on kunnossa. Tässä näkyy, miksi tutoriaalin
  aiheet riippuvat toisistaan.
- **Huoltokatko on joskus oikea valinta.** Sisäinen järjestelmä, jota
  kukaan ei käytä öisin, voidaan pysäyttää kymmeneksi minuutiksi.
  Laajenna–supista on kannattava, kun katko maksaa enemmän kuin
  ylimääräiset käyttöönotot.
- **Kaikki muutokset eivät ole rakenteellisia.** Jos tiedon *merkitys*
  muuttuu, esimerkiksi hinta vaihtuu verottomasta verolliseksi samassa
  sarakkeessa, mikään skeema ei suojaa. Turvallisempaa on lisätä uusi
  sarake uudella merkityksellä.

## Käytännössä

- Pidä migraatiot versionhallinnassa ja anna putken ajaa ne.
- Jaa jokainen yhteensopimaton muutos laajennukseen, siirtymään ja
  supistukseen, ja tee ne eri käyttöönotoissa.
- Varmista ennen jokaista askelta, että kaikki sen aikana ajossa
  olevat versiot toimivat sekä vanhalla että uudella rakenteella.
- Tee supistus viimeisenä ja vasta, kun olet mitannut, ettei vanhaa
  käytetä.
- Aja suurten taulujen täyttö erissä erillisenä, keskeytettävänä
  työnä.
- Kokeile migraatio tuotannon kokoisella datalla ennen tuotantoa.

## Itsearviointi

- Osaat selittää, miksi tietokannan rakenteen on sovittava kaikille
  ajossa oleville sovellusversioille.
- Osaat jakaa sarakkeen uudelleennimeämisen tai jakamisen
  laajenna–supista-askeliin ja kertoa, mikä sovellusversio kuuluu
  mihinkin askeleeseen.
- Osaat kertoa, mitä tapahtuu, jos askelten järjestys rikotaan, ja
  miksi hiljaa puuttuva tieto on pahempi kuin kaatuminen.
- Osaat perustella, miksi supistus on ainoa peruuttamaton askel ja
  miksi vastakkaisiin migraatioihin ei pidä nojata.
- Osaat soveltaa samaa mallia rajapinnan tai viestimuodon muutokseen.
