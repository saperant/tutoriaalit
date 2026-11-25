# Infrastruktuuri koodina ja GitOps

Tähän asti putken läpi on kulkenut sovellus. Ympäristö, jossa sovellus
ajetaan, on kuitenkin yhtä lailla muuttuva asia: palvelimet, verkot,
tietokannat, kuormantasaajat ja niiden asetukset. Jos ne tehdään käsin,
ne ovat putken ulkopuolella, eikä mikään edellä sanotusta koske niitä.
Infrastruktuuri koodina (*infrastructure as code*, IaC) tuo ympäristön
samojen käytäntöjen piiriin, ja GitOps on tapa järjestää sen
käyttöönotto.

Työkalut on esitelty muualla: Terraform ja Helm tutoriaalissa
*Säiliöt ja pilvi-infrastruktuuri*, Ansible tutoriaalissa
*Palvelinympäristöt*. Tämä luku käsittelee periaatteet, jotka ovat
niille yhteiset.

## Käskevä ja deklaratiivinen

Ympäristön voi kuvata kahdella tavalla. Käskevä (*imperative*) kuvaus
on luettelo toimenpiteitä: luo palvelin, asenna paketti, avaa portti.
Deklaratiivinen kuvaus kertoo lopputuloksen: palvelimia on kolme,
paketti on asennettu, portti on auki. Työkalu päättelee toimenpiteet
vertaamalla kuvausta nykytilaan.

Ero näkyy, kun sama asia ajetaan kahdesti.

```{.python tiedosto="esimerkit/luku10/suunnitelma.py" osa="kaskeva"}
```

Käskevä skripti lisää kolme palvelinta joka ajolla. Se toimii oikein
vain, jos lähtötila on se, jonka kirjoittaja oletti. Deklaratiivinen
malli vertaa haluttua tilaa nykyiseen ja tuottaa suunnitelman.

```{.python tiedosto="esimerkit/toimitus/tasmaytys.py" osa="suunnitelma"}
```

Haluttu tila on tiedostossa, ja ympäristön lähtötilassa on yksi
vanhentunut palvelu ja yksi ylimääräinen.

```{.python tiedosto="esimerkit/luku10/suunnitelma.py" osa="deklaratiivinen"}
```

```{.tuloste tiedosto="esimerkit/luku10/suunnitelma.odotettu"}
```

Tulosteessa on deklaratiivisen mallin kolme ominaisuutta.

**Idempotenssi.** Toteutuksen jälkeen uusi suunnitelma on tyhjä.
Saman kuvauksen voi ajaa kuinka monta kertaa tahansa, ja tulos on
sama. Keskeytynyt ajo korjataan ajamalla uudelleen.

**Suunnitelma ennen toteutusta.** Muutokset nähdään ennen kuin mitään
tehdään. Suunnitelma on katselmoitavissa: rivi *poista
vanha-raportointi* on se, johon katselmoijan pitää pysähtyä.
Terraformin `plan` ja Ansiblen tarkistustila ovat tätä varten.

**Ajautuman havaitseminen.** Kun joku muuttaa ympäristöä käsin, ero
halutun ja todellisen tilan välillä näkyy seuraavassa suunnitelmassa.
Ilman kuvausta käsin tehty muutos olisi tietoa, joka on vain tekijän
muistissa.

Malli on tarkoituksella yksinkertainen. Oikeissa työkaluissa vaikeus
on siinä, mitä tässä on yksi sanakirja: nykytilan selvittäminen. Se on
kysyttävä pilvipalvelun rajapinnasta tai luettava työkalun omasta
tilatiedostosta, resursseilla on keskinäisiä riippuvuuksia, jotka
määräävät järjestyksen, ja osa muutoksista onnistuu vain tuhoamalla ja
luomalla uudelleen.

## Infrastruktuurikoodin käytännöt

Kun ympäristö on koodia, siihen pätee kaikki, mitä edellisissä luvuissa
sanottiin koodista.

