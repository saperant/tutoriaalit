# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Syötteen pituus on väite.** Tarkista se kohteen ja saadun datan
  todellista kokoa vasten.
- **Koko kulkee osoittimen mukana.** Rajapinta, joka ei kerro puskurin
  kokoa, on virhe.
- **Koon laskenta tarkistetaan** (`ckd_mul`, `calloc`), ja etumerkit
  pidetään erillään.
- **Data ei ole koodia.** Muotoilumerkkijono, komento, kysely ja lokin
  lauseke ovat aina vakioita, ja data annetaan argumenttina.
- **Omistajuus on selvä.** Jokaisella varauksella on yksi omistaja ja
  yksi vapautuspolku.
- **Sanitoijat testeihin, suojaukset julkaisuun.** ASan ja UBSan
  löytävät virheet, kanari, NX, ASLR, RELRO, FORTIFY ja CFI rajaavat
  niiden vaikutusta.
- **Jokainen jäsennin fuzzataan**, ja jokainen löydös on regressiotesti.
- **Korjaa juurisyy ja etsi variaatiot.**
- **Rajaa vaikutus**: vähimmät oikeudet, eristys ja avainten erottelu.
- **Ilmoita koordinoidusti**, ja tee omille käyttäjillesi helpoksi
  ilmoittaa sinulle.

## Muistiturvalliset kielet

Tämän paketin virheluokista suurin osa on mahdottomia kielissä, jotka
tarkistavat rajat ja hallitsevat elinajat: Rust, Go, Java, C#, Swift ja
monet muut. Esimerkiksi Rust estää käännösaikana käytön vapautuksen
jälkeen ja kaksoisvapautuksen ja tarkistaa indeksit ajossa. Uusi koodi,
joka käsittelee luottamatonta syötettä, kannattaa kirjoittaa
muistiturvallisella kielellä, ja vanhaa C- ja C++-koodia kannattaa
kääriä ja korvata vähitellen. Androidin ja Chromen kehittäjät ovat
raportoineet muistiturvallisuusvirheiden osuuden laskeneen, kun uusi koodi
on kirjoitettu muistiturvallisilla kielillä. Muistiturvallisuus ei
kuitenkaan poista logiikkavirheitä, injektioita eikä toimitusketjun
riskejä, kuten luku 10 näytti.

## Miten jatkaa laillisesti

Haavoittuvuuksien tutkimista oppii parhaiten tekemällä, ja tekemiseen
on olemassa ympäristöjä, joissa kohteet on rakennettu nimenomaan
harjoittelua varten ja testaaminen on luvallista sääntöjen puitteissa.
Lue jokaisen palvelun säännöt ennen aloittamista.

| Palvelu | Mitä tarjoaa | Osoite |
|---------|--------------|--------|
| picoCTF | aloittelijoille suunnattu CTF-kilpailu ja harjoituskirjasto (Carnegie Mellon) | `picoctf.org` |
| OverTheWire | komentorivipohjaiset harjoitussarjat, myös binääriharjoituksia | `overthewire.org` |
| pwn.college | yliopistotasoinen kurssimateriaali ja harjoitukset (Arizona State University) | `pwn.college` |
| Hack The Box | virtuaaliset harjoituskoneet ja haasteet | `hackthebox.com` |
| TryHackMe | ohjatut oppimispolut selaimessa | `tryhackme.com` |
| CTFtime | kansainvälisten CTF-kilpailujen kalenteri ja tulokset | `ctftime.org` |
| OWASP Juice Shop | tarkoituksella haavoittuva web-sovellus omalle koneelle | `owasp.org` |

*CTF* (*capture the flag*) on kilpailumuoto, jossa ratkaistaan
tietoturvatehtäviä, ja oikea vastaus on tehtävään piilotettu
merkkijono. Monet suomalaiset yliopistot, ammattikorkeakoulut ja
harrastajayhteisöt järjestävät omia kilpailujaan ja harjoitusiltojaan.

Oikeisiin järjestelmiin siirrytään vasta luvalla: bug bounty -ohjelman
säännöillä, työnantajan tai asiakkaan kirjallisella toimeksiannolla tai
omissa järjestelmissä. Omaa palvelinta, kotiverkkoa ja omia ohjelmia
kannattaa testata säännöllisesti, ja juuri siihen tämän paketin työkalut
on tarkoitettu.

