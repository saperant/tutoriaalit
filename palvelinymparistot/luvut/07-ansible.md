# Konfiguraationhallinta Ansiblella

Käsin asennettu palvelin on ainutkertainen: kukaan ei muista, mitä
siihen tehtiin kolme vuotta sitten, eikä sitä voi rakentaa uudelleen
samanlaiseksi. Konfiguraationhallinta kuvaa koneiden halutun tilan
tiedostoina, ja työkalu saattaa koneet siihen tilaan. Kuvaus on
versionhallinnassa, katselmoidaan kuten koodi ja toimii samalla
dokumentaationa.

## Ansiblen rakenne

Ansible ottaa yhteyden koneisiin SSH:lla, eikä kohdekoneisiin tarvitse
asentaa agenttia. Rakenneosat:

| Osa | Tehtävä |
|-----|---------|
| Inventaario | Koneet ryhmittäin ja ryhmäkohtaiset muuttujat |
| Playbook | Mitkä roolit ja tehtävät ajetaan millekin ryhmälle |
| Rooli | Uudelleenkäytettävä kokonaisuus: tehtävät, oletusarvot, mallit, käsittelijät |
| Moduuli | Yksi toiminto, joka kuvaa halutun tilan (`file`, `template`, `lineinfile`, `service`) |
| Käsittelijä | Toimenpide, joka ajetaan vain, jos jokin tehtävä muutti jotain |

Esimerkin playbook ajaa web-palvelimille roolin `perus`:

```{.yaml tiedosto="esimerkit/07-ansible/palvelin.yml" osa="playbook"}
```

Roolin oletusarvot voi korvata inventaariossa ryhmä- tai konekohtaisesti:

```{.yaml tiedosto="esimerkit/07-ansible/roles/perus/defaults/main.yml" osa="oletukset"}
```

Tehtävät kuvaavat lopputilan, eivät komentoja. `template` tuottaa
SSH-palvelimen asetukset Jinja2-mallista ja ilmoittaa käsittelijälle,
jos tiedosto muuttui:

```{.yaml tiedosto="esimerkit/07-ansible/roles/perus/tasks/main.yml" osa="tehtavat"}
```

```{.text tiedosto="esimerkit/07-ansible/roles/perus/templates/sshd_config.j2"}
```

```{.yaml tiedosto="esimerkit/07-ansible/roles/perus/handlers/main.yml" osa="kasittelija"}
```

Testissä tiedostot kirjoitetaan tilapäiseen juurihakemistoon
(muuttuja `juuri`), ja yhteys on paikallinen. Oikeassa ympäristössä
juuri on tyhjä ja käsittelijä lataa SSH-palvelun uudelleen.

## Idempotenssi

Idempotentti tehtävä tuottaa saman lopputilan, ajettiin se kerran tai
sata kertaa, ja raportoi muutoksen vain, kun se todella muutti jotain.
Siksi playbookin voi ajaa milloin tahansa, ja ajon tulos kertoo, oliko
kone halutussa tilassa:

```{.bash tiedosto="esimerkit/07-ansible/main.sh" osa="ajo"}
```

Toinen ajo ei muuta mitään (`changed=0`), eikä käsittelijää ajeta.
Kun joku muuttaa asetusta käsin, tarkistusajo (`--check --diff`)
näyttää poikkeaman muuttamatta mitään, ja seuraava ajo palauttaa
halutun tilan:

```{.bash tiedosto="esimerkit/07-ansible/main.sh" osa="ajautuminen"}
```

```{.tuloste tiedosto="esimerkit/07-ansible.odotettu"}
```

Säännöllisesti ajettu tarkistusajo on halpa tapa havaita *ajautuminen*
(configuration drift): koneet, joita on muutettu ohi
konfiguraationhallinnan. Periaate on sama kuin pilvi-infrastruktuurin
suunnitelma–toteutus-syklissä (taito *Kontit ja
pilvi-infrastruktuuri*): kuvaus on totuus, ja työkalu näyttää eron
ennen kuin korjaa sen.

Idempotenssi ei synny itsestään. Moduuli `shell` ajaa komennon joka
kerta, eikä Ansible tiedä, mitä se tekee:

```{.yaml tiedosto="esimerkit/07-idempotenssi/kirjaus.yml" osa="huono"}
```

```{.yaml tiedosto="esimerkit/07-idempotenssi/kirjaus.yml" osa="hyva"}
```

```{.bash tiedosto="esimerkit/07-idempotenssi/main.sh"}
```

```{.tuloste tiedosto="esimerkit/07-idempotenssi.odotettu"}
```

Jos komentoa on pakko käyttää, sille kerrotaan, milloin se on jo tehty
(`creates:`, `removes:`) ja milloin se muutti jotain (`changed_when:`).

## Testaus

Konfiguraatiokoodi testataan kuten muukin koodi, portaittain:

1. **Syntaksi ja tyyli:** `ansible-playbook --syntax-check` ja
   `ansible-lint`.
2. **Tarkistusajo** testiympäristöä vastaan: `--check --diff` näyttää,
   mitä muuttuisi.
3. **Integraatiotesti:** rooli ajetaan puhtaaseen koneeseen tai
   konttiin kahdesti, toinen ajo ei saa muuttaa mitään, ja lopputila
   tarkistetaan (Molecule-työkalu automatisoi tämän).
4. **Vaiheittainen käyttöönotto:** ensin yksi kone (`--limit`), sitten
   loput erissä (`serial:`), jotta virhe ei kaada kaikkia kerralla.

## Salaisuudet

Salasanoja ja avaimia ei kirjoiteta playbookeihin selväkielisinä.
Vaihtoehtoja ovat Ansible Vault (salatut muuttujatiedostot), ulkoinen
salaisuusvarasto (HashiCorp Vault, pilven salaisuuspalvelu), josta
arvot haetaan ajon aikana, tai SOPS. Salaisuuksien hallintaa käsittelee
tarkemmin taito *Tietoturva kehitystyössä*.

## Käytännössä

- **Kaikki muutokset koodin kautta.** Käsin tehty korjaus kirjataan
  heti rooliin, tai seuraava ajo kumoaa sen.
- **Moduulit ennen komentoja.** `shell` ja `command` vain, kun
  moduulia ei ole, ja silloin `creates`/`changed_when`.
- **Roolit pieniksi ja yksitehtäväisiksi**, oletusarvot rooliin,
  ympäristökohtaiset arvot inventaarioon.
- **Ajautumisen valvonta.** Tarkistusajo aikataulutettuna, ja
  poikkeamat raportoidaan.
- **Kertakäyttöiset koneet.** Kun koneen voi rakentaa koodista
  minuuteissa, rikkinäistä konetta ei korjata vaan se korvataan
  (*immutable infrastructure*). Konttien ja pilven kanssa tämä on
  oletus (ks. *Kontit ja pilvi-infrastruktuuri*).

## Itsearviointi

- Osaat kuvata Ansiblen inventaarion, playbookin, roolin, moduulin ja
  käsittelijän tehtävät.
- Osaat kirjoittaa idempotentin roolin ja todentaa idempotenssin
  ajamalla sen kahdesti.
- Osaat havaita ajautumisen tarkistusajolla ja korjata sen.
- Osaat testata ja ottaa käyttöön konfiguraatiomuutoksen vaiheittain ja
  säilyttää salaisuudet turvallisesti.
