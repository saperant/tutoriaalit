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
haavoittuvuudet (injektiot, XSS, istunnot) ovat taidossa *Web-
sovellusten tietoturva*, eikä niitä toisteta.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Palveluarkkitehtuurit* (palvelujen jako,
synkroninen ja asynkroninen viestintä, yhdyskäytävä) ja *Kryptografia*
(TLS 1.3, varmenteet ja PKI, allekirjoitukset, AEAD). Myös
*Taustapalvelut* (Spring Boot ja Spring Security) ja *Tietoturvan
perusteet* (uhkamallinnus, pääsynhallinnan mallit, tiivisteketju
auditointilokissa) oletetaan.

Verkon segmentointi palomuureilla ja VLANeilla on taidossa
*Verkkoinfrastruktuuri* ja Kubernetesin perusteet taidossa *Kontit ja
pilvi*. Tässä keskitytään siihen, mitä palvelujen ja niiden
alustan pitää tehdä, jotta verkon sijainti ei ole luottamuksen peruste.

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

## Esimerkkiprojekti

`esimerkit/` on Maven-projekti (Java 21, Spring Boot 4.2), jossa on
viisi modulia. Neljä ensimmäistä käyttävät vain JDK:ta ja muutamaa
kirjastoa, jotta mekanismi näkyy. Viimeinen kokoaa saman Spring Boot
-palveluksi.

| Moduli | Luvut | Mitä näyttää |
|--------|-------|--------------|
| `luottamus` | 2–6, 10 | oma varmentaja, mTLS, kierto, palvelutokenit, tokenien vaihto, yhdyskäytävä |
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
