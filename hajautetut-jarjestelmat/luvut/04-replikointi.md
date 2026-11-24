# Replikointi

Replikointi tarkoittaa saman tiedon pitämistä usealla solmulla.
Replikoilla saadaan vikasietoisuutta (tieto säilyy, vaikka solmu
kaatuu), lukukapasiteettia (luvut jaetaan replikoille) ja pienempää
viivettä (replika on lähellä käyttäjää). Vaikeus on muutoksissa: kun
tieto muuttuu, muutoksen on päädyttävä kaikille replikoille, ja sillä
välin replikat ovat eri mieltä. Tapoja on kolme: yksi johtaja, useita
johtajia tai ei johtajaa lainkaan.

## Johtaja ja seuraajat

Tavallisin rakenne on yksi *johtaja* (*leader*, *primary*), joka ottaa
vastaan kaikki kirjoitukset ja lähettää muutokset *seuraajille*
(*follower*, *replica*). Luvut voidaan tehdä johtajalta tai, jos
vanha tieto kelpaa, seuraajilta. PostgreSQL:n ja MySQL:n replikointi,
MongoDB:n replikajoukot ja Kafkan osiot toimivat näin. Johtaja
järjestää kirjoitukset, joten samanaikaisia kirjoituksia ei tarvitse
ratkaista: järjestys on se, jossa johtaja ne näki.

Ratkaisevaa on, milloin johtaja kuittaa kirjoituksen asiakkaalle:

- **Asynkroninen**: heti, kun kirjoitus on johtajalla. Nopea, mutta jos
  johtaja kaatuu ennen kuin muutos on lähtenyt seuraajille, kuitattu
  kirjoitus katoaa.
- **Synkroninen**: vasta, kun kaikki seuraajat ovat kuitanneet. Mikään
  kuitattu ei katoa, mutta yksi hidas tai kaatunut seuraaja pysäyttää
  kaikki kirjoitukset.
- **Puolisynkroninen**: kun vähintään yksi seuraaja on kuitannut.
  Kompromissi, jota MySQL ja PostgreSQL tarjoavat asetuksena.

Esimerkin johtaja replikoi asynkronisessa tilassa erissä 50 ms välein,
kuten oikeat järjestelmät tekevät levyn ja verkon säästämiseksi. Muissa
tiloissa se lähettää heti ja odottaa kuittauksia:

```{.cpp tiedosto="esimerkit/04-johtaja.cpp" osa="johtaja"}
```

Kokeessa asiakas kirjoittaa 10 ms välein. Ensimmäisessä tilanteessa
johtaja kaatuu hetkellä 1000, ja seuraaja, jonka loki on pisin,
ylennetään uudeksi johtajaksi (*failover*). Toisessa tilanteessa
seuraaja 2 kaatuu hetkellä 500:

```{.cpp tiedosto="esimerkit/04-johtaja.cpp" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/04-johtaja.odotettu"}
```

Asynkroninen replikointi menetti keskimäärin viisi kuitattua
kirjoitusta jokaisessa vaihdossa: ne olivat johtajan erässä, kun se
kaatui. Synkroninen ja puolisynkroninen eivät menettäneet mitään,
mutta viive kasvoi, ja synkroninen pysähtyi seuraajan kaaduttua:
kirjoituksia kuitattiin vain 43 eli ne, jotka valmistuivat ennen
kaatumista. Puolisynkroninen jatkoi, koska yksi seuraaja riitti.

Puolisynkronisen tilan nollatulos on onnekas. Uudeksi johtajaksi
valittiin seuraaja, jolla oli pisin loki, mutta kuittaus vaati vain,
että *jollakin* seuraajalla on kirjoitus. Jos kirjoitus oli vain
lyhyemmän lokin seuraajalla, se katoaa. Oikea ratkaisu edellyttää, että
uudeksi johtajaksi voi tulla vain solmu, jolla on kaikki kuitatut
kirjoitukset, ja että tästä päätetään yhdessä. Tämä on konsensusta, ja
Raft ratkaisee sen luvuissa 7 ja 8.

Manuaalinen tai yksinkertainen automaattinen vaihto kätkee kaksi
muutakin vaaraa. *Halkeama-aivot* (*split brain*): vanha johtaja ei
ole kaatunut vaan erillään verkosta, ja se jatkaa kirjoitusten
vastaanottamista uuden johtajan rinnalla. *Väärä vaihto*: vikailmaisin
epäilee turhaan (ks. edellinen luku), ja vaihto aiheuttaa enemmän
haittaa kuin hidas johtaja. Kumpaankin tarvitaan termejä ja
kvoorumeja, jotka esitellään Raftin yhteydessä.

## Monta johtajaa

Monijohtajainen replikointi (*multi-leader*) sallii kirjoitukset usealla
solmulla, tyypillisesti yksi johtaja jokaisessa konesalissa tai
jokaisella laitteella, joka toimii myös ilman verkkoa (kalenteri,
muistiinpanot). Kirjoitukset ovat nopeita ja toimivat verkon jakautuessa,
mutta samaa tietoa voidaan muuttaa kahdessa paikassa samanaikaisesti.
Ristiriidat on ratkaistava jälkikäteen: LWW:llä (ja kirjoituksia katoaa),
vektorikellojen sisaruksilla (ja sovellus yhdistää) tai tietorakenteilla,
jotka yhdistyvät automaattisesti (seuraava luku).

## Johtajaton replikointi ja kvoorumit

