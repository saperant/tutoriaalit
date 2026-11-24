# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

| Tilanne | Muista |
|---------|--------|
| teho ja vaimennus | laske desibeleinä; +3 dB = kaksinkertainen teho, +10 dB = kymmenkertainen |
| kaapeli | vaimennus kasvaa taajuuden ja pituuden mukana; kierretty pari 100 m |
| kuitu | vaimennusbudjetti ja dispersio; jätä 3 dB varaa |
| radio | +6 dB vaimennusta, kun etäisyys kaksinkertaistuu; varaa häipymälle |
| kapasiteetti | $C = B \log_2(1 + S/N)$; kaista kasvattaa enemmän kuin teho |
| kohinataso | $-174$ dBm/Hz $+ 10\log_{10} B +$ kohinaluku |
| linjakoodi | erota bitti- ja symbolinopeus; koodin hinta 3–25 % |
| virheet | CRC havaitsee, FEC korjaa, lomitus hajottaa purskeet |
| multipleksointi | ortogonaalisuus erottaa; etuliite ja suojakaista maksavat |
| viive | siirto + eteneminen + jono + käsittely; matka ei lyhene kaistalla |
| ikkuna | vähintään kaistan ja kierrosajan tulo |
| satunnaispääsy | ALOHA enintään 18–37 %; perääntyminen satunnaisesti ja kasvavasti |
| Ethernet | mitoita kehyksinä sekunnissa; anna päiden neuvotella |
| solut | uudelleenkäyttö vaihtaa reunan laadun keskikapasiteettiin |
| jonot | viive $\propto 1/(1-\rho)$; Littlen laki $L = \lambda W$ |
| QoS | priorisoi vähän ja rajattua; rajoita reunalla |

## Jatkotaidot taitopuussa

- *Digitaalinen tiedonsiirto* syventää modulaatiot, pulssinmuokkauksen,
  synkronoinnin ja kanavakoodauksen, ja *Ohjelmistoradio* toteuttaa ne
  oikealla radiolaitteella.
- *Verkkoinfrastruktuuri* soveltaa tämän tutoriaalin linkkitason
  tietämystä lähiverkkojen, langattomien verkkojen ja palvelun laadun
  suunnitteluun.
- *Verkko-ohjelmointi* ja *Hajautetut järjestelmät* rakentavat
  sovelluksia, joiden on siedettävä tässä mitattua viivettä, häviöitä
  ja kapasiteetin vaihtelua.
- *Skaalautuvien järjestelmien suunnittelu* käyttää jonoteoriaa ja
  Littlen lakia palveluiden mitoitukseen.

## Lähteet ja lisälukemista

- Larry Peterson ja Bruce Davie: *Computer Networks: A Systems
  Approach*. Avoin oppikirja (CC BY 4.0),
  <https://book.systemsapproach.org/>. Erityisesti luvut suorista
  linkeistä ja suorituskyvystä.
- Wikibooks: *Communication Systems* ja *Data Coding Theory*
  (CC BY-SA), <https://en.wikibooks.org/wiki/Communication_Systems>.
- Claude E. Shannon: A Mathematical Theory of Communication. *Bell
  System Technical Journal* 27 (1948).
- Norman Abramson: The ALOHA System – Another Alternative for Computer
  Communications. *AFIPS Fall Joint Computer Conference* (1970).
- Robert Metcalfe ja David Boggs: Ethernet: Distributed Packet Switching
  for Local Computer Networks. *Communications of the ACM* 19(7) (1976).
- Leonard Kleinrock: *Queueing Systems, Volume 1: Theory*. Wiley, 1975.
- IEEE 802.3 Ethernet -standardi. Saatavilla maksutta IEEE GET
  -ohjelman kautta, <https://ieeexplore.ieee.org/browse/standards/get-program/page>.
- 3GPP TS 38.211 (fyysiset kanavat ja numerologia), TS 38.101-1
  (kaistat ja resurssilohkot) ja TS 38.306 (päätelaitteen
  ominaisuudet ja huippunopeuden kaava), <https://www.3gpp.org/>.
- ITU-T G.652: yksimuotokuidun ominaisuudet,
  <https://www.itu.int/rec/T-REC-G.652>.
- RFC 2475 (DiffServ-arkkitehtuuri), RFC 2697 (rahakkeen ämpäriin
  perustuva merkitsijä), RFC 4594 (DiffServ-luokkien suositukset) ja
  RFC 8289 (CoDel), <https://www.rfc-editor.org/>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Standardien ja artikkelien sisältöä ei ole kopioitu; niihin viitataan
lähteinä.
