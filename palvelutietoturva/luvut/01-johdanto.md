# Johdanto {.runko-johdanto}

Kun järjestelmä jaetaan palveluiksi, sen hyökkäyspinta kasvaa. Yhden
sovelluksen sisäiset funktiokutsut muuttuvat verkkokutsuiksi, joita
kuka tahansa verkossa oleva voi yrittää tehdä. Tietokannan salasana ei
ole enää yhdessä paikassa vaan kymmenessä. Murto yhteen palveluun
avaa reitin muihin, ellei sitä ole erikseen estetty.

Tämä tutoriaali käsittelee palvelukokonaisuuden suojaamisen: miten
palvelut tunnistavat toisensa, miten ne saavat vain tarvitsemansa
oikeudet, miten salaisuudet pidetään salassa tuotannossa ja miten
murto havaitaan, rajataan ja selvitetään. Yksittäisen sovelluksen
haavoittuvuudet (injektiot, XSS, istunnot) ovat taidossa
*Web-sovellusten tietoturva*, eikä niitä toisteta.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Palveluarkkitehtuurit* (palvelujen jako,
synkroninen ja asynkroninen viestintä, yhdyskäytävä) ja *Kryptografia*
(TLS 1.3, varmenteet ja PKI, allekirjoitukset, AEAD). Myös
*Taustapalvelut* (Spring Boot ja Spring Security) ja *Tietoturvan
perusteet* (uhkamallinnus, pääsynhallinnan mallit, tiivisteketju
auditointilokissa) oletetaan.

Verkon segmentointi palomuureilla ja VLANeilla on taidossa
*Verkkoinfrastruktuuri* ja Kubernetesin perusteet sekä työkuorman
koventaminen taidossa *Kontit ja pilvi-infrastruktuuri*. Tässä
keskitytään siihen, mitä palvelujen ja niiden alustan pitää tehdä,
jotta verkon sijainti ei ole luottamuksen peruste.

## Vastuulauseke

Materiaali on tarkoitettu opetukseen ja oman järjestelmän
suojaamiseen. Esimerkeissä on "hyökkäys"-testejä: väärennetty otsake,
vieraan varmentajan varmenne ja toiselle palvelulle myönnetty token.
Ne kohdistuvat paketin omiin palveluihin, jotka käynnistyvät testin
sisällä omalla koneella ja sammuvat sen päätyttyä.

- **Käytä tekniikoita vain omiin järjestelmiisi tai kohteisiin,
  joihin sinulla on kirjallinen lupa.** Työpaikalla luvan antaa
  järjestelmän omistaja, ja siinä rajataan kohteet, ajankohta ja
  menetelmät.
- **Luvaton tunkeutuminen on rikos** (rikoslain 38. luku: muun muassa
  tietomurto ja tietojärjestelmän häirintä). Tämä on yleiskuvaus, ei
  oikeudellinen neuvo.
- **Tekijät eivät vastaa materiaalin väärinkäytöstä.** Paketissa ei
  ole työkaluja vieraiden verkkojen tai palvelujen tutkimiseen.

Oman palvelukokonaisuuden koettelu näillä kysymyksillä on juuri se,
mihin tutoriaali kannustaa: jos tämä palvelu murretaan, mihin siitä
pääsee?

## Esimerkkijärjestelmä

Esimerkit käsittelevät samaa verkkokauppaa kuin palveluarkkitehtuurit.
Palvelut ovat luottamusalueella `kauppa.example`, ja niiden
identiteetit ovat SPIFFE-tunnisteita:

| Palvelu | Identiteetti | Tehtävä |
|---------|--------------|---------|
| tilaus | `spiffe://kauppa.example/tilaus` | tilaukset, kutsuu laskutusta |
| laskutus | `spiffe://kauppa.example/laskutus` | laskut ja asiakkaan maksutiedot |
| suositukset | `spiffe://kauppa.example/suositukset` | lukee tilaushistoriaa; hyökkäysten lähtöpiste |
| hallinta | `spiffe://kauppa.example/hallinta` | ylläpidon työkalut |
| yhdyskäytävä | `spiffe://kauppa.example/yhdyskaytava` | julkinen API |

Suosituspalvelu on esimerkeissä se, joka murretaan: se käyttää
kolmannen osapuolen koneoppimiskirjastoa, ja sen kautta hyökkääjä
pääsee sisäverkkoon. Jokaisessa luvussa kysytään, mitä hyökkääjä voi
sieltä tehdä ja mikä sen estää.

