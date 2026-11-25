# Verkko ja etäkäyttö: ssh

Tässä luvussa käsitellään ensin komennot, joilla selvitetään, toimiiko
verkkoyhteys, ja sitten SSH (*Secure Shell*), salattu yhteys etäkoneen
komentoriville. SSH:lla ylläpidetään palvelimia, siirretään tiedostoja,
käytetään Gitiä ja tunneloidaan muita yhteyksiä. OpenSSH on käytännössä
ainoa toteutus Linuxissa. Testiympäristössä ei ole etäkonetta, joten
luvun testatut esimerkit käsittelevät omaa konetta, avaimia ja
asetuksia. Yhteyskomennot etäkoneelle näytetään ilman tulostetta.

## Verkon perustyökalut

Kun yhteys palveluun ei toimi, vika on jollakin neljästä tasosta: nimi
ei selviä osoitteeksi, osoitteeseen ei ole reittiä, portti ei vastaa
tai palvelu vastaa virheellä. Jokaiselle tasolle on oma komentonsa:

| Komento | Mihin se vastaa |
|---------|-----------------|
| `ip addr`, `ip route` | Mitkä osoitteet koneella on ja minne liikenne reititetään |
| `getent hosts palvelin` | Miksi osoitteeksi nimi selviää tällä koneella |
| `dig +short palvelin` | Mitä nimipalvelu vastaa |
| `ping -c 3 palvelin` | Vastaako kone; palomuuri voi estää pingin, vaikka palvelu toimii |
| `nc -zv palvelin 443` | Aukeaako TCP-yhteys porttiin |
| `ss -tlnp` | Mitkä portit kuuntelevat tällä koneella ja mikä prosessi |
| `curl -I https://palvelin/` | Vastaako HTTP-palvelu ja millä tilakoodilla |
| `curl -fsS -o tiedosto URL` | Lataa tiedosto; `wget URL` tekee saman |

Komennot käydään läpi tässä järjestyksessä: nimi, yhteys, portti,
palvelu. Ensimmäinen epäonnistuva kertoo, missä vika on. `curl` on
näistä monipuolisin, koska sillä voi tehdä minkä tahansa HTTP-pyynnön.
Alla sitä kokeillaan omalla koneella ajettavaan palvelimeen:

```{.bash tiedosto="esimerkit/12-verkko.sh" osa="verkko"}
```

```{.tuloste tiedosto="esimerkit/12-verkko.odotettu"}
```

Oletuksena `curl` palauttaa arvon 0 aina, kun palvelin vastasi, myös
virhesivulla. Valitsin `-f` muuttaa HTTP-virheen (tilakoodi 400 tai
suurempi) paluuarvoksi 22, joten se kuuluu jokaiseen skriptiin. `-sS`
piilottaa edistymispalkin mutta näyttää virheet, `-I` hakee vain
otsakkeet ja `-L` seuraa uudelleenohjauksia. Osoite `127.0.0.1`
(`localhost`) on aina oma kone.

Verkkojen toiminta, osoitteet, nimipalvelu ja protokollat kuuluvat
taitoon *Tietoverkot*.

## Yhteys ja palvelimen tunnistus

```text
ssh kaisa@palvelin.example.com           # kuori etäkoneella
ssh -p 2222 kaisa@palvelin.example.com   # muu portti
ssh palvelin 'df -h /var'                # yksi komento, tuloste tänne
ssh palvelin 'sudo journalctl -u nginx -n 20' | grep -i error
```

Ensimmäisellä yhteydellä ssh näyttää palvelimen avaimen sormenjäljen
ja kysyy, luotetaanko siihen:

```text
The authenticity of host 'palvelin (192.0.2.10)' can't be established.
ED25519 key fingerprint is SHA256:kq1Zr0v…
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Sormenjälkeä verrataan palvelimen ylläpidolta saatuun. Vastauksen `yes`
jälkeen avain tallentuu tiedostoon `~/.ssh/known_hosts`. Jos avain
myöhemmin muuttuu, ssh kieltäytyy yhteydestä:

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
…
Host key verification failed.
```

Syy on joko uudelleen asennettu palvelin, jolla on uusi avain, tai
välimieshyökkäys. Sormenjälki tarkistetaan palvelimen ylläpidolta, ja
vasta sitten vanha avain poistetaan: `ssh-keygen -R palvelin`.

## Avaimet

Salasanan sijaan tunnistaudutaan avainparilla. Yksityinen avain pysyy
omalla koneella, ja julkinen avain lisätään palvelimen tiedostoon
`~/.ssh/authorized_keys`. Nykyinen suositus on Ed25519-avain, jonka
yksityinen osa suojataan salalauseella. Testissä salalause on tyhjä
(`-N ''`):

```{.bash tiedosto="esimerkit/12-avaimet.sh" osa="avain"}
```