- **Versionhallinta.** Jokaisella muutoksella on tekijä, peruste ja
  ajankohta. Kysymykseen "mikä muuttui tiistaina" on vastaus.
- **Katselmointi.** Muutos ja sen suunnitelma katselmoidaan ennen
  toteutusta.
- **Putki.** Kuvaus tarkistetaan automaattisesti (syntaksi, skeema,
  käytäntösäännöt), suunnitelma tuotetaan yhdistämispyyntöön ja
  toteutus tapahtuu putkesta, ei kehittäjän koneelta.
- **Sama kuvaus joka ympäristöön.** Testi- ja tuotantoympäristö
  luodaan samasta koodista eri parametreilla. Tämä on se luvun 5
  ympäristöjen yhtäläisyys, jota käsin ei saavuteta.
- **Käsin ei muuteta.** Jokainen käsin tehty muutos on ajautumaa, jonka
  seuraava toteutus joko kumoaa tai johon se kompastuu.

Viimeinen sääntö on vaikein pitää, koska häiriön aikana käsin
korjaaminen on nopeinta. Kestävä käytäntö on sallia se hätätilanteessa
ja vaatia, että muutos viedään kuvaukseen heti sen jälkeen. Ajautuman
tarkistus kertoo, jos näin ei tehty.

Sama ajattelu ulottuu palvelimen sisältöön. *Muuttumaton
infrastruktuuri* tarkoittaa, että käynnissä olevaa palvelinta tai
säiliötä ei päivitetä paikallaan, vaan rakennetaan uusi kuva ja
korvataan vanha. Se on luvun 5 artefaktisääntö sovellettuna koneeseen.

## GitOps

GitOps on käyttöönottomalli, jossa versionhallinnan sisältö *on*
ympäristön haluttu tila ja ympäristö pitää itsensä sen mukaisena.
Termi on Weaveworksin vuodelta 2017. OpenGitOps-hanke on tiivistänyt
mallin neljään periaatteeseen.

1. **Deklaratiivinen.** Järjestelmän haluttu tila on kuvattu
   deklaratiivisesti.
2. **Versioitu ja muuttumaton.** Haluttu tila säilytetään niin, että
   sen versiot ovat muuttumattomia ja koko historia on tallessa.
3. **Haetaan automaattisesti.** Ohjelmistoagentit hakevat halutun
   tilan lähteestä itse.
4. **Täsmäytetään jatkuvasti.** Agentit tarkkailevat todellista tilaa
   jatkuvasti ja pyrkivät saattamaan sen halutuksi.

Kaksi ensimmäistä ovat infrastruktuuria koodina. Kaksi jälkimmäistä
ovat GitOpsin oma lisä, ja ne erottavat sen tavallisesta putkesta.

```{.dot otsikko="Työntävä putki ja vetävä agentti: GitOpsissa ympäristö hakee muutokset itse ja vertaa tilaansa jatkuvasti"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.45;
  subgraph cluster_a {
    label="työntävä"; style=dashed;
    g1 [label="repositorio"]; p1 [label="putki"]; y1 [label="ympäristö"];
    g1 -> p1 [label="heräte"]; p1 -> y1 [label="toteuta"];
  }
  subgraph cluster_b {
    label="vetävä (GitOps)"; style=dashed;
    g2 [label="repositorio"]; a2 [label="agentti"]; y2 [label="ympäristö"];
    a2 -> g2 [label="hae"]; a2 -> y2 [label="vertaa ja korjaa"];
  }
}
```

Työntävässä mallissa putki ottaa yhteyden ympäristöön ja tekee
muutoksen, kun repositorio muuttuu. Vetävässä mallissa ympäristössä
ajetaan agenttia, joka lukee repositoriota ja korjaa erot. Tutoriaali
*Säiliöt ja pilvi-infrastruktuuri* vertaa malleja Kubernetesin
kannalta (Argo CD, Flux). Erot ovat yleisiä.

