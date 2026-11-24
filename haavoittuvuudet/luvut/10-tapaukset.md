# Tapaustutkimuksia

Edellisten lukujen virheet olivat pieniä ja tarkoituksellisia. Oikeissa
ohjelmissa samat virheet ovat johtaneet tietovuotoihin, joita ei voinut
perua, kalliisiin avainten vaihtoihin ja pysyviin mainehaittoihin. Tämä
luku käy läpi seitsemän vanhaa, korjattua ja hyvin dokumentoitua
tapausta. Jokaisessa toistuu sama rakenne: pieni, usein huomaamaton
oletus, joka ei pitänyt.

Kustakin tapauksesta kerrotaan tausta, virheellinen oletus, miten virhe
tuli esiin, mitä se mahdollisti, miten se korjattiin ja mitä siitä
seurasi. Tärkein osa on lopussa: **miten virhe olisi vältetty**, eli
mikä työkalu, prosessi tai suojaus olisi löytänyt sen ennen julkaisua
tai rajannut sen vaikutusta. Hyökkäysten yksityiskohtia ei käsitellä;
lähteet ovat luvussa 12.

## Morrisin mato (1988)

**Tausta.** Marraskuussa 1988 Cornellin yliopiston jatko-opiskelija
Robert T. Morris päästi internetiin itseään levittävän ohjelman. Se
levisi BSD-pohjaisiin VAX- ja Sun-koneisiin usealla tavalla: `fingerd`-
palvelun puskurin ylivuodolla, `sendmail`-ohjelman virheenjäljitystilalla
sekä koneiden välisillä luottamussuhteilla ja arvattavilla salasanoilla.

**Virheellinen oletus.** `fingerd` luki verkosta tulevan pyynnön
funktiolla `gets`, eli oletti, ettei pyyntö ole puskuria pidempi:

```{.c tiedosto="esimerkit/tapaukset/fingerd.c"}
```

**Miten tuli esiin.** Saastuneet koneet hidastuivat käyttökelvottomiksi,
koska mato tartutti samoja koneita yhä uudelleen. Yliopistojen
järjestelmänvalvojat analysoivat sen muutamassa päivässä; tunnetuimmat
analyysit ovat Eugene Spaffordin (Purdue) ja Mark Eichinin ja Jon
Rochlisin (MIT) raportit.

**Mitä mahdollisti.** Koodin suorituksen etäkoneella ilman tunnuksia.
Usein mainittu arvio on, että mato saastutti noin 6 000 konetta, mikä
oli merkittävä osa silloisesta internetistä.

**Korjaus.** `gets` korvattiin rajatulla luvulla, `sendmail`in
virheenjäljitystila suljettiin, ja salasanakäytäntöjä kiristettiin.

**Seuraukset.** Tapaus johti CERT/CC:n perustamiseen Carnegie Mellonin
yliopistoon samana vuonna. Morris tuomittiin Yhdysvaltain Computer Fraud
and Abuse Act -lain nojalla ensimmäisenä tämän lain mukaan
rikoksesta. `gets` poistettiin lopulta C-standardista vuonna 2011.

**Miten olisi vältetty.**

- *Rajapinta*: koon kertova luku (`fgets`) olisi estänyt ylivuodon
  kokonaan; tämän paketin luku 3 näyttää saman virheen.
- *Työkalut*: nykyiset kääntäjät ja linkkerit varoittavat `gets`-kutsusta,
  ja sanitoija tai fuzzeri löytäisi ylivuodon ensimmäisellä pitkällä
  syötteellä.
- *Prosessi*: virheenjäljitystoiminnot pois tuotantokokoonpanosta,
  oletuksena turvalliset asetukset.
- *Rajaus*: pinokanari ja NX, joita ei vielä ollut, olisivat tehneet
  ylivuodosta kaatumisen; vähimmät oikeudet ja koneiden väliset
  luottamussuhteet rajaavat leviämistä.

## Debianin OpenSSL-satunnaisuus (2006–2008)

**Tausta.** Debianin OpenSSL-paketin ylläpitäjä poisti vuonna 2006
kaksi riviä satunnaislukugeneraattorista, koska Valgrind ja Purify
varoittivat alustamattoman muistin käytöstä.