Dynamo, Cassandra ja Riak eivät käytä johtajaa. Asiakas (tai sen puolesta
toimiva koordinaattori) lähettää kirjoituksen kaikille N replikalle ja
pitää sitä valmiina, kun W on kuitannut. Luku kysyy kaikilta ja odottaa
R vastausta, joista valitaan uusin versio. Jos

$$R + W > N,$$

jokainen lukukvoorumi ja jokainen kirjoituskvoorumi leikkaavat: ainakin
yksi luvun vastanneista on kuitannut viimeisimmän valmiin kirjoituksen.
Tyypillinen valinta on N = 3 ja R = W = 2.

Esimerkin replika säilyttää suurimman näkemänsä version:

```{.cpp tiedosto="esimerkit/04-kvoorumi.cpp" osa="replika"}
```

Kirjoittaja kirjoittaa versiot peräkkäin ja lähettää uudelleen, jos
kuittauksia ei kuulu:

```{.cpp tiedosto="esimerkit/04-kvoorumi.cpp" osa="kirjoittaja"}
```

Lukija lukee jatkuvasti ja tarkistaa jokaisesta luvusta, palauttiko se
vanhemman version kuin ennen luvun alkua valmistunut kirjoitus. Jos
lukukorjaus (*read repair*) on päällä, lukija lähettää uusimman
version niille vastanneille, joilla oli vanhempi:

```{.cpp tiedosto="esimerkit/04-kvoorumi.cpp" osa="lukija"}
```

Koe ajaa jokaisen R:n ja W:n yhdistelmän kymmenellä siemenellä verkossa,
joka kadottaa 10 % viesteistä:

```{.tuloste tiedosto="esimerkit/04-kvoorumi.odotettu"}
```

Kun R + W ≤ N, jopa joka kymmenes luku palautti vanhentuneen arvon: luku osui
replikaan, jolle kirjoitus ei ollut vielä tullut tai jolta se oli
kadonnut. Kun kvoorumit leikkaavat, vanhentuneita lukuja ei ollut.
Valinta siirtää kustannusta: R = 1, W = 3 tekee luvuista nopeita ja
kirjoituksista hitaita ja haavoittuvia (yksikin kaatunut replika
pysäyttää kirjoitukset), R = 3, W = 1 päinvastoin.

Kvoorumi ei yksin pidä replikoita ajan tasalla. Kun W = 2, kolmas
replika voi jäädä ilman kirjoitusta, jos viesti katoaa, eikä mikään
korjaa sitä. Lukukorjaus päivittää jäljessä olevan replikan, kun luku
osuu siihen; kokeessa se korjasi lopussa jäljessä olleen replikan.
Harvoin luettu tieto tarvitsee lisäksi taustalla toimivan
*anti-entropian*: replikat vertaavat sisältöään esimerkiksi
Merkle-puilla ja siirtävät erot.

Leikkaavat kvoorumit eivät myöskään tee järjestelmästä linearisoituvaa.
Jos kirjoitus on kesken ja vain yksi replika on saanut sen, yksi luku voi
nähdä uuden arvon ja sitä seuraava luku vanhan. Luku *Konsistenssimallit*
näyttää tämän ja korjauksen, jossa luku kirjoittaa näkemänsä arvon
kvoorumille ennen vastaamista. Löysät kvoorumit (*sloppy quorum*,
*hinted handoff*), joissa kirjoitus hyväksytään väliaikaisesti muille
kuin arvon omille replikoille, heikentävät takuuta entisestään.

## Käytännössä

- **Asynkronisen replikoinnin menetys on rajattu ajalla.** Tiedä, montako
  sekuntia kirjoituksia voi kadota vaihdossa (*replication lag*), ja
  valvo sitä. Monelle sovellukselle se on hyväksyttävää, rahaliikenteelle
  ei.
- **Puolisynkroninen ei yksin riitä.** Ilman konsensusta uusi johtaja voi
  olla seuraaja, jolta kuitattu kirjoitus puuttuu. Käytä valmista
  konsensukseen perustuvaa vaihtoa (etcd, ZooKeeper, Patroni, Raft
  tietokannan sisällä).
- **Estä halkeama-aivot.** Vanhan johtajan on lakattava kirjoittamasta,
  kun uusi valitaan: termit tai aitausmerkit (*fencing token*), joita
  tallennuskerros tarkistaa, ovat luotettavampia kuin vanhan solmun
  sammuttaminen.
- **Valitse R ja W kuorman mukaan.** $R = W = \lceil (N + 1)/2 \rceil$ on tasapainoinen
  oletus. Kirjoita ylös, mitä takuuta sovellus odottaa, ja testaa se.
- **Johtajaton ei tarkoita ristiriidatonta.** Samanaikaiset kirjoitukset
  samaan avaimeen on ratkaistava, ja oletuksena ratkaisu on usein LWW.

## Itsearviointi

- Osaat kuvata johtaja–seuraaja-replikoinnin ja asynkronisen,
  synkronisen ja puolisynkronisen kuittauksen hinnat.
- Osaat selittää, miksi johtajan vaihto voi hukata kuitattuja
  kirjoituksia ja mitä halkeama-aivot tarkoittavat.
- Osaat perustella ehdon R + W > N ja valita R:n ja W:n kuorman mukaan.
- Osaat toteuttaa kvoorumiluvun ja -kirjoituksen sekä lukukorjauksen
  simulaattorissa ja mitata vanhentuneiden lukujen osuuden.
- Osaat kertoa, miksi leikkaavat kvoorumit eivät yksin takaa
  linearisoituvuutta.
