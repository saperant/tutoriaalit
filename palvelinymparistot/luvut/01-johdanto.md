# Johdanto {.runko-johdanto}

Palvelinympäristö on kokonaisuus, jonka päällä palvelut toimivat:
laitteisto, tallennus, varmuuskopiot, käyttäjähallinta, asetusten
hallinta, valvonta ja raha. Sovelluskehittäjä näkee siitä usein vain
rajapinnan, esimerkiksi virtuaalikoneen tai Kubernetes-klusterin. Joku
kuitenkin päättää, montako levyä saa hajota, kuinka vanha varmuuskopio
riittää ja paljonko kapasiteettia ostetaan ensi vuodeksi. Tämä
tutoriaali opettaa nuo päätökset ja niiden taustalla olevat laskelmat.

Painopiste on periaatteissa, jotka pysyvät, vaikka tuotteet vaihtuvat.
RAID-tason vikasietoisuus, varmuuskopion palautusaika ja
virhebudjetti lasketaan samoin omassa konesalissa ja pilvessä. Siksi
esimerkit ovat laskelmia ja pieniä työkaluja, joita voi käyttää
sellaisenaan: tarkistus, joka lukee muistivirhelaskurit, säilytyssääntö,
joka päättää poistettavat kopiot, tai tarkastus, joka arvioi palvelimen
koventamisen.

## Mitä tutoriaali kattaa

| Luku | Kysymys, johon luku vastaa |
|------|----------------------------|
| Palvelinlaitteisto | Mikä tekee palvelimesta palvelimen, ja miten sen kuntoa valvotaan? |
| Tallennus ja RAID | Montako levyä saa hajota, ja kuinka riskialtis uudelleenrakennus on? |
| Tiedostojärjestelmät ja tarkistussummat | Miten hiljainen korruptoituminen havaitaan? |
| Varmuuskopiointi | Riittääkö kopiointi palvelun RPO- ja RTO-tavoitteisiin? |
| Käyttäjähallinta | Miten sadat koneet tunnistavat samat käyttäjät? |
| Konfiguraationhallinta | Miten sadat koneet pidetään samassa, tunnetussa tilassa? |
| Koventaminen ja päivitykset | Miten hyökkäyspinta pienennetään ja pidetään pienenä? |
| Alustat ja klusterit | Kestääkö klusteri yhden koneen vian tai huoltokatkon? |
| Valvonta ja palvelutasot | Milloin päivystäjä herätetään? |
| Kustannukset ja kapasiteetti | Mitä palvelu maksaa, ja milloin tila loppuu? |

Esitiedoiksi oletetaan Linuxin käyttö komentoriviltä, verkkojen
perusteet ja taito *Verkkoinfrastruktuuri* (palomuurit, VLANit,
hallintaverkko) sekä taito *Kontit ja pilvi* (Docker ja Kubernetes).
Niitä ei toisteta tässä.

## Kenen työtä palvelinympäristö on

Perinteisesti palvelimista huolehti ylläpito (system administration).
Nykyään sama työ jakautuu usein useammalle roolille:

- **Infrastruktuuri- tai alustatiimi** rakentaa ja ylläpitää
  laitteistoa, virtualisointia, tallennusta ja klustereita.
- **SRE** (site reliability engineering) vastaa palvelutasoista,
  valvonnasta ja häiriöiden käsittelystä ja automatisoi toistuvan
  työn pois.
- **DevOps-tiimi** omistaa palvelunsa koko elinkaaren, myös
  käyttöönoton ja valvonnan.

Nimistä riippumatta kaikki tarvitsevat samat perusasiat. Tutoriaali
käyttää yleistä sanaa *ylläpitäjä*.

## Työtavat

Kolme periaatetta toistuu kaikissa luvuissa:

1. **Kaikki koodina.** Palvelimen asetukset, varmuuskopioiden
   säilytyssäännöt ja hälytysrajat kirjoitetaan tiedostoihin, jotka
   ovat versionhallinnassa ja katselmoidaan. Käsin tehty muutos on
   tuntematon muutos.
2. **Mittaa ja laske.** "Riittävän luotettava" ja "tarpeeksi tilaa"
   muutetaan luvuiksi: saatavuusprosentiksi, virhebudjetiksi,
   kuukausiksi siihen, kun levy täyttyy.
3. **Testaa palautuminen.** Varmuuskopio, jota ei ole palautettu,
   RAID, jonka uudelleenrakennusta ei ole kokeiltu, ja hälytys, joka ei
   ole koskaan lauennut, ovat oletuksia, eivät suojauksia.

## Tutoriaalin esimerkit

Esimerkit ovat Python- ja Bash-ohjelmia, jotka ajetaan ja joiden
tuloste tarkistetaan automaattisesti. Työkaluja käytetään oikeasti
siltä osin kuin se onnistuu ilman erikoislaitteita:

- **rsync** ja **restic** tekevät oikeita varmuuskopioita
  tilapäishakemistoon.
- **OpenLDAP** käynnistetään tilapäishakemistoon vapaaseen porttiin.
- **Ansible** ajaa roolia paikallisesti tiedostoihin, jotka ovat
  tilapäisessä juurihakemistossa.
- **ext4-tiedostojärjestelmä** luodaan levykuvaan, johon kirjoitetaan
  `debugfs`-työkalulla ilman liittämistä.

Levyjärjestelmiä (`mdadm`, LVM) ei voi luoda tavallisessa kontissa
ilman ytimen etuoikeuksia. Niiden komennot näytetään tekstinä, ja
periaatteet (raidoitus, pariteetti, tarkistussummat) toteutetaan
Pythonilla, jotta ne voi ajaa ja testata. Komennot on tarkistettu
Ubuntu 24.04:n versioita vastaan.

Esimerkit ajetaan näin:

```text
make testaa              # tarkistukset ja kaikkien esimerkkien ajo
python3 esimerkit/03-ure.py
bash esimerkit/05-restic.sh
```

Kehityskontissa (`.devcontainer/palvelinymparistot`) on valmiina
Python, ShellCheck, Ansible, OpenLDAP, rsync ja restic.