- **Tunnukset.** Työntävässä mallissa putkella on kirjoitusoikeus
  tuotantoon. Vetävässä mallissa agentti tarvitsee vain lukuoikeuden
  repositorioon, ja tuotannon tunnukset pysyvät tuotannossa.
- **Ajautuma.** Putki toimii vain, kun repositorio muuttuu. Agentti
  vertaa jatkuvasti ja huomaa myös muutokset, jotka tehtiin ohi.
- **Palautuminen.** Jos ympäristö tuhoutuu, agentti rakentaa sen
  uudelleen repositoriosta ilman, että kukaan käynnistää mitään.

## Täsmäytys mallina

Agentin ydin on silmukka, joka lukee halutun tilan rungon kärjestä ja
toteuttaa erot. Esimerkissä haluttu tila on JSON-tiedosto oikeassa
Git-repositoriossa ja klusteria esittää sanakirja.

```{.python tiedosto="esimerkit/luku10/gitops.py" osa="agentti"}
```

Esimerkki käy läpi viisi tilannetta: ensimmäinen käyttöönotto, kierros
ilman muutoksia, käsin tehty muutos klusterissa, uusi versio ja sen
peruminen.

```{.tuloste tiedosto="esimerkit/luku10/gitops.odotettu"}
```

Kolmas kierros korjaa ajautuman: joku nosti kopioiden määrän käsin
viiteen, ja agentti palautti sen kahteen. Tämä on GitOpsin lupaus ja
samalla sen terävin reuna. Jos käsin tehty muutos oli hätäkorjaus
kuormapiikkiin, agentti kumosi sen. Useimmat agentit voi siksi asettaa
myös vain ilmoittamaan erosta, ja häiriön ajaksi täsmäytys voidaan
pysäyttää.

Viimeinen kierros näyttää perumisen. Versio 1.5.0 perutaan komennolla
`git revert`, joka tekee uuden commitin. Agentille se on tavallinen
muutos: haluttu tila on taas 1.4.0, ja se toteutetaan. Historiaan jää
sekä viallinen julkaisu että sen peruminen, tekijöineen ja
kellonaikoineen. Erillistä perumismekanismia tai käyttöönottolokia ei
tarvita.

## Repositorion rakenne ja edistäminen

Kaksi rakennekysymystä tulee vastaan heti.

**Sovelluksen koodi ja ympäristön kuvaus eri repositorioihin.**
Sovelluksen putki rakentaa artefaktin, ja sen viimeinen askel on
muutos kuvausrepositorioon: uusi versio testiympäristön tiedostoon.
Erottelulla on kaksi syytä. Kuvauksen muutos ei käynnistä sovelluksen
rakennusta uudelleen, ja oikeudet voidaan rajata erikseen: moni saa
muuttaa koodia, harvempi tuotannon kuvausta.

**Ympäristöt hakemistoina, ei haaroina.** Houkutteleva rakenne on
haara ympäristöä kohden: `testi`, `esituotanto`, `tuotanto`. Se
johtaa pitkäikäisiin haaroihin, jotka ajautuvat erilleen, eli
täsmälleen siihen ongelmaan, jonka luku 3 poisti koodista.
Kestävämpi rakenne on yksi runko, jossa jokaisella ympäristöllä on
oma hakemistonsa ja yhteinen pohja, jota ympäristöt tarkentavat.

Edistäminen ympäristöstä toiseen on silloin commit, joka muuttaa
version tuotannon tiedostossa samaksi kuin esituotannon. Sen voi tehdä
ihminen yhdistämispyynnöllä tai putki, kun edellisen ympäristön
tarkistukset ovat menneet läpi. Kummassakin tapauksessa luvun 5 sääntö
pätee: versio viittaa samaan muuttumattomaan artefaktiin.

## Rajat ja kritiikki

GitOps on hyödyllinen malli, jonka ympärillä on paljon markkinointia.
Sen rajat kannattaa tuntea.