**Virheellinen oletus.** Että varoitus koski virhettä ja että rivit
olivat merkityksettömiä. Toinen poistetuista riveistä lisäsi
tarkoituksella alustamatonta puskuria satunnaisuusaltaaseen
(harmitonta), mutta toinen oli ainoa paikka, jossa *kaikki* lisätty
satunnaisuus päätyi altaaseen:

```{.c tiedosto="esimerkit/tapaukset/debian.c"}
```

**Miten tuli esiin.** Luciano Bello huomasi toukokuussa 2008, että
avaimia oli vain vähän erilaisia. Debian julkaisi tiedotteen DSA-1571
(CVE-2008-0166).

**Mitä mahdollisti.** Generaattorin ainoa vaihteleva syöte oli
prosessinumero, jolla oli enintään 32 768 arvoa. Debianilla ja
Ubuntulla kahden vuoden aikana luodut SSH-, OpenVPN- ja TLS-avaimet
olivat siksi ennustettavissa: mahdolliset avaimet voitiin luetella
etukäteen.

**Korjaus.** Rivi palautettiin. Lisäksi jakelut julkaisivat luettelot
heikoista avaimista ja työkalut niiden tunnistamiseen, ja kaikki
avaimet piti luoda uudelleen.

**Seuraukset.** Haitta ei rajautunut Debianiin, koska heikkoja avaimia
oli käytössä kaikkialla, minne niitä oli kopioitu. Tapauksesta tuli
esimerkki siitä, miksi jakelun omat muutokset kryptografiseen koodiin
on vietävä alkuperäisen projektin katselmoitaviksi.

**Miten olisi vältetty.**

- *Työkalut*: varoitus olisi pitänyt ymmärtää eikä vaientaa poistamalla
  koodia. Valgrindin vaiennustiedosto tai yhden harmittoman rivin
  poistaminen olisi riittänyt. Sama periaate kuin luvussa 2:
  varoitukset korjataan tai perustellaan.
- *Testit*: testi, joka luo kaksi avainta ja varmistaa, että ne
  eroavat (myös samalla prosessinumerolla), olisi kaatunut heti.
- *Prosessi*: kryptografian muutokset alkuperäisen projektin ja
  asiantuntijan katselmoitaviksi; jakelukohtaiset paikat minimiin.
- *Rajaus*: avainten säilytys laitteistossa tai ytimen satunnaislähteen
  (`getrandom`) käyttö oman altaan sijaan.

## Heartbleed (2014)

**Tausta.** OpenSSL toteutti TLS:n *heartbeat*-laajennuksen (RFC 6520),
jolla yhteyden osapuoli voi tarkistaa, onko toinen vielä paikalla:
pyyntö sisältää dataa ja sen pituuden, ja vastaus palauttaa saman
datan. Virheellinen koodi oli julkaistu OpenSSL 1.0.1:ssä vuonna 2012.

**Virheellinen oletus.** Että viestin ilmoittama pituus vastaa saapunutta
dataa. Vastaus kopioi ilmoitetun määrän tavuja, vaikka dataa olisi
ollut vähemmän, eli luki palvelimen muistia pyynnön ohi. Sama kuvio on
luvun 2 kehyksen purussa ja luvun 8 TLV-jäsentimessä.

**Miten tuli esiin.** Neel Mehta Googlelta ja Codenomiconin tutkijat
löysivät virheen toisistaan riippumatta. Se julkistettiin 7.4.2014
(CVE-2014-0160) samaan aikaan korjatun version 1.0.1g kanssa.
Codenomicon antoi virheelle nimen ja logon, ja siitä tuli yksi
ensimmäisistä laajasti brändätyistä haavoittuvuuksista.

**Mitä mahdollisti.** Kuka tahansa verkossa sai pyytää palvelimelta
toistuvasti kymmeniä kilotavuja muistia kerrallaan. Muistissa saattoi
olla yksityisiä avaimia, istuntoevästeitä ja salasanoja, eikä lukeminen
jättänyt jälkiä lokeihin.

**Korjaus.** Pituus tarkistetaan saapuneen tietueen todellista pituutta
vasten, ja virheellinen viesti hylätään hiljaa, kuten RFC 6520 vaatii:

```{.c tiedosto="esimerkit/tapaukset/heartbleed.c"}
```

