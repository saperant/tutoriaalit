# Käsitteet ja periaatteet

## Mitä suojataan: CIA

Tietoturvan tavoitteet kuvataan perinteisesti kolmella ominaisuudella
(englanniksi *CIA triad*):

| Ominaisuus | Tarkoittaa | Esimerkki rikkoutumisesta |
|------------|-----------|---------------------------|
| **Luottamuksellisuus** (*confidentiality*) | tieto vain niille, joille se kuuluu | asiakasrekisteri vuotaa |
| **Eheys** (*integrity*) | tieto ja järjestelmä muuttuvat vain sallitusti | hyökkääjä muuttaa tilisiirron summaa |
| **Saatavuus** (*availability*) | palvelu toimii, kun sitä tarvitaan | palvelunestohyökkäys kaataa kaupan |

Usein lisätään **aitous** (*authenticity*: viesti on todella siltä,
jolta se väittää olevansa) ja **kiistämättömyys** (*non-repudiation*:
tekijä ei voi jälkikäteen kiistää tekoaan). Ominaisuudet voivat olla
ristiriidassa: varmuuskopiot parantavat saatavuutta mutta lisäävät
paikkoja, joista tieto voi vuotaa.

## Uhka, haavoittuvuus ja riski

Termit sekoitetaan usein, vaikka ne tarkoittavat eri asioita:

- **Suojattava kohde** (*asset*) on se, millä on arvoa: data, palvelu,
  maine, laitteet.
- **Uhka** (*threat*) on mahdollinen haitallinen tapahtuma ja sen
  aiheuttaja: rikollinen, joka haluaa asiakasrekisterin, tai sisäpiiriläinen
  vahingossa.
- **Haavoittuvuus** (*vulnerability*) on heikkous, jonka kautta uhka
  voi toteutua: SQL-injektio, oletussalasana, puuttuva päivitys.
- **Hyökkäys** (*attack*, *exploit*) on haavoittuvuuden hyödyntäminen.
- **Riski** (*risk*) on uhan toteutumisen todennäköisyys kertaa
  vaikutus. Riskiä hallitaan **suojauksilla** (*control*).

Haavoittuvuus ilman uhkaa on pieni riski, ja vakava uhka ilman
haavoittuvuutta samoin. Riskin arviointi (luku *Uhkamallinnus*) yhdistää
nämä, jotta rajallinen aika käytetään tärkeimpiin korjauksiin.

**Hyökkäyspinta** (*attack surface*) on kaikkien niiden kohtien
summa, joista hyökkääjä voi syöttää dataa tai vaikuttaa
järjestelmään: verkkorajapinnat, lomakkeet, tiedostojen lataus,
ylläpitoliittymät, riippuvuudet, työntekijät. Jokainen poistettu
ominaisuus ja suljettu portti pienentää sitä.

## Ihminen hyökkäyksen kohteena

Hyökkäyspintaan kuuluvat myös ihmiset. **Käyttäjän manipulointi**
(*social engineering*) tarkoittaa, että hyökkääjä saa ihmisen tekemään
jotain hyökkääjän puolesta: kertomaan salasanan, hyväksymään
kirjautumisen tai maksamaan laskun. Tavallisimmat muodot ovat

- **tietojenkalastelu** (*phishing*): viesti, joka ohjaa väärennetylle
  kirjautumissivulle tai saa avaamaan haitallisen liitteen,
- **kohdennettu kalastelu** (*spear phishing*): sama, mutta viesti on
  räätälöity vastaanottajalle julkisista tiedoista,
- **tekosyy** (*pretexting*): soittaja esiintyy tukihenkilönä,
  esihenkilönä tai toimittajana ja pyytää poikkeusta käytäntöön.

Keinot toimivat, koska ne vetoavat kiireeseen, auktoriteettiin ja
auttamisenhaluun, eivät siksi, että kohde olisi huolimaton. Siksi
torjunta ei voi nojata pelkkään valppauteen. Kestävät suojaukset ovat
teknisiä ja prosessiin rakennettuja: kalastelua kestävä tunnistus (luku
*Todennus*), kahden henkilön hyväksyntä maksuille ja oikeuksien
muutoksille, tunnistetun kanavan käyttö takaisinsoittoon sekä
ilmoituskanava, jonka käytöstä ei seuraa syyllistämistä. Koulutus
auttaa tunnistamaan yritykset, mutta järjestelmä suunnitellaan niin,
että yhden ihmisen erehdys ei riitä murtoon.

## Suunnitteluperiaatteet

Saltzer ja Schroeder kokosivat vuonna 1975 periaatteet, jotka ovat
edelleen tietoturvallisen suunnittelun perusta. Tärkeimmät:

| Periaate | Käytännössä |
|----------|-------------|
| **Vähimmät oikeudet** (*least privilege*) | prosessi, käyttäjä ja palvelu saavat vain tehtävään tarvittavat oikeudet |
| **Turvallinen oletus** (*fail-safe defaults*) | pääsy on kielletty, ellei sitä ole erikseen sallittu; virhe johtaa kieltoon |
| **Täydellinen välitys** (*complete mediation*) | jokainen pääsy tarkistetaan joka kerta, ei vain ensimmäisellä kerralla |
| **Mekanismin yksinkertaisuus** (*economy of mechanism*) | yksinkertaisen tarkistuksen voi todeta oikeaksi |
| **Avoin suunnittelu** (*open design*) | turvallisuus ei perustu siihen, että menetelmä on salainen; vain avaimet ovat salaisia |
| **Oikeuksien erottelu** (*separation of privilege*) | kriittinen toiminto vaatii kaksi ehtoa, esim. salasanan ja laitteen |
| **Psykologinen hyväksyttävyys** | turvallinen tapa on helpoin tapa, muuten käyttäjät kiertävät sen |

Avoimen suunnittelun periaate tunnetaan myös Kerckhoffsin
periaatteena: salausjärjestelmän on oltava turvallinen, vaikka kaikki
muu kuin avain on julkista. Sen vastakohta, *security through
obscurity*, pettää viimeistään, kun lähdekoodi tai laite päätyy
hyökkääjälle.

## Turvallinen oletus koodissa

Turvallisen oletuksen rikkominen on yleinen virhe, koska se näyttää
viattomalta. Alla tarkistus palauttaa luvan, kun käyttäjää ei löydy:

```{.python tiedosto="esimerkit/02-oletus.py" osa="avoin"}
```

Korjatussa versiossa lupa myönnetään vain, kun kaikki ehdot täyttyvät
nimenomaisesti. Kaikki muu, myös odottamaton tilanne, johtaa kieltoon:

```{.python tiedosto="esimerkit/02-oletus.py" osa="suljettu"}
```

```{.tuloste tiedosto="esimerkit/02-oletus.odotettu"}
```

Huomaa myös vertailun suunta: avoin versio kysyy "onko rooli jokin muu
kuin tavallinen käyttäjä", korjattu "onko rooli ylläpitäjä". Jos joku
myöhemmin lisää roolin `vieras`, ensimmäinen versio antaa sille
poisto-oikeuden.

## Puolustus syvyyssuunnassa

Yksittäinen suojaus pettää ennemmin tai myöhemmin: ohjelmassa on
virhe, ylläpitäjä erehtyy tai salasana vuotaa. **Puolustus
syvyyssuunnassa** (*defense in depth*) tarkoittaa, että suojauksia on
useassa kerroksessa ja ne ovat toisistaan riippumattomia. Esimerkiksi
verkkokaupan asiakastietoja suojaavat

1. palomuuri, joka päästää tietokantaan vain sovelluspalvelimen,
2. sovelluksen parametrisoidut kyselyt (ei SQL-injektiota),
3. tietokantatunnus, jolla on vain tarvittavat oikeudet,
4. levyn ja varmuuskopioiden salaus,
5. lokit ja hälytykset, jotka paljastavat poikkeavan tiedonsiirron.

Kun yksi kerros pettää, seuraava rajaa vahinkoa. Kerrokset ovat
arvokkaita vain, jos ne ovat todella riippumattomia: kaksi suojausta,
jotka käyttävät samaa salasanaa, ovat yksi suojaus.

## Käytännössä

- **Ajattele hyökkääjänä.** Kysy jokaisesta syötteestä, mitä pahin
  mahdollinen arvo tekee. Testaa myös tyhjä, valtava, negatiivinen ja
  erikoismerkkejä sisältävä syöte.
- **Kiellä oletuksena.** Sallittujen lista (*allowlist*) on turvallisempi
  kuin kiellettyjen lista (*denylist*), koska unohtunut tapaus johtaa
  kieltoon eikä pääsyyn.
- **Virhetilanne ei ole lupa.** Jos tarkistusta ei voi tehdä
  (tietokanta ei vastaa, käyttäjää ei löydy), vastaus on kielto.
- **Pienennä hyökkäyspintaa.** Poista käyttämättömät ominaisuudet,
  portit, tunnukset ja riippuvuudet. Koodi, jota ei ole, ei voi olla
  haavoittuva.
- **Älä luota salassapitoon.** Oleta, että hyökkääjä tuntee
  järjestelmän rakenteen ja lähdekoodin. Vain avaimet ja salasanat ovat
  salaisia.
- **Rakenna kerroksia.** Älä luota siihen, että ulompi kerros, kuten
  palomuuri tai kirjautuminen, pysäyttää kaiken.

## Itsearviointi

- Osaat selittää luottamuksellisuuden, eheyden ja saatavuuden erot
  esimerkein.
- Osaat erottaa uhan, haavoittuvuuden ja riskin toisistaan.
- Osaat nimetä käyttäjän manipuloinnin tavallisimmat muodot ja
  suojaukset, jotka eivät nojaa yksittäisen ihmisen valppauteen.
- Osaat tunnistaa koodista tarkistuksen, joka epäonnistuu avoimeksi, ja
  korjata sen.
- Osaat suunnitella palvelulle toisistaan riippumattomia
  suojauskerroksia.
