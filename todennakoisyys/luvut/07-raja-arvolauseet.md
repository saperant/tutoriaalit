# Raja-arvolauseet

Kaksi lausetta selittää, miksi tilastotiede toimii. *Suurten lukujen
laki* takaa, että otoskeskiarvo lähestyy odotusarvoa. *Keskeinen
raja-arvolause* kertoo, millä tavalla se lähestyy: keskiarvon virhe on
likimain normaalijakautunut, ja sen hajonta pienenee kuten
$\sigma/\sqrt{n}$.

## Suurten lukujen laki

Kun riippumattomia, samoin jakautuneita havaintoja on $n$ kappaletta,
niiden keskiarvo $\bar X_n$ lähestyy odotusarvoa $\mu$. Nopanheittojen
keskiarvo hakeutuu kohti arvoa 3,5:

```{.python tiedosto="esimerkit/07-suuret-luvut.py" osa="keskiarvo"}
```

Laki edellyttää, että odotusarvo on olemassa. Cauchyn jakaumalla sitä
ei ole: yksittäiset äärimmäiset arvot heittävät keskiarvoa vielä
miljoonan havainnon jälkeenkin.

```{.python tiedosto="esimerkit/07-suuret-luvut.py" osa="cauchy"}
```

```{.tuloste tiedosto="esimerkit/07-suuret-luvut.odotettu"}
```

Cauchy on ääriesimerkki, mutta sama ilmiö näkyy lievempänä
raskashäntäisissä aineistoissa, kuten vasteajoissa ja tiedostojen
koissa: harvinainen jättiarvo hallitsee keskiarvoa.

## Keskeinen raja-arvolause

Riippumattomien muuttujien summa on suurella $n$:llä likimain
normaalijakautunut lähes alkuperäisestä jakaumasta riippumatta, kunhan
varianssi on äärellinen. Tasajakautuneiden lukujen summa näyttää jo
kahdellatoista termillä normaalijakaumalta. Tekstihistogrammi
piirretään NumPyn `histogram`-funktiolla:

```{.python tiedosto="esimerkit/07-raja-arvo.py" osa="histogrammi"}
```

```{.python tiedosto="esimerkit/07-raja-arvo.py" osa="summat"}
```

Lähestyminen on hitaampaa, jos jakauma on vino. Eksponenttijakauman
vinous on 2, ja summan vinous pienenee vain kuten $2/\sqrt{n}$:

```{.python tiedosto="esimerkit/07-raja-arvo.py" osa="vino"}
```

```{.tuloste tiedosto="esimerkit/07-raja-arvo.odotettu"}
```

Keskeinen raja-arvolause on luottamusvälien ja monen testin perusta.
Kun aineisto on vino, ”suuri $n$” voi tarkoittaa satoja havaintoja.

## Käytännössä

- **Keskiarvoista riippumattomia havaintoja.** Keskiarvon epävarmuus
  pienenee kuten $1/\sqrt{n}$: kymmenkertainen tarkkuus vaatii
  satakertaisen määrän mittauksia.
- **Varo raskaita häntiä.** Jos aineistossa on harvinaisia jättiarvoja,
  keskiarvo heiluu ja raja-arvolause toteutuu hitaasti. Käytä
  mediaania tai persentiilejä.
- **Tarkista vinous ennen normaalioletusta.** Vino jakauma tarvitsee
  enemmän havaintoja, ennen kuin normaaliapproksimaatio pitää.
- **Muista riippumattomuus.** Peräkkäiset mittaukset samasta
  järjestelmästä korreloivat usein, jolloin tehollinen otoskoko on
  pienempi kuin havaintojen määrä.

## Itsearviointi

- Osaat selittää suurten lukujen lain ja sen edellytykset sekä
  näyttää simuloimalla, milloin se ei päde.
- Osaat selittää keskeisen raja-arvolauseen ja sen merkityksen
  keskiarvon epävarmuudelle.
- Osaat arvioida, kuinka monta havaintoa normaaliapproksimaatio
  tarvitsee vinolla jakaumalla.