`ssh-keygen` asettaa yksityiselle avaimelle oikeudet `600`. ssh
kieltäytyy käyttämästä avainta, jota muut voivat lukea. Julkinen avain
on yksi rivi: tyyppi, avain ja kommentti. Julkisen avaimen vienti
palvelimelle tehdään komennolla `ssh-copy-id -i tunnus_ed25519.pub
palvelin`.

Salalauseen kirjoittamista toistuvasti välttää *ssh-agent*, joka pitää
avatun avaimen muistissa (`ssh-add`). Työpöytäympäristöt käynnistävät
sen automaattisesti. `ssh -A` välittää agentin etäkoneelle, mutta
silloin etäkoneen pääkäyttäjä voi käyttää avaintasi yhteyden ajan.
Hyppykone (`ProxyJump`, alla) on turvallisempi tapa.

Avaimen käyttöä voi rajata `authorized_keys`-tiedostossa. Esimerkiksi
varmuuskopiointiavain saa ajaa vain yhden komennon ja vain
sisäverkosta:

```{.bash tiedosto="esimerkit/12-avaimet.sh" osa="rajoitettu"}
```

```{.tuloste tiedosto="esimerkit/12-avaimet.odotettu"}
```

Sormenjälkeä (`SHA256:…`) ei näytetä, koska se on jokaisella ajolla
eri. Rajoitettu avain on hyvä tapa antaa automaatiolle pääsy: vaikka
avain vuotaisi, sillä ei saa kuorta.

## Asetustiedosto

`~/.ssh/config` antaa koneille lyhyet nimet ja isäntäkohtaiset
asetukset. Jokaiselle asetukselle käytetään *ensimmäistä* osuvaa arvoa,
joten tarkat `Host`-lohkot kirjoitetaan ennen yleisiä:

```{.bash tiedosto="esimerkit/12-asetukset.sh" osa="config"}
```

Nyt `ssh rakennus-01` kirjautuu käyttäjänä `ci` koneeseen
`rakennus-01.sisainen.example.com` bastionin kautta. `%h` on annettu
nimi. `ssh -G` tulostaa lopulliset asetukset ottamatta yhteyttä, mikä
on paras tapa selvittää, miksi yhteys käyttää väärää käyttäjää tai
avainta:

```{.bash tiedosto="esimerkit/12-asetukset.sh" osa="tulkinta"}
```

```{.tuloste tiedosto="esimerkit/12-asetukset.odotettu"}
```

`IdentitiesOnly yes` estää ssh:ta kokeilemasta kaikkia agentin
avaimia. Muuten palvelin voi katkaista yhteyden liian monen
epäonnistuneen yrityksen jälkeen. `ServerAliveInterval` pitää
yhteyden auki palomuurien yli. Vianetsintään auttaa `ssh -v`, joka
näyttää, mitä avaimia ja asetuksia yritetään.

## Tiedostojen siirto

```text
scp raportti.pdf palvelin:/tmp/                  # yksi tiedosto
scp -r palvelin:/var/log/nginx ./lokit           # hakemisto tänne
rsync -av --delete sivusto/ palvelin:/srv/www/   # synkronointi
rsync -av --dry-run --delete sivusto/ palvelin:/srv/www/
sftp palvelin                                    # vuorovaikutteinen
```

`rsync` siirtää vain muutokset ja jatkaa keskeytyneestä, joten se on
oikea työkalu toistuviin siirtoihin ja varmuuskopioihin. Lähteen
lopun kauttaviiva on merkitsevä: `sivusto/` kopioi hakemiston
*sisällön*, `sivusto` hakemiston itsensä. `--delete` poistaa kohteesta
tiedostot, jotka puuttuvat lähteestä, joten se ajetaan ensin
`--dry-run`-valitsimella.

## Tunnelit

SSH-yhteys voi kuljettaa muita TCP-yhteyksiä:

```text
ssh -L 5433:localhost:5432 tietokanta   # paikallinen 5433 -> etäkoneen 5432
ssh -L 8080:sisainen-web:80 bastioni    # sisäverkon web-palvelu tänne
ssh -R 9000:localhost:3000 palvelin     # etäkoneen 9000 -> oma 3000
ssh -J bastioni rakennus-01             # hyppykoneen kautta
ssh -N -f -L 5433:localhost:5432 tietokanta  # vain tunneli, taustalle
```

Paikallinen tunneli (`-L`) on tavallisin: etäkoneen tietokanta, joka
kuuntelee vain osoitetta `localhost`, saadaan omalle koneelle ilman,
että sitä avataan verkkoon.

```{.dot otsikko="Paikallinen tunneli: ssh -L 5433:localhost:5432 tietokanta"}
digraph {
  rankdir=LR;
  subgraph cluster_o {
    label="oma kone"; color="#D9E0E3";
    a [label="psql -p 5433\n-h localhost"]; s [label="ssh\nkuuntelee: 5433"];
  }
  subgraph cluster_e {
    label="tietokanta"; color="#D9E0E3";
    d [label="sshd"]; p [label="PostgreSQL\nlocalhost:5432"];
  }
  a -> s; s -> d [label="salattu\nSSH-yhteys", penwidth=2]; d -> p;
}
```