**Seuraukset.** Ylläpitäjät ympäri maailman joutuivat päivittämään,
vaihtamaan yksityiset avaimet ja mitätöimään sertifikaatteja, koska
vuotoa ei voinut todeta jälkikäteen. Tapaus nosti esiin sen, että
kriittistä infrastruktuuria ylläpiti pieni, vähän rahoitettu joukko.
Linux Foundation perusti samana vuonna Core Infrastructure Initiativen
tukemaan tällaisia projekteja, OpenBSD haarautti LibreSSL:n ja Google
BoringSSL:n.

**Miten olisi vältetty.**

- *Työkalut*: kattavuusohjattu fuzzaus ASanin kanssa löytää virheen
  nopeasti; Googlen libFuzzer-opetusmateriaali käyttää Heartbleediä
  esimerkkinä juuri tästä. ASan ilmoittaa ylilukemisen
  (*heap-buffer-overflow*, READ) ensimmäisellä virheellisellä
  viestillä.
- *Rajatarkistus*: pituus tarkistetaan sekä kohteen että saadun datan
  kokoa vasten (luku 2).
- *Prosessi*: katselmointi protokollan jäsentimille, harvoin tarvittavat
  laajennukset pois oletuksena (pienempi hyökkäyspinta) ja riittävät
  resurssit kriittisille riippuvuuksille (*Turvallinen kehitys*).
- *Rajaus*: yksityisen avaimen erottaminen eri prosessiin tai
  laitteistomoduuliin olisi estänyt avainten vuodon; ASLR ja NX eivät
  auta pelkkää lukua vastaan.

## Applen "goto fail" (2014)

**Tausta.** Applen TLS-kirjasto SecureTransport tarkisti palvelimen
avaintenvaihtoviestin allekirjoituksen funktiossa
`SSLVerifySignedServerKeyExchange`. Virhe korjattiin iOS 7.0.6:ssa ja
OS X 10.9.2:ssa helmikuussa 2014 (CVE-2014-1266).

**Virheellinen oletus.** Että sisennys kertoo, mikä kuuluu `if`-lauseeseen.
Rivi `goto fail;` oli kahdesti peräkkäin, ja toinen suoritettiin aina:

```{.c tiedosto="esimerkit/tapaukset/gotofail.c"}
```

Koska `err` oli tuolloin nolla, funktio palasi "onnistuneena" ja
allekirjoituksen tarkistus jäi tekemättä.

**Miten tuli esiin.** Apple julkaisi korjauksen ilman yksityiskohtia, ja
Adam Langley (Google) julkaisi analyysin seuraavana päivänä korjauksen
lähdekoodin perusteella.

**Mitä mahdollisti.** Samassa verkossa oleva hyökkääjä, esimerkiksi
julkisessa langattomassa verkossa, pystyi esiintymään mitä tahansa
palvelinta vastaan TLS-yhteyksissä, jotka käyttivät
Diffie–Hellman-avaintenvaihtoa: salaus ei suojannut välistäkuuntelulta.

**Korjaus.** Ylimääräinen rivi poistettiin.

**Seuraukset.** Tapaus kiihdytti keskustelua pakollisista aaltosulkeista
ja automaattisesta muotoilusta, ja siitä tuli opetusesimerkki
virhepolkujen testaamisesta.

**Miten olisi vältetty.**

- *Kääntäjä*: Clangin `-Wunreachable-code` olisi varoittanut, että
  tarkistus ei ole saavutettavissa; GCC 6:n `-Wmisleading-indentation`
  (vuodesta 2016 osa `-Wall`-valitsinta) tunnistaa juuri tämän kuvion.
- *Tyyli ja muotoilu*: pakolliset aaltosulkeet (CERT EXP19-C, MISRA C)
  ja automaattinen muotoilija (`clang-format`) olisivat tehneet virheen
  näkyväksi.
- *Testit*: yksikin testi väärällä allekirjoituksella olisi epäonnistunut.
  Rivikattavuus olisi näyttänyt, ettei tarkistusta koskaan suoritettu.
- *Prosessi*: koodikatselmointi kahdella hyväksyjällä, koska
  muutos näkyi diffissä selvästi.

## Cloudbleed (2017)

**Tausta.** Cloudflare käsitteli asiakkaidensa HTML-sivuja
reunapalvelimillaan jäsentimellä, jonka koodi tuotettiin Ragel-
työkalulla. Kun yhtiö otti käyttöön uuden jäsentimen, vanhan
jäsentimen piilevä virhe alkoi vaikuttaa.