- **Git ei ole koko totuus.** Repositorio kertoo halutun tilan, ei
  todellista. Onko käyttöönotto valmis, onnistuiko se ja milloin, on
  kysyttävä agentilta tai ympäristöstä. Putki, joka päättyy
  commitiin, ei tiedä, mitä sen jälkeen tapahtui, ellei sitä
  rakenneta kysymään.
- **Kaikki ei ole tilaa.** Tietokantamigraatio, kertaluonteinen
  tietojen korjaus tai varmuuskopion palautus on toimenpide, ei tila.
  Ne sopivat deklaratiiviseen malliin huonosti ja tarvitsevat oman
  käsittelynsä.
- **Peruminen ei peru dataa.** `git revert` palauttaa kuvauksen.
  Tietokantaan kirjoitettu tieto ja ulos lähetetyt viestit pysyvät.
  Luvun 9 yhteensopivuusvaatimus on voimassa.
- **Salaisuudet eivät kuulu repositorioon selväkielisinä.** Jos kaikki
  on Gitissä, myös tunnukset pyrkivät sinne. Ratkaisut, kuten
  salattuina tallennetut salaisuudet tai viittaukset
  salaisuusvarastoon, käsittelee *Tietoturva kehitystyössä*.
- **Järjestys ja riippuvuudet.** Täsmäytys ei luonnostaan tiedä, että
  tietokannan on oltava valmis ennen sovellusta. Työkaluissa on tähän
  keinoja, mutta ne ovat lisättyä monimutkaisuutta.
- **Vianetsintä on epäsuoraa.** Kun muutos ei toteudu, syy on agentin
  lokeissa, ei putken tulosteessa. Palaute on hitaampaa kuin
  suorassa komennossa.
- **Malli sopii parhaiten alustoille, jotka ovat itse
  deklaratiivisia.** Kubernetesissa täsmäytys on alustan
  perusmekanismi. Yksittäisellä palvelimella tai perinteisessä
  virtuaalikoneympäristössä sama saavutetaan
  konfiguraationhallinnalla, jota ajetaan ajastetusti, ja ajatus
  jatkuvasti täsmäytettävästä tilasta on siellä vuosikymmeniä
  vanhempi kuin sana GitOps.

Pienessä järjestelmässä työntävä putki, joka toteuttaa versioidun
kuvauksen, antaa suurimman osan hyödystä vähemmällä koneistolla.
GitOpsin lisäarvo kasvaa, kun ympäristöjä tai klustereita on monta,
kun ajautuma on todellinen ongelma tai kun tuotannon tunnuksia ei
haluta putken ulottuville.

## Käytännössä

- Kuvaa ympäristö deklaratiivisesti ja pidä kuvaus versionhallinnassa.
- Tuota suunnitelma jokaisesta muutoksesta ja katselmoi se, etenkin
  poistot.
- Aja ajautuman tarkistus säännöllisesti, vaikka et korjaisi
  automaattisesti.
- Luo ympäristöt samasta koodista eri parametreilla, hakemistoina
  samassa rungossa.
- Tee perumisesta tavallinen muutos: `git revert` ja sama putki.
- Sovi, miten hätätilanteessa käsin tehty muutos viedään kuvaukseen
  jälkikäteen.

## Itsearviointi

- Osaat erottaa käskevän ja deklaratiivisen kuvauksen ja selittää,
  miksi jälkimmäinen on idempotentti.
- Osaat kertoa, mitä suunnitelma ja ajautuman tarkistus antavat ja
  miksi käsin tehty muutos on ongelma.
- Osaat luetella OpenGitOpsin neljä periaatetta ja kertoa, mitkä
  niistä erottavat GitOpsin muusta infrastruktuurista koodina.
- Osaat verrata työntävää ja vetävää käyttöönottoa tunnusten,
  ajautuman ja palautumisen kannalta.
- Osaat perustella, miksi ympäristöt kuvataan hakemistoina eikä
  haaroina.
- Osaat nimetä asioita, joita GitOps ei ratkaise.
