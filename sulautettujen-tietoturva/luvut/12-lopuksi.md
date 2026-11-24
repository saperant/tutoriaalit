# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Hyökkääjällä on laite käsissään.** Suunnittele sen mukaan, ja
   varmista, ettei yhden laitteen murto auta murtamaan muita.
2. **Ei yhteisiä salaisuuksia.** Laitekohtaiset avaimet,
   laitekohtaiset salasanat ja käyttötarkoituskohtaiset johdetut
   avaimet.
3. **Luottamusketju ROM:sta asti.** Ota piirin turvallinen käynnistys
   käyttöön, ja anna jokaisen vaiheen tarkistaa seuraava.
4. **Allekirjoitusavain HSM:ään**, kehitys- ja tuotantoavaimet
   erikseen, kumoaminen suunniteltuna.
5. **Monotoninen laskuri ja turvaversio** estävät haavoittuvan version
   palauttamisen. Nosta laskuri vasta vahvistuksen jälkeen.
6. **A/B-päivitys, manifesti ja kokeilukäynnistys.** Päivitys ei saa
   rikkoa laitetta sähkökatkossa eikä huonolla versiolla.
7. **Mittaa ja todenna**, jos palvelun pitää tietää, mitä laite ajaa.
8. **Lukitse debug ja konsoli tuotannossa**; huolto todennetulla
   debugilla.
9. **Vakioaikainen kryptografia valmiista kirjastosta.** Sivukanavat
   koskevat kaikkea salaisuudesta riippuvaa.
10. **Ei boolean-arvoja turvapäätöksissä.** Vakiot, oletusarvona
    hylkäys ja tuplatarkistus.
11. **Vaatimustenmukaisuus on prosessi.** SBOM, haavoittuvuuksien
    käsittely, ilmoitusvalmius ja tukiaika ennen ensimmäistä myyntiä.

## Mallit ja niiden käyttö

| Malli | Mihin | Luku |
|-------|-------|------|
| Luottamusketju | vain aito ohjelmisto käynnistyy | 3 |
| Tiiviste otsakkeessa, allekirjoitus otsakkeesta | lyhyt allekirjoitettava viesti, paloittainen tiivistys | 3 |
| Termometrilaskuri OTP:ssa | monotoninen laskuri ilman erillistä piiriä | 4 |
| Laajennettava rekisteri ja tapahtumaloki | mittauskäynnistys, etätodennus | 5 |
| Avaimen monipuolistus ja HKDF | laitekohtaiset ja käyttökohtaiset avaimet | 6 |
| Sumea poimija | avain kohinaisesta PUF-lukemasta | 6 |
| A/B ja kokeilukäynnistys | kestävä päivitys | 7 |
| Allekirjoitettu manifesti | päivityksen kohde, järjestys ja tiiviste ennen latausta | 7 |
| Haaste–vastaus-lupa | todennettu debug | 8 |
| Vakioaikainen vertailu, maskaus | sivukanavat | 9 |
| Kovennettu päätös | vikahyökkäykset | 10 |

## Jatkotaidot

- *Mikrokontrollerit ja bare-metal-ohjelmointi* ja *Sulautettu Linux*:
  laitteistotason perusta,
  jonka päälle tässä esitetyt mekanismit rakennetaan.
- *Laiteohjelmiston takaisinmallinnus*: sama aihe hyökkääjän
  näkökulmasta.
- *Reaaliaikakäyttöjärjestelmät* ja *Linux-laiteajurit*: tietoturva käyttöjärjestelmän ja
  ajurien tasolla.
- *Palveluarkkitehtuurin tietoturva*: laitteiden taustajärjestelmän
  identiteetit, salaisuudet ja käyttöoikeudet.

## Lähteet

Standardit ja säädökset:

- Euroopan parlamentin ja neuvoston asetus (EU) 2024/2847
  (kyberkestävyyssäädös). <https://eur-lex.europa.eu/eli/reg/2024/2847/oj>
- Komission delegoitu asetus (EU) 2022/30 (radiolaitedirektiivin
  tietoturvavaatimukset) ja standardit EN 18031-1, -2 ja -3.
- ETSI EN 303 645: *Cyber Security for Consumer Internet of Things:
  Baseline Requirements*. <https://www.etsi.org/>
- IEC 62443-4-1 ja IEC 62443-4-2. International Electrotechnical
  Commission.
- Traficomin Kyberturvallisuuskeskus: Kyberturvallisuusmerkki.
  <https://www.kyberturvallisuuskeskus.fi/>

Tekniset määrittelyt:

- RFC 8032: *Edwards-Curve Digital Signature Algorithm (EdDSA)*.
- RFC 9019 ja RFC 9124: *A Firmware Update Architecture for Internet of
  Things* ja *A Manifest Information Model for Firmware Updates in
  Internet of Things (IoT) Devices*.
- NIST SP 800-193: *Platform Firmware Resiliency Guidelines*.
- Trusted Computing Group: *TPM 2.0 Library Specification* ja *DICE
  Layering Architecture*. <https://trustedcomputinggroup.org/>
- Arm: *Platform Security Architecture* ja *Authenticated Debug
  Access Control Specification*.

Ohjelmistot ja dokumentaatio:

- MCUboot. <https://docs.mcuboot.com/>
- Trusted Firmware-M. <https://www.trustedfirmware.org/projects/tf-m/>
- Monocypher (BSD-2-Clause tai CC0). <https://monocypher.org/>
- ChipWhisperer (NewAE Technology), avoimet sivukanava- ja
  vikahyökkäystyökalut ja harjoitukset. <https://chipwhisperer.readthedocs.io/>

Kirjat ja artikkelit:

- Jasper van Woudenberg, Colin O'Flynn: *The Hardware Hacking
  Handbook*. No Starch Press, 2021.
- Paul Kocher: *Timing Attacks on Implementations of Diffie-Hellman,
  RSA, DSS, and Other Systems*. CRYPTO 1996.
- Paul Kocher, Joshua Jaffe, Benjamin Jun: *Differential Power
  Analysis*. CRYPTO 1999.
- Eric Brier, Christophe Clavier, Francis Olivier: *Correlation Power
  Analysis with a Leakage Model*. CHES 2004.
- Dan Boneh, Richard DeMillo, Richard Lipton: *On the Importance of
  Checking Cryptographic Protocols for Faults*. EUROCRYPT 1997.

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien mukana oleva
Monocypher-kirjasto on lisensoitu BSD-2-Clause- tai CC0-lisenssillä
(ks. `esimerkit/laite/ulkoiset/monocypher/LICENSE.txt`).