**Virheellinen oletus.** Että osoitin osuu puskurin loppuun tasan.
Lopun tarkistus käytti yhtäsuuruutta, ja tietyssä virheellisessä
HTML:ssä osoitin hyppäsi lopun yli:

```{.c tiedosto="esimerkit/tapaukset/cloudbleed.c"}
```

**Miten tuli esiin.** Tavis Ormandy (Google Project Zero) huomasi
helmikuussa 2017 oman tutkimusprojektinsa aineistossa Cloudflaren kautta
palveltuja vastauksia, joissa oli muiden käyttäjien dataa, ja otti
yhteyttä Cloudflareen. Cloudflare poisti vuotoa aiheuttaneet
ominaisuudet käytöstä alle tunnissa, korjasi virheen saman päivän aikana
ja julkaisi yksityiskohtaisen tapahtumaraportin.

**Mitä mahdollisti.** Jäsennin luki puskurin yli ja kirjoitti
vastaukseen palvelimen muistia: muiden asiakkaiden HTTP-otsakkeita,
evästeitä ja todennustunnisteita. Osa vuotaneesta datasta oli ehtinyt
hakukoneiden välimuisteihin.

**Korjaus.** Tarkistus muutettiin muotoon "lopussa tai sen yli", ja
virheellisen HTML:n polku korjattiin. Cloudflare teki hakukoneiden kanssa
töitä välimuistien tyhjentämiseksi.

**Seuraukset.** Mainehaitta ja asiakkaiden epävarmuus siitä, mitä oli
vuotanut. Tapaus osoitti, että yhden palvelun muistivirhe voi vuotaa
kymmenien tuhansien eri asiakkaiden dataa, koska ne jakavat saman
prosessin.

**Miten olisi vältetty.**

- *Työkalut*: jäsentimen fuzzaus ASanilla olisi löytänyt ylilukemisen;
  generoitu koodi on testattava kuten käsin kirjoitettu.
- *Puolustava ohjelmointi*: lopun tarkistus aina muodossa `>=` (tai
  pituuslaskurilla), jotta yli meneminen pysähtyy.
- *Prosessi*: uuden komponentin vaiheittainen käyttöönotto ja
  tarkkailu (anomaliat vastausten koossa).
- *Rajaus*: eri asiakkaiden datan eristäminen eri prosesseihin tai
  muistialueisiin.

## Baron Samedit, sudo (2021)

**Tausta.** `sudo` on setuid-ohjelma: se käynnistyy pääkäyttäjän
oikeuksin kenen tahansa ajamana ja päättää sitten, mitä käyttäjä saa
tehdä. Virhe oli sudon versioissa 1.8.2–1.9.5p1, eli lähes kymmenen
vuoden ajan.

**Virheellinen oletus.** Argumenttien kopiointi oletti, että kenoviivaa
seuraa aina jokin merkki. Kun argumentti päättyi kenoviivaan, kopiointi
ohitti loppunollan ja jatkoi seuraavaan argumenttiin, eli kirjoitti
kekopuskurin yli:

```{.c tiedosto="esimerkit/tapaukset/samedit.c"}
```

**Miten tuli esiin.** Qualysin tutkimusryhmä löysi virheen koodia
tarkastamalla, ilmoitti siitä sudon ylläpitäjälle ja jakeluille
koordinoidusti, ja virhe julkistettiin tammikuussa 2021 (CVE-2021-3156)
korjatun version 1.9.5p2 kanssa.

**Mitä mahdollisti.** Kuka tahansa paikallinen käyttäjä, myös ilman
oikeutta käyttää `sudo`a, sai pääkäyttäjän oikeudet useimpien
jakeluiden oletusasennuksissa.

**Korjaus.** Kopiointi tarkistaa, että kenoviivaa seuraa merkki, ja
ohjelma tarkistaa johdonmukaisesti, missä tilassa argumentit
tulkitaan.

**Seuraukset.** Kaikki Linux- ja Unix-järjestelmät, joissa oli sudo,
piti päivittää. Tapaus vauhditti keskustelua setuid-ohjelmien
riskeistä, ja sudolle on sittemmin kehitetty muistiturvallinen
uudelleentoteutus, sudo-rs.

**Miten olisi vältetty.**

- *Työkalut*: argumenttien jäsennin kohdefunktioksi ja fuzzaus ASanilla
  (luku 8); rajatapausten testit (tyhjä argumentti, pelkkä kenoviiva).
