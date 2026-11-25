# Helm ja GitOps

Luvun 8 manifestit kuvaavat yhden ympäristön. Kun sama sovellus
ajetaan kehityksessä, testissä ja tuotannossa eri replikamäärin,
osoittein ja asetuksin, manifestien kopiointi johtaa nopeasti eroihin,
joita kukaan ei huomaa. Helm tekee manifesteista parametrisoitavan
paketin, ja GitOps tuo paketin klusteriin versionhallinnasta.

## Helm-kaavio

Helmin paketti on *kaavio* (*chart*): hakemisto, jossa on kuvaus,
oletusarvot ja Go-mallipohjat.

```text
helm/kaynnit/
  Chart.yaml              nimi, kaavion versio ja sovelluksen versio
  values.yaml             oletusarvot
  values-tuotanto.yaml    tuotannon erot
  templates/              mallipohjat
    _apu.tpl              yhteiset apumallit
    deployment.yaml  service.yaml  configmap.yaml
    ingress.yaml  hpa.yaml
```

```{.yaml tiedosto="esimerkit/helm/kaynnit/Chart.yaml"}
```

Kaaviolla on kaksi versiota: `version` on kaavion oma (muuttuu, kun
pohjat muuttuvat) ja `appVersion` sovelluksen, jota kaavio oletuksena
asentaa.

## Arvot ja ympäristöt

```{.yaml tiedosto="esimerkit/helm/kaynnit/values.yaml"}
```

Tuotannon tiedostossa ovat vain erot:

```{.yaml tiedosto="esimerkit/helm/kaynnit/values-tuotanto.yaml"}
```

Ympäristökohtainen tiedosto on lyhyt ja luettava: siitä näkee heti,
miten tuotanto eroaa oletuksesta. Kun sama ero toistuu kaikissa
ympäristöissä, se siirretään oletuksiin.

## Mallipohjat

```{.yaml tiedosto="esimerkit/helm/kaynnit/templates/deployment.yaml"}
```

```{.yaml tiedosto="esimerkit/helm/kaynnit/templates/_apu.tpl"}
```

- **`{{ .Values.… }}`, `.Release`, `.Chart`.** Arvot, asennuksen nimi
  ja kaavion tiedot.
- **`include` ja `nindent`.** Apumalli (`define`) lisätään oikeaan
  sisennykseen; YAML:ssä sisennys on merkitsevä.
- **`toYaml`.** Kokonainen arvopuu, kuten resurssit, kirjoitetaan
  sellaisenaan.
- **Asetusten tiiviste.** Annotaatio `checksum/asetukset` sisältää
  ConfigMapin tiivisteen. Kun asetukset muuttuvat, podin pohja muuttuu
  ja Deployment vaihtaa podit, jolloin uudet asetukset tulevat voimaan
  (luku 8).
- **`replicas` vain ilman skaalausta.** Automaattisen skaalauksen
  kanssa replikamäärä jätetään HPA:lle.

Ehdolliset resurssit luodaan vain tarvittaessa:

```{.yaml tiedosto="esimerkit/helm/kaynnit/templates/hpa.yaml"}
```

## Renderöinti ja tarkistus

`helm template` tulostaa valmiit manifestit asentamatta mitään.
Esimerkkien testi renderöi tuotannon manifestit, vertaa ne
tallennettuun tulokseen ja tarkistaa ne kuten luvun 8 manifestit
(rivit *helm* tiedostossa `testit/docker.odotettu`). Renderöity HPA:

```{.tuloste tiedosto="esimerkit/helm/hpa.odotettu"}
```

Tallennettu renderöinti on *kultainen tiedosto*: jos pohjan muutos
muuttaa tulosta odottamatta, testi näyttää eron rivi riviltä.
`helm lint` tarkistaa kaavion rakenteen, ja `required` kaataa
renderöinnin selvällä viestillä, jos pakollinen arvo puuttuu.

Asennus ja päivitys tehdään samalla komennolla:

```text
helm upgrade --install kaynnit helm/kaynnit -n kaynnit \
    -f helm/kaynnit/values-tuotanto.yaml --wait --atomic
helm -n kaynnit history kaynnit
helm -n kaynnit rollback kaynnit 3
```

`--atomic` peruu päivityksen, jos resurssit eivät tule valmiiksi
aikarajassa. Helm tallentaa jokaisen version klusteriin, joten
edelliseen palaaminen on yksi komento.

## Kustomize vaihtoehtona