Käänteinen tunneli (`-R`) toimii toiseen suuntaan: portti avataan
etäkoneella, ja yhteydet siihen ohjataan omalle koneelle. Sillä
näytetään esimerkiksi omalla koneella kehitettävä palvelu etäkoneen
kautta.

```{.dot otsikko="Käänteinen tunneli: ssh -R 9000:localhost:3000 palvelin"}
digraph {
  rankdir=LR;
  subgraph cluster_o {
    label="oma kone"; color="#D9E0E3";
    p [label="kehityspalvelin\nlocalhost:3000"]; s [label="ssh"];
  }
  subgraph cluster_e {
    label="palvelin"; color="#D9E0E3";
    d [label="sshd\nkuuntelee: 9000"]; a [label="asiakas\nlocalhost:9000"];
  }
  p -> s [dir=back]; s -> d [label="salattu\nSSH-yhteys", penwidth=2, dir=back];
  d -> a [dir=back];
}
```

Hyppykone (`-J`, asetuksissa `ProxyJump`) välittää yhteyden koneeseen,
johon ei pääse suoraan. Salaus ulottuu omalta koneelta kohteeseen asti,
joten hyppykone ei näe liikenteen sisältöä eikä tarvitse avaimiasi.

```{.dot otsikko="Hyppykone: ssh -J bastioni rakennus-01"}
digraph {
  rankdir=LR;
  o [label="oma kone\nssh"];
  b [label="bastioni\n(julkinen osoite)"];
  r [label="rakennus-01\n(sisäverkko)"];
  o -> b [label="SSH"]; b -> r [label="välitetty\nTCP-yhteys"];
  o -> r [style=dashed, label="päästä päähän salattu SSH-istunto", constraint=false];
}
```

## Pitkät istunnot: tmux

Katkeava yhteys lopettaa etäkuoren ja sen käynnistämät ohjelmat.
`tmux` pitää istunnon käynnissä palvelimella:

```text
tmux new -s paivitys     # uusi nimetty istunto
# ... pitkä ajo ...  Ctrl+B d irrottaa istunnon
tmux ls                  # istunnot
tmux attach -t paivitys  # palaa istuntoon, myös toisesta yhteydestä
```

Ctrl+B `%` ja `"` jakavat ikkunan, ja Ctrl+B `c` luo uuden ikkunan.
Palvelinpäivitykset ja pitkät siirrot ajetaan aina tmuxissa.

## Palvelimen kovennus lyhyesti

Palvelimen asetukset ovat tiedostossa `/etc/ssh/sshd_config` tai
hakemistossa `/etc/ssh/sshd_config.d/`. Perusasetukset ovat:

```ini
PasswordAuthentication no      # vain avaimet
PermitRootLogin no             # ylläpito sudo-oikeuksin
AllowGroups ssh-kayttajat      # vain nimetyt käyttäjät
```

Tarkista asetukset komennolla `sudo sshd -t` ennen uudelleenlatausta
(`systemctl reload ssh`) ja pidä toinen yhteys auki. Virheellinen
asetus voi muuten lukita sinut ulos koneesta.

## Käytännössä

- **Ed25519-avain salalauseella ja agentti**, ei salasanoja.
  Yksi avain laitetta kohden, jotta kadonneen laitteen avaimen voi
  poistaa muihin vaikuttamatta.
- **`~/.ssh/config` komentorivivalitsinten sijaan.** Asetukset ovat
  silloin samat ssh:lle, scp:lle, rsyncille ja Gitille.
- **Sormenjälki tarkistetaan, ei ohiteta.** Varoitus muuttuneesta
  avaimesta on juuri se tilanne, jota varten tarkistus on olemassa.
- **`ProxyJump`, ei agentin välitystä**, kun mennään hyppykoneen
  kautta.
- **Automaation avaimet rajataan** (`command=`, `from=`) ja pidetään
  erillään henkilökohtaisista avaimista.
- **`rsync --dry-run` ennen `--delete`-valitsinta** ja tmux ennen
  pitkää ajoa.

## Itsearviointi

- Osaat selvittää komennoilla, onko vika nimessä, yhteydessä, portissa
  vai palvelussa, ja tehdä HTTP-pyynnön `curl`-komennolla niin, että
  virhe näkyy paluuarvossa.
- Osaat luoda avainparin, viedä julkisen avaimen palvelimelle ja
  rajata avaimen käyttöä `authorized_keys`-tiedostossa.
- Osaat kirjoittaa `~/.ssh/config`-tiedoston, jossa on lyhyet nimet ja
  hyppykone, ja tarkistaa lopulliset asetukset `ssh -G`:llä.
- Osaat siirtää ja synkronoida tiedostoja `scp`:llä ja `rsync`:llä.
- Osaat avata paikallisen tunnelin ja pitää pitkän ajon käynnissä
  tmuxissa.
- Osaat toimia oikein, kun palvelimen avain on muuttunut.