- *Kieli*: muistiturvallinen kieli tai merkkijonokirjasto, joka
  tarkistaa rajat, poistaa koko virheluokan.
- *Prosessi*: setuid-ohjelmien koodi on kriittisin hyökkäyspinta ja
  ansaitsee erityiskatselmoinnin ja jatkuvan fuzzauksen.
- *Rajaus*: setuid-ohjelmien määrän vähentäminen ja oikeuksien
  pudottaminen mahdollisimman aikaisin.

## xz-utilsin takaovi (2024)

**Tausta.** xz ja sen kirjasto liblzma ovat laajasti käytetty
pakkausohjelmisto, jota ylläpiti pitkään yksi henkilö, suomalainen
Lasse Collin. Vuodesta 2021 alkaen nimimerkki "Jia Tan" osallistui
projektiin, sai vähitellen luottamusta ja lopulta ylläpito-oikeudet,
samalla kun muut nimimerkit painostivat ylläpitäjää ottamaan apua
vastaan.

**Virheellinen oletus.** Että julkaisupaketti vastaa versionhallinnan
sisältöä ja että pitkäaikainen avustaja on se, miltä näyttää.
Versioiden 5.6.0 ja 5.6.1 julkaisupaketeissa oli muokattu
käännösskripti, jota versionhallinnassa ei ollut, ja haitallinen koodi
oli piilotettu binäärisiin testitiedostoihin. Kun kirjasto käännettiin
tietyissä jakeluissa, se muutti OpenSSH-palvelimen todennukseen
liittyvää funktiota. Yhteys syntyi siksi, että jotkin jakelut linkittivät
`sshd`:n libsystemd-kirjastoon, joka puolestaan käytti liblzmaa.

**Miten tuli esiin.** Andres Freund, PostgreSQL-kehittäjä Microsoftilla,
huomasi maaliskuussa 2024 suorituskykymittauksissa, että
SSH-kirjautumiset kuluttivat odottamattoman paljon prosessoriaikaa ja
että Valgrind ilmoitti virheistä. Hän selvitti syyn takaisinmallintamalla
ja julkaisi löydöksen oss-security-postituslistalla 29.3.2024
(CVE-2024-3094).

**Mitä mahdollisti.** Takaovi oli tarkoitettu antamaan tietyn avaimen
haltijalle pääsy koodin suoritukseen palvelimilla, joiden `sshd` latasi
haitallisen kirjaston. Muutos ehti testi- ja kehitysjakeluihin (esim.
Debianin unstable- ja testing-haarat ja Fedoran kehitysversiot) mutta
ei juuri lainkaan vakaisiin julkaisuihin.

**Korjaus.** Haitalliset versiot poistettiin ja jakelut palasivat
aiempaan versioon; projektin ylläpito järjestettiin uudelleen.

**Seuraukset.** Tapaus on avoimen lähdekoodin toimitusketjun tunnetuin
esimerkki: hyökkäys kohdistui ihmisiin ja julkaisuprosessiin eikä
ohjelmointivirheeseen. Se lisäsi huomiota ylläpitäjien kuormitukseen,
toistettaviin käännöksiin ja tarpeettomien riippuvuuksien karsimiseen
(esimerkiksi systemd siirtyi lataamaan pakkauskirjastot vasta tarvittaessa).

**Miten olisi vältetty.**

- *Prosessi*: julkaisupaketin ja versionhallinnan vertailu automaattisesti;
  toistettavat käännökset (*reproducible builds*) suoraan
  versionhallinnasta; binääristen testitiedostojen alkuperän tarkistus;
  ylläpitäjien resursointi ja useampi ylläpitäjä
  (*Turvallinen kehitys*: toimitusketju, SBOM ja SLSA).
- *Riippuvuudet*: jokainen linkitetty kirjasto kasvattaa luotettavaa
  koodia; kevyt rajapinta (esim. palveluilmoitus ilman koko libsystemd:tä)
  olisi poistanut yhteyden.
- *Havaitseminen*: suorituskykyseuranta ja poikkeamien selvittäminen
  takaisinmallintamalla; juuri ne löysivät tämän.
- *Rajaus*: `sshd`:n oikeuksien erottelu ja hiekkalaatikointi rajaavat,
  mitä palvelimen sisällä suoritettu koodi voi tehdä.

## Muita opettavaisia tapauksia