Kustomize (sisäänrakennettuna `kubectl apply -k`) ei käytä
mallipohjia vaan *päällekkäisyyksiä* (*overlay*): perusmanifestit ja
ympäristökohtaiset muutokset niihin. Se sopii, kun erot ovat pieniä ja
manifestit halutaan pitää tavallisena YAML:na. Helm sopii, kun sovellus
jaetaan muille asennettavaksi paketiksi tai erot ovat suuria.

## GitOps

GitOpsissa versionhallinta on klusterin halutun tilan ainoa lähde, ja
klusterissa ajettava agentti (Argo CD, Flux) vetää muutokset sieltä:

1. Muutos (uusi kuvan tagi, asetus) tehdään pull requestina
   käyttöönottorepositorioon.
2. Katselmoinnin ja hyväksynnän jälkeen muutos yhdistetään.
3. Agentti huomaa muutoksen, renderöi manifestit (Helm, Kustomize) ja
   vie ne klusteriin.
4. Agentti vertaa jatkuvasti klusterin tilaa versionhallintaan ja
   korjaa ajautumisen (*drift*) tai ilmoittaa siitä.

```{.dot otsikko="Työntävä putki ja vetävä agentti. Työntävässä mallissa klusterin tunnukset ovat CI-järjestelmässä ja käyttöönotto tapahtuu vain putken ajon aikana. GitOpsissa agentti on klusterin sisällä, hakee halutun tilan itse ja vertaa sitä jatkuvasti todelliseen."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.55;
  subgraph cluster_g {
    label="GitOps: agentti vetää"; style="rounded"; margin=10;
    c2 [label="CI-putki"];
    g2 [label="käyttöönotto-\nrepositorio"];
    subgraph cluster_k { label="klusteri"; style="rounded,dashed"; margin=8;
      a2 [label="agentti\n(Argo CD, Flux)", penwidth=1.6]; r2 [label="resurssit"];
      a2 -> r2 [label="vie ja\nvertaa"];
    }
    c2 -> g2 [label="pull request:\nuusi kuvan tagi"];
    g2 -> a2 [label="agentti hakee"];
  }
  subgraph cluster_p {
    label="työntävä putki"; style="rounded"; margin=10;
    g1 [label="sovellus-\nrepositorio"]; c1 [label="CI-putki\n(klusterin tunnukset)"];
    k1 [label="klusteri"];
    g1 -> c1 [label="push"]; c1 -> k1 [label="helm upgrade"];
  }
}
```

| Ominaisuus | Työntävä putki (CI ajaa `helm upgrade`) | GitOps (agentti vetää) |
|----------------------|----------------------------------------|----------------------------------------|
| Klusterin tunnukset | CI:ssä | vain klusterissa |
| Ajautuminen | jää huomaamatta | korjataan tai hälytetään |
| Historia ja peruminen | putken lokit | Gitin historia, `git revert` |
| Monta klusteria | putki jokaiseen | agentti jokaisessa |

Luvun 11 putki käyttää yksinkertaisuuden vuoksi työntävää mallia.
GitOpsissa sama putki päättyisi pull requestiin, joka päivittää kuvan
tagin käyttöönottorepositorioon.

## Käytännössä

- **Yksi kaavio, ympäristöt arvotiedostoina.** Ei kopioituja
  manifesteja. Ympäristötiedostoissa vain erot.
- **Renderöi ja tarkista putkessa.** `helm lint`, `helm template`,
  skeema- ja käytäntötarkistukset ennen kuin mitään asennetaan.
- **Kaavion versio ja sovelluksen versio ovat eri asioita.**
  Molempia nostetaan semanttisesti.
- **Asetusmuutokset käynnistävät podit uudelleen.** Tiivisteannotaatio
  tai Secretin ja ConfigMapin nimiin lisätty tiiviste.
- **GitOps, kun klustereita tai tiimejä on useita.** Versionhallinnan
  historia on silloin käyttöönottojen kirjanpito, ja klusterin
  tunnukset eivät poistu klusterista. GitOps osana toimitusputkea ja sen
  mittareita on taidossa *Jatkuva integraatio ja toimitus*.

## Itsearviointi

- Osaat rakentaa Helm-kaavion, jossa on oletusarvot,
  ympäristökohtaiset arvotiedostot ja apumallit.
- Osaat renderöidä ja tarkistaa kaavion ilman klusteria ja käyttää
  kultaista tiedostoa regressioiden havaitsemiseen.
- Osaat asentaa, päivittää ja perua Helm-julkaisun.
- Osaat selittää GitOpsin periaatteen ja verrata sitä putkesta
  työnnettyyn käyttöönottoon.
