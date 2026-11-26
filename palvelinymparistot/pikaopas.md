---
title: Palvelinympäristöt
subtitle: Pikaopas · laitteisto, tallennus, varmuuskopiot, hakemistot, palvelut, Ansible, palvelutasot
---

# Laitteisto

| Asia | Komento tai sääntö |
|------|--------------------|
| Muistivirheet | `ras-mc-ctl --error-count`, `/sys/devices/system/edac/mc` |
| Levyn kunto | `smartctl -a /dev/sda`, NVMe: `smartctl -a /dev/nvme0` |
| BMC | `ipmitool sdr`, Redfish `GET /redfish/v1/Chassis/1/Power` |
| Virtalähteet | Eri syötöt (A/B), kumpikin kestää koko kuorman |
| Hallintaverkko | BMC:t erilliseen verkkoon, oletustunnukset pois |

# RAID

| Taso | Käytössä (n levyä) | Kestää | Kirjoitus × |
|------|-------------------|--------|-------------|
| 1 | 1/n | n−1 | n |
| 10 | n/2 | 1 (varmasti) | 2 |
| 5 | n−1 | 1 | 4 |
| 6 | n−2 | 2 | 6 |

```{.python tiedosto="esimerkit/03-ure.py" osa="ure"}
```

- `cat /proc/mdstat`, `mdadm --detail /dev/md0`, kuukausittainen
  `check`.
- Suurille levyille RAID 6 tai RAID 10. RAID ei ole varmuuskopio.

# Tiedostojärjestelmät

| Tehtävä | Komento |
|---------|---------|
| Tila ja inodet | `df -h`, `df -i` |
| LVM kasvatus | `lvextend -r -L +100G /dev/vg/lv` |
| LVM vedos | `lvcreate -s -n vedos -L 20G /dev/vg/lv` |
| ZFS | `zfs snapshot p/fs@nimi`, `zpool scrub p`, `zpool status` |

# Varmuuskopiointi

- **RPO** = kopiointiväli ≤ sallittu datan menetys; **RTO** =
  palautuksen kesto ≤ sallittu katko.
- **3-2-1-1-0**: 3 kopiota, 2 mediaa, 1 muualla, 1 muuttumaton,
  0 palautusvirhettä.

```{.bash tiedosto="esimerkit/05-rsync-kopiot.sh" osa="kopio"}
```

| restic | Komento |
|--------|---------|
| Alustus | `restic init` |
| Kopio | `restic backup --tag paivittainen /data` |
| Säilytys | `restic forget --keep-daily 7 --keep-monthly 12 --prune` |
| Eheys | `restic check` |
| Palautus | `restic restore latest --target /palautus` |

# Hakemistot

| Tehtävä | Komento |
|---------|---------|
| Haku | `ldapsearch -x -H ldaps://ldap -b dc=x,dc=fi '(uid=aino)'` |
| Kirjautuminen | `ldapwhoami -x -H ldaps://ldap -D uid=aino,... -W` |
| Salasanatiiviste | `slappasswd` |
| AD-liitos | `realm join esimerkki.fi`, `getent passwd aino` |
| Kerberos | `kinit aino`, `klist`; kellot ±5 min |

# Palvelut (systemd)

| Tehtävä | Komento tai asetus |
|---------|--------------------|
| Tarkistus | `systemd-analyze verify x.service` |
| Altistus | `systemd-analyze security x`, putkessa `--threshold=20` |
| Tila ja loki | `systemctl status x`, `journalctl -u x -b -p err` |
| Asetukset | `systemctl cat x`; lisäys `systemctl edit x` |
| Riippuvuus | `Wants=` ja `After=`; `Requires=` vain pakosta |
| Kestävyys | `Type=notify`, `Restart=on-failure`, `StartLimitBurst=` |
| Rajaus | `DynamicUser=`, `ProtectSystem=strict`, `MemoryMax=` |
| Ajastin | `OnCalendar=`, `systemd-analyze calendar "Mon..Fri 02:30"` |
| Kello | `timedatectl`, `chronyc tracking`, `chronyc sources` |

# Ansible

| Tehtävä | Komento |
|---------|---------|
| Ajo | `ansible-playbook -i inventaario palvelin.yml` |
| Kuiva-ajo | `--check --diff` |
| Rajaus | `--limit web1`, `--tags ssh` |
| Syntaksi | `--syntax-check`, `ansible-lint` |

- Moduulit kuvaavat tilan; `shell` vain `creates`/`changed_when`-ehdoin.
- Toinen ajo: `changed=0`.

# Koventaminen

- SSH: `PermitRootLogin no`, `PasswordAuthentication no`, `AllowGroups`.
- `unattended-upgrades`; `/var/run/reboot-required`; `needrestart`.
- `ss -tlnp` kuuntelevat portit; `find /etc -perm -o+w`.

# Palvelutasot

| Saatavuus | Katko / kk | Katko / v |
|-----------|-----------|-----------|
| 99 % | 7,2 h | 3,7 vrk |
| 99,9 % | 43 min | 8,8 h |
| 99,99 % | 4,3 min | 53 min |

```{.python tiedosto="esimerkit/11-virhebudjetti.py" osa="palaminen"}
```

- Päivystäjä: palamisnopeus > 14,4 (1 h ja 5 min ikkunat).
- Tiketti: > 6 (6 h ja 1 h ikkunat).

# Kapasiteetti ja kustannukset

- TCO = laitteet + sähkö × PUE + tila + tuki + työ.
- Tilaa laajennus: ennustettu rajan ylitys − hankinta-aika.
- N+1: suurin virtuaalikone mahtuu yksittäiselle isännälle vian jälkeen.
