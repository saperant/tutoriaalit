# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kontti on prosessi.** Yksi vastuu, exec-muoto, SIGTERM käsitelty,
   ei rootia, muistiraja aina.
2. **Kuva on toistettava.** Peruskuva digestillä, riippuvuudet
   lukittuina, rakennus samalla komennolla kaikkialla.
3. **Kuva on pieni ja tarkistettu.** Monivaiheinen rakennus,
   distroless tai slim, hadolint, skannaus ja SBOM.
4. **Sama kuva joka ympäristöön.** Erot asetuksissa, ei kuvissa.
5. **Tila erikseen.** Tilattomat palvelut skaalautuvat; tila kuuluu
   tietokantaan, volyymiin tai hallittuun palveluun.
6. **Elävyys ja valmius erikseen.** Elävyys ei riipu muista
   palveluista; valmius kertoo totuuden.
7. **Haluttu tila versionhallintaan.** Manifestit, kaaviot ja
   infrastruktuuri koodina; ei käsin tehtyjä muutoksia.
8. **Tarkista ennen kuin otat käyttöön.** Skeemat, käytännöt koodina,
   renderöinnin vertailu ja suunnitelma katselmoitavaksi.
9. **Käyttöönotto osaa perua itsensä.** Rullaava päivitys ilman
   katkoa, `--atomic`, mittarit.
10. **Vähimmät oikeudet kaikkialla.** Kontti, pod, nimiavaruus,
    putki ja pilvitunnukset.

## Mallit

| Malli | Luku | Tarkoitus |
|-------|------|-----------|
| monivaiheinen rakennus | 3–4 | pieni ajokuva, testit kuvan sisällä |
| twelve-factor | 5 | sovellus, joka sopii konttiin |
| hallittu sammutus | 3, 5 | käyttöönotot ilman katkenneita pyyntöjä |
| elävyys- ja valmiustarkistus | 5, 8 | oikea toimenpide oikeaan vikaan |
| sivuvaunu (*sidecar*) | 7 | apuprosessi samaan podiin |
| ohjaussilmukka | 7, 9, 10 | haluttu tila, jatkuva korjaus |
| käytännöt koodina | 8 | organisaation säännöt automaattisiksi |
| kultainen tiedosto | 9 | renderöinnin regressiot näkyviin |
| GitOps | 9 | versionhallinta käyttöönottojen lähteenä |
| muuttumaton infrastruktuuri | 10 | korvaa, älä korjaa |
| rakenna kerran, ota käyttöön monesti | 11 | testattu kuva tuotantoon |
| expand–contract | 11 | skeemamuutokset ilman katkoa |

## Mihin seuraavaksi

- **Palvelinympäristöt:** konesalit, tallennus, varmuuskopiot,
  käyttäjähallinta ja klusterien ylläpito.
- **Palveluarkkitehtuurit:** miten sovellus jaetaan palveluihin ja miten
  ne puhuvat keskenään.
- **Järjestelmäsuunnittelu:** skaalautuvuus, välimuistit, jonot ja
  luotettavuus.
- **Virtualisointi:** konttien ja virtuaalikoneiden toteutus ytimessä
  ja laitteistossa.
- **Palveluarkkitehtuurin tietoturva:** nollaluottamus, palvelujen
  identiteetit ja salaisuudet tuotannossa.

## Lähteet

- **The Twelve-Factor App** (<https://12factor.net>): konttisovelluksen
  periaatteet.
- **Dockerin dokumentaatio** (<https://docs.docker.com>): Dockerfile-
  viite, rakennuksen parhaat käytännöt, Compose-määrittely.
- **Open Container Initiative** (<https://opencontainers.org>): kuva- ja
  ajoaikamäärittelyt.
- **Kubernetesin dokumentaatio** (<https://kubernetes.io/docs>):
  käsitteet, Pod Security Standards, resurssien hallinta, rullaavat
  päivitykset. Dokumentaatio on lisensoitu CC BY 4.0 -lisenssillä.
- **Helmin dokumentaatio** (<https://helm.sh/docs>): kaavioiden
  rakenne ja parhaat käytännöt.
- **OpenTofu** (<https://opentofu.org/docs>) ja **Terraform**
  (<https://developer.hashicorp.com/terraform/docs>).
- **OpenGitOps** (<https://opengitops.dev>): GitOpsin periaatteet.
- **Google distroless** (<https://github.com/GoogleContainerTools/distroless>).
- **hadolint** (<https://github.com/hadolint/hadolint>): säännöt
  selityksineen.
- **CNCF Cloud Native Landscape** (<https://landscape.cncf.io>):
  ekosysteemin työkalut.
- **Kirjat:** Brendan Burns, Joe Beda, Kelsey Hightower ja Lachlan
  Evenson, *Kubernetes: Up and Running*. Bilgin Ibryam ja Roland Huß,
  *Kubernetes Patterns*. Kief Morris, *Infrastructure as Code*. Jez
  Humble ja David Farley, *Continuous Delivery*. Liz Rice, *Container
  Security*.

### Työkalut

- **kind** ja **k3d**: paikallinen Kubernetes Dockerin päällä.
- **k9s** ja **Lens**: klusterin tarkastelu.
- **Trivy** ja **Grype**: haavoittuvuusskannaus; **Syft**: SBOM;
  **cosign**: allekirjoitukset.
- **Kyverno**, **OPA Gatekeeper** ja **Conftest**: käytännöt koodina.
- **Argo CD** ja **Flux**: GitOps.
- **Renovate** ja **Dependabot**: kuvien ja riippuvuuksien
  päivitysehdotukset.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