- **Shellshock (2014, CVE-2014-6271).** Bash suoritti
  ympäristömuuttujaan tallennetun funktiomäärittelyn perässä olevan
  tekstin komentoina. Periaate on sama kuin muotoilumerkkijonovirheessä:
  data tulkittiin koodina. Michał Zalewski löysi ensimmäisen korjauksen
  jälkeen lisää virheitä fuzzaamalla Bashin jäsennintä AFL:llä.
- **Log4Shell (2021, CVE-2021-44228).** Javan lokikirjasto Log4j 2
  tulkitsi lokiviestissä olevat erikoislausekkeet ja saattoi niiden
  perusteella hakea ja ladata koodia verkosta. Lokiin kirjattu
  käyttäjän syöte muuttui ohjeiksi. Tapaus osoitti myös, miten vaikeaa
  on tietää, missä kaikkialla jokin kirjasto on käytössä, eli miksi
  ohjelmistoluettelo (SBOM) on tarpeen.

## Yhteenveto

| Tapaus | Virheellinen oletus | Työkalu | Prosessi | Rajaus |
|------------|------------------|-------------------|------------------|----------------|
| Morrisin mato | syöte mahtuu puskuriin | rajattu rajapinta, fuzzaus | turvalliset oletusasetukset | kanari, NX, vähimmät oikeudet |
| Debian OpenSSL | varoitus on virhe | testi avainten erilaisuudesta | muutokset alkuperäiseen projektiin | avaimet laitteistossa |
| Heartbleed | ilmoitettu pituus on oikea | fuzzaus ja ASan | jäsentimien katselmointi, resursointi | avain eri prosessissa |
| goto fail | sisennys kertoo rakenteen | varoitukset kuolleesta koodista ja sisennyksestä | aaltosulkeet, virhepolkujen testit | – |
| Cloudbleed | osoitin osuu loppuun tasan | fuzzaus ja ASan | vaiheittainen käyttöönotto | asiakkaiden eristys |
| Baron Samedit | kenoviivaa seuraa merkki | fuzzaus ja ASan, muistiturvallinen kieli | setuid-koodin katselmointi | vähemmän setuid-ohjelmia |
| xz-utils | julkaisu vastaa lähdekoodia | toistettava käännös, suorituskykyseuranta | toimitusketjun valvonta, ylläpitäjien tuki | oikeuksien erottelu |

Taulukosta näkyy kaksi asiaa. Ensinnäkin muistivirheissä sama
yhdistelmä toistuu: rajatarkistus, fuzzaus ja sanitoijat (luvut 2, 8
ja 9) olisivat löytäneet useimmat ennen julkaisua. Toiseksi suurimmat
vahingot syntyivät tapauksissa, joissa virhe ei ollut yksittäinen
koodirivi vaan oletus prosessista: kuka katselmoi, mitä testataan ja
mihin luotetaan. Ne korjataan kehitystavoilla, joita *Turvallinen
kehitys* käsittelee.

## Käytännössä

- **Etsi oletus, ei vain virhettä.** Jokaisessa tapauksessa korjattu
  rivi oli pieni; oletus sen takana oli laaja ja toistui muualla.
- **Testaa virhepolut ja virheelliset syötteet**, ei vain toimivia
  tapauksia: goto fail ja Debian olisivat jääneet kiinni yhdellä
  negatiivisella testillä.
- **Fuzzaa jäsentimet sanitoijien kanssa**, myös generoidut ja vanhat.
- **Valvo toimitusketjua**: julkaisu vastaa lähdekoodia, riippuvuuksia
  on vähän ja jokaisella kriittisellä projektilla on riittävästi
  ylläpitäjiä.
- **Rajaa vaikutus**: avaimet eri prosessiin, vähimmät oikeudet ja
  eristys, koska kaikkia virheitä ei löydetä ajoissa.

## Itsearviointi

- Osaat kuvata Heartbleedin, goto failin ja xz-takaoven virheellisen
  oletuksen ja vaikutuksen yleisellä tasolla.
- Osaat nimetä kullekin tapaukselle työkalun, prosessin ja suojauksen,
  joka olisi estänyt sen tai rajannut sen vaikutusta.
- Osaat yhdistää tapausten virhekuviot tämän paketin omiin esimerkkeihin
  (pituuskenttä, rajapinta, muotoilu).
- Osaat perustella, miksi toimitusketjun ja kehitysprosessin oletukset
  ovat yhtä tärkeitä kuin yksittäisten koodirivien virheet.
