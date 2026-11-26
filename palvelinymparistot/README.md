# Palvelinympäristöt

Tiivis suomenkielinen opas palvelinympäristöjen ylläpitoon: laitteisto,
tallennus ja RAID, tiedostojärjestelmät, varmuuskopiointi,
käyttäjähallinta, palvelut ja systemd, konfiguraationhallinta
Ansiblella, koventaminen, klusterien ylläpito, valvonta ja
palvelutasot sekä kustannukset.
Valmiit dokumentit:
[palvelinymparistot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelinymparistot.pdf)
ja pikaopas
[palvelinymparistot-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelinymparistot-pikaopas.pdf).

Esitiedot: [Verkkoinfrastruktuuri](../verkkoinfrastruktuuri/) ja
[Kontit ja pilvi-infrastruktuuri](../kontit-ja-pilvi/).

## Sisältö

1. Johdanto – palvelinympäristö kokonaisuutena, roolit, työtavat
2. Palvelinlaitteisto – ECC-muisti ja EDAC, kahdennettu virransyöttö,
   BMC, IPMI ja Redfish
3. Tallennus ja RAID – SAS, NVMe, RAID-tasot, pariteetti,
   uudelleenrakennus ja lukuvirheet, mdadm
4. Tiedostojärjestelmät, LVM ja ZFS – inodet, LVM, bittimätä,
   tarkistussummat ja scrub, lohko-, tiedosto- ja objektitallennus
5. Varmuuskopiointi – RPO ja RTO, 3-2-1-1-0, rsync ja kovat linkit,
   restic, porrastettu säilytys, palautustestaus
6. Käyttäjähallinta ja hakemistot – LDAP, pääsynhallinta, Kerberos,
   Active Directory ja SSSD
7. Palvelut ja systemd – yksiköt, riippuvuudet, valmius ja
   sokettiaktivointi, uudelleenkäynnistys, rajaaminen, journald,
   ajastimet, vianetsintä, ajan tahdistus
8. Konfiguraationhallinta Ansiblella – roolit, idempotenssi,
   ajautuminen, testaus
9. Koventaminen ja päivitykset – tarkastus koodina, päivitysprosessi,
   varmenteiden elinkaari, auditointi
10. Virtualisointialustat ja klusterit – N+1, live migration,
    PodDisruptionBudget, klusterin ylläpito
11. Valvonta ja palvelutasot – saatavuus, SLI, SLO, SLA,
    virhebudjetti ja palamisnopeushälytykset, häiriön jälkiselvitys
12. Kustannukset ja kapasiteetti – TCO, kapasiteetin ennustaminen,
    varakapasiteetti
13. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, ShellCheck ja ajot
make pdf      # palvelinymparistot.pdf ja pikaopas
make kuvat    # piirtää kuvaajat uudelleen (kuvat/piirra.py, Matplotlib)
```

Esimerkit tarvitsevat Python 3.12:n, ShellCheckin, Ansiblen
(`ansible-core`), OpenLDAPin (`slapd`, `ldap-utils`), rsyncin,
resticin, e2fsprogsin ja systemd:n (`systemd-analyze`).
Kehityskontissa ne ovat valmiina. Luvun 7 koe oikean systemd:n alla
(`make -C esimerkit`) ajetaan vain koneessa, jossa systemd on
prosessi 1 ja `sudo` toimii ilman salasanaa; muualla se ohittaa
itsensä. Levyjärjestelmien
komennot (`mdadm`, LVM, ZFS) vaativat ytimen etuoikeuksia, ja ne
näytetään tekstissä ajamatta.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