## Jatkotaidot

*Tietoturva kehitystyössä* vie tämän paketin työkalut tiimin
prosessiin: staattinen analyysi ja fuzzaus CI:ssä, riippuvuudet ja
toimitusketju. *Sulautettujen järjestelmien tietoturva* ja
*Laiteohjelmiston takaisinmallinnus* käsittelevät samoja virheitä
laitteissa, joissa suojauksia on vähemmän. *Web-sovellusten
tietoturva* kattaa web-haavoittuvuudet ja *Virtualisointi* eristyksen,
jolla virheen vaikutus rajataan. Esitiedoista *Takaisinmallinnus*,
*Objektitiedostot, linkitys ja ABI*, *C-kieli* ja *Tietoturvan
perusteet* kannattaa kerrata tarpeen mukaan.

## Lähteet

Standardit ja ohjeet:

- ISO/IEC 9899:2024 (C23): otsake `<stdckdint.h>`.
- SEI CERT C Coding Standard. Carnegie Mellon University, Software
  Engineering Institute.
- MISRA C:2023. MISRA Consortium.
- OpenSSF: Compiler Options Hardening Guide for C and C++.
- FIRST: Common Vulnerability Scoring System v3.1 Specification ja
  CVSS v4.0 Specification.
- MITRE: Common Weakness Enumeration (CWE) ja CWE Top 25.
- RFC 9116: A File Format to Aid in Security Vulnerability Disclosure
  (2022).
- ISO/IEC 29147:2018 Vulnerability disclosure ja ISO/IEC 30111:2019
  Vulnerability handling processes.
- Euroopan parlamentin ja neuvoston asetus (EU) 2024/2847
  (kyberkestävyyssäädös).
- Rikoslaki (39/1889), 38. luku. Finlex.
- Traficom, Kyberturvallisuuskeskus: haavoittuvuuksien koordinointi.

Työkalut:

- Clang: AddressSanitizer, UndefinedBehaviorSanitizer, Control Flow
  Integrity ja libFuzzer -dokumentaatio (`clang.llvm.org`,
  `llvm.org/docs/LibFuzzer.html`).
- GCC: Static Analyzer (`-fanalyzer`) ja Instrumentation Options.
- AFL++: dokumentaatio (`aflplus.plus`).
- Google: fuzzing-opetusmateriaali ja OSS-Fuzz (`google.github.io/oss-fuzz`).
- clang-tidy: tarkistusluettelo (`clang.llvm.org/extra/clang-tidy`).

Tapaustutkimukset (luku 10):

- Spafford, E. H.: The Internet Worm Program: An Analysis. Purdue
  University, tekninen raportti CSD-TR-823, 1988.
- Eichin, M. W. ja Rochlis, J. A.: With Microscope and Tweezers: An
  Analysis of the Internet Virus of November 1988. IEEE Symposium on
  Security and Privacy, 1989.
- Debian Security Advisory DSA-1571-1: openssl – predictable random
  number generator, 2008; CVE-2008-0166.
- OpenSSL Security Advisory: TLS heartbeat read overrun
  (CVE-2014-0160), 7.4.2014; Codenomicon: The Heartbleed Bug
  (`heartbleed.com`).
- Apple: About the security content of iOS 7.0.6, 2014
  (CVE-2014-1266); Langley, A.: Apple's SSL/TLS bug. ImperialViolet,
  2014.
- Graham-Cumming, J.: Incident report on memory leak caused by
  Cloudflare parser bug. Cloudflare-blogi, 2017.
- Qualys Research Team: CVE-2021-3156: Heap-Based Buffer Overflow in
  Sudo (Baron Samedit), 2021.
- Freund, A.: backdoor in upstream xz/liblzma leading to ssh server
  compromise. oss-security-postituslista, 29.3.2024; CVE-2024-3094.
- Chazelas, S. ja GNU Bash: CVE-2014-6271 (Shellshock), 2014.
- Apache Logging Services: Log4j Security Vulnerabilities
  (CVE-2021-44228), 2021.

Kirjoja:

- Seacord, R. C.: Secure Coding in C and C++. 2. painos,
  Addison-Wesley, 2013.
- Dowd, M., McDonald, J. ja Schuh, J.: The Art of Software Security
  Assessment. Addison-Wesley, 2006.
- Zalewski, M.: The Tangled Web. No Starch Press, 2011.
