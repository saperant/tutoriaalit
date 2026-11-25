# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kirjoita kaikki koodiksi.** Asetukset, koventaminen, säilytyssäännöt
   ja hälytykset ovat versionhallinnassa ja katselmoidaan.
2. **Redundanssin menetys on hälytys.** Kahdennettu osa, jonka parin
   vikaa ei huomata, on yksittäinen vikaantumispiste.
3. **RAID ei ole varmuuskopio, eikä vedos ole varmuuskopio.**
   Varmuuskopio on toisessa paikassa, ja yksi kopio on muuttumaton.
4. **Testaa palautus.** Mittaa palautuksen kesto ja vertaa sitä RTO:hon.
5. **Laske ennen kuin päätät.** RAID-taso, saatavuus, kapasiteetti ja
   kustannukset ovat laskelmia, joiden oletukset kirjataan.
6. **Yksi lähde käyttäjille ja ryhmille**, ja oikeudet ryhmille.
7. **Idempotentti konfiguraatio ja ajautumisen valvonta.**
8. **Päivitä rutiinilla**, ja muista uudelleenkäynnistys.
9. **Mitoita N+1**, myös suurimman koneen ja jokaisen sovelluksen
   kannalta.
10. **Hälytä käyttäjälle näkyvistä oireista ja virhebudjetin
    palamisesta**, ja anna jokaiselle hälytykselle ohje.

## Jatkotaidot

- *Virtualisointi*: hypervisorit, laitteistotuki ja kontit ytimen
  tasolla.
- *Kontit ja pilvi-infrastruktuuri*: tämän taidon esitieto, johon
  kannattaa palata klusterin käyttäjän näkökulmasta.
- *Skaalautuvien järjestelmien suunnittelu*: skaalautuvuus,
  replikointi, havaittavuus ja luotettavuusmallit sovellusten
  näkökulmasta.
- *Jatkuva integraatio ja toimitus*: käyttöönottojen automatisointi ja
  infrastruktuurimuutosten putket.
- *Tietoturva kehitystyössä* ja *Palveluarkkitehtuurin tietoturva*:
  salaisuuksien hallinta, toimitusketju ja nollaluottamus.

## Lähteet ja lisämateriaali

### Kirjat ja oppaat

- Beyer, Jones, Petoff, Murphy (toim.): *Site Reliability
  Engineering*. O'Reilly 2016. Luettavissa maksutta:
  <https://sre.google/sre-book/table-of-contents/>
- Beyer ym. (toim.): *The Site Reliability Workbook*. O'Reilly 2018.
  Luku *Alerting on SLOs* esittelee palamisnopeuteen perustuvat
  hälytykset: <https://sre.google/workbook/alerting-on-slos/>
- Limoncelli, Hogan, Chalup: *The Practice of System and Network
  Administration*, 3. painos. Addison-Wesley 2016.
- Kyberturvallisuuskeskus: ohjeet ja suositukset palvelinten ja
  järjestelmien suojaamiseen: <https://www.kyberturvallisuuskeskus.fi/>

### Dokumentaatio

- Linux RAID -wiki (mdadm): <https://raid.wiki.kernel.org/>
- OpenZFS-dokumentaatio: <https://openzfs.github.io/openzfs-docs/>
- LVM: `man lvm`, `man lvmthin`
- restic: <https://restic.readthedocs.io/>
- OpenLDAP Administrator's Guide: <https://www.openldap.org/doc/admin26/>
- MIT Kerberos -dokumentaatio: <https://web.mit.edu/kerberos/krb5-latest/doc/>
- SSSD: <https://sssd.io/>
- Ansible-dokumentaatio: <https://docs.ansible.com/>
- DMTF Redfish -määrittely: <https://www.dmtf.org/standards/redfish>
- Prometheus: <https://prometheus.io/docs/>
- CIS Benchmarks: <https://www.cisecurity.org/cis-benchmarks>

### Työkalut

- Ansible Lint ja Molecule roolien testaukseen.
- OpenSCAP ja Lynis koventamisen tarkastukseen.
- `smartctl` (smartmontools), `rasdaemon` ja `ipmitool` laitteiston
  kunnon seurantaan.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkiohjelmia saa
käyttää ja muokata saman lisenssin ehdoin.
