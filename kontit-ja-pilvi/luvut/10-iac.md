# Infrastruktuuri koodina

Kontit ja Kubernetes-resurssit kuvataan tiedostoina, mutta niiden alla
on infrastruktuuria: verkot, klusterit, rekisterit, tietokannat,
tallennustilat, DNS-nimet ja käyttöoikeudet. Jos ne luodaan pilven
hallintakonsolista käsin, kukaan ei tiedä tarkasti, mitä on olemassa ja
miksi, eikä ympäristöä voi luoda uudelleen. *Infrastruktuuri koodina*
(*infrastructure as code*, IaC) kuvaa myös ne tiedostoina, jotka ovat
versionhallinnassa, katselmoidaan ja ajetaan työkalulla.

## Deklaratiivinen malli

Terraform ja sen avoin jatkaja OpenTofu toimivat samalla mallilla kuin
Kubernetes:

1. **Kuvaus.** Haluttu tila kirjoitetaan tiedostoihin (HCL-kielellä).
2. **Suunnitelma** (`plan`). Työkalu lukee nykytilan (tilatiedosto ja
   pilvipalvelun rajapinta) ja laskee erot: mitä luodaan, muutetaan ja
   poistetaan.
3. **Toteutus** (`apply`). Työkalu kutsuu pilvipalvelun rajapintoja ja
   päivittää tilatiedoston.

Mallin ydin mahtuu muutamaan riviin. Esimerkkien `iac/tila.py` laskee
suunnitelman halutun ja nykyisen tilan erosta:

```{.python tiedosto="esimerkit/iac/tila.py" osa="suunnitelma"}
```

Haluttu tila:

```{.json tiedosto="esimerkit/iac/haluttu.json"}
```

Skripti ajaa suunnitelman, toteutuksen ja toisen suunnitelman ja
muuttaa sitten tilaa "käsin":

```{.bash tiedosto="esimerkit/iac/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/iac/aja.odotettu"}
```

Tulosteessa näkyvät mallin kolme tärkeintä ominaisuutta:

- **Idempotenssi.** Toinen ajo ei muuta mitään. Saman kuvauksen voi
  ajaa uudelleen turvallisesti, toisin kuin skriptin, joka luo
  resurssin joka kerta.
- **Suunnitelma ennen toteutusta.** Muutokset näkyvät ennen kuin
  mitään tapahtuu. Putkessa suunnitelma liitetään pull requestiin
  katselmoitavaksi.
- **Poikkeaman havaitseminen** (*drift*). Konsolista tehty muutos
  näkyy seuraavassa suunnitelmassa, ja seuraava toteutus palauttaa
  kuvauksen mukaisen tilan. Käsin tehty korjaus ei siis säily, ellei
  sitä kirjata kuvaukseen.

## Sama Terraformilla

Oikealla työkalulla klusterin kuvaus näyttää esimerkiksi tältä (ei
testattu tässä tutoriaalissa, koska se vaatii pilvipalvelun tunnukset):

```text
resource "google_container_cluster" "tuotanto" {
  name     = "kaynnit-tuotanto"
  location = "europe-north1"

  initial_node_count = 3
  min_master_version = "1.35"
}
```

```text
tofu init       # lataa palveluntarjoajan liitännäiset
tofu plan       # suunnitelma
tofu apply      # toteutus
```

## Tila, moduulit ja ympäristöt

- **Tilatiedosto** on työkalun muisti siitä, mitkä todelliset
  resurssit vastaavat mitäkin kuvausta. Se sisältää usein
  salaisuuksia, joten se säilytetään etätallennuksessa (objektitallennus,
  Terraform Cloud) salattuna ja lukittuna, jottei kaksi ajoa muuta sitä
  yhtä aikaa. Tilatiedosto ei kuulu versionhallintaan.
- **Moduulit** paketoivat toistuvan kokonaisuuden (verkko, klusteri,
  tietokanta) parametreineen, kuten Helm-kaavio Kubernetes-resurssit.
- **Ympäristöt** ovat saman moduulin eri parametreja ja eri tiloja,
  esimerkiksi omat hakemistot `kehitys/` ja `tuotanto/`.

## Muuttumaton infrastruktuuri

Kun palvelimia ei korjata paikan päällä vaan korvataan uusilla
(uusi kuva, uusi virtuaalikone, uusi pod), ympäristö on aina
sellainen kuin kuvaus sanoo. Kontit tekevät tästä luonnollista:
konttiin ei kirjauduta päivittämään paketteja, vaan rakennetaan uusi
kuva. Sama periaate koskee virtuaalikoneita (valmiit levykuvat,
Packer) ja klustereita (uusi solmuryhmä vanhan päivittämisen sijaan).

## Käytännössä

- **Kaikki infrastruktuuri koodiksi, myös "väliaikainen".** Käsin
  luodut resurssit unohtuvat ja maksavat; koodina ne voi poistaa yhdellä
  komennolla.
- **Suunnitelma katselmoitavaksi.** `plan` pull requestiin ja `apply`
  vasta yhdistämisen jälkeen putkessa, ei kehittäjän koneelta.
- **Tila etätallennukseen lukittuna.** Paikallinen tilatiedosto katoaa
  tai kilpailee toisen ajon kanssa.
- **Ei käsin tehtyjä muutoksia.** Hätätilanteessa tehty muutos
  kirjataan kuvaukseen heti, tai seuraava ajo kumoaa sen.
- **Lyhytaikaiset tunnukset.** Putki tunnistautuu pilveen
  OIDC-federaatiolla eikä pitkäikäisillä avaimilla (luku 11).

## Itsearviointi

- Osaat selittää deklaratiivisen infrastruktuurin suunnitelma–toteutus-
  syklin ja idempotenssin.
- Osaat kertoa, mitä poikkeama (drift) on ja miten se havaitaan ja
  korjataan.
- Osaat kertoa, miksi tilatiedosto säilytetään etätallennuksessa
  lukittuna ja miksi se ei kuulu versionhallintaan.
- Osaat perustella muuttumattoman infrastruktuurin periaatteen ja sen
  yhteyden kontteihin.