```{.dot otsikko="Esimerkkijärjestelmä. Katkoviiva rajaa luottamusalueen, jonka sisällä hyökkääjä jo on. Pisteviivat ovat tutoriaalin kysymys: pääseekö murrettu suosituspalvelu maksutietoihin, varmentajaan tai salaisuuksiin, ja mikä sen estää."}
digraph {
  rankdir=TB; nodesep=0.45; ranksep=0.45;
  selain [label="asiakkaan selain"];
  hyokkaaja [label="hyökkääjä", style="rounded,dashed"];
  subgraph cluster_alue {
    label="luottamusalue kauppa.example"; labeljust=l; style="rounded,dashed"; fontsize=10;
    yk [label="yhdyskäytävä\n(julkinen API)"];
    suositukset [label="suositukset\n(murrettu)", penwidth=2];
    tilaus [label="tilaus"];
    hallinta [label="hallinta"];
    laskutus [label="laskutus\n(maksutiedot)"];
    tuki [label="varmentaja, vaihtopalvelu,\nsalaisuusvarasto", shape=box, style="dashed"];
  }
  selain -> yk [label=" käyttäjän token"];
  yk -> tilaus;
  tilaus -> laskutus [label=" mTLS + vaihdettu token"];
  hallinta -> laskutus;
  suositukset -> tilaus [label=" tilaushistoria"];
  hyokkaaja -> suositukset [style=dashed, label=" haavoittuva kirjasto"];
  suositukset -> laskutus [style=dotted, label=" pääseekö?"];
  suositukset -> tuki [style=dotted, label=" pääseekö?"];
}
```

Kaavion kolme tukipalvelua esitellään myöhemmin: varmentaja antaa
palveluille identiteetit (luku 3), vaihtopalvelu rajaa tokenit
kohdekohtaisiksi (luku 6) ja salaisuusvarasto jakaa tunnukset
(luvut 7–8).

## Esimerkkiprojekti

`esimerkit/` on Maven-projekti (Java 21, Spring Boot 4.2), jossa on
viisi modulia. Neljä ensimmäistä käyttävät vain JDK:ta ja muutamaa
kirjastoa, jotta mekanismi näkyy. Viimeinen kokoaa saman Spring Boot
-palveluksi.

| Moduli | Luvut | Mitä näyttää |
|--------|-------|--------------|
| `luottamus` | 2–6, 10 | oma varmentaja, mTLS, kierto, palvelutokenit, tokenien vaihto, yhdyskäytävä, viestin kuori |
| `salaisuudet` | 7–8 | avainpalvelu, kirjekuorisalaus, dynaamiset tunnukset |
| `kaytannot` | 2, 9 | käytäntömoottori, vähimmät oikeudet, käytäntöjen tarkastus |
| `havainnointi` | 12–13 | auditointiloki, peittäminen, poikkeamat |
| `palvelu` | 11 | Spring Boot -palvelu mTLS:llä ja palvelukohtaisilla oikeuksilla |

Testit ajetaan komennolla `make` hakemistossa `esimerkit`. Ne eivät
tarvitse verkkoa (riippuvuuksien latausta lukuun ottamatta) eivätkä
Dockeria: varmentaja, salaisuuspalvelu ja palvelut käynnistetään testin
sisällä. Jokaisesta haavoittuvuudesta on haavoittuva ja korjattu
versio, ja testi osoittaa, että hyökkäys onnistuu ensimmäistä vastaan
ja epäonnistuu jälkimmäistä vastaan.

Testi kertoo, pitääkö väite, mutta ei näytä, mitä palvelu vastasi.
Siksi testien joukossa on **näytösajoja** (`NaytosTest.java`): ne
tekevät samat kutsut ja kirjoittavat vastaukset tauluksi. Taulu
verrataan tiedostoon `esimerkit/naytos/*.odotettu`, ja lukujen
tulostelohkot ovat näitä tiedostoja. Jos palvelun vastaus muuttuu,
testi epäonnistuu ja kirjan tuloste päivitetään samalla
(`make paivita-naytokset`).

Esimerkkien avaaminen kehityskontissa on kuvattu taidossa
*Kehitysympäristöt ja Dev Containers*.

Varmentaja (`Varmentaja.java`) ja tokenit (`Tokenit.java`) ovat
opetustoteutuksia. Ne tekevät samat tarkistukset kuin tuotantotyökalut,
mutta tuotannossa käytetään valmiita: SPIRE, Vault, pilven
varmentajat ja avainpalvelut sekä JOSE-kirjastot.

## Uhkamalli

Tutoriaalin uhkamalli on palvelukokonaisuuksille tyypillinen:

- **Hyökkääjä on jo sisällä.** Yksi palvelu tai kehittäjän kone on
  murrettu, tai sisäverkkoon on päästy muuta kautta. Kysymys ei ole,
  pääseekö hyökkääjä sisään, vaan kuinka pitkälle se pääsee.
- **Salaisuudet vuotavat.** Lokit, muistivedokset, varmuuskopiot,
  CI-putket ja ympäristömuuttujat vuotavat ajan mittaan.
- **Virheitä tehdään.** Liian laaja oikeus, unohtunut testiavain tai
  väärin konfiguroitu yhdyskäytävä ovat yleisempiä kuin taitavat
  hyökkäykset.

Kaikki tutoriaalin mallit pyrkivät samaan: rajaamaan vahingon, joka
seuraa yhdestä murrosta, vuodosta tai virheestä.
