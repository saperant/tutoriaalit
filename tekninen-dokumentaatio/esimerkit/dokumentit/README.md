# Sääasema

Sääasema kerää lämpötila- ja kosteuslukemia asemilta ja laskee niistä
yhteenvetoja. Se on tarkoitettu pienille mittausverkoille, joissa
asemia on kymmeniä ja lukemia tulee kerran tunnissa.

## Pika-aloitus

Tarvitset Python 3.12:n tai uudemman.

```text
python3 -m saa lukemat.csv --asema kumpula
```

Tuloste kertoo lukemien määrän, vaihteluvälin ja keskiarvon.

## Dokumentaatio

- [Muutosloki](CHANGELOG.md) kertoo, mikä versioiden välillä muuttui.
- [Osallistuminen](CONTRIBUTING.md) kertoo, miten muutos tehdään ja
  testataan.
- [Levy täynnä](kayttoohjeet/levy-taynna.md) on ylläpitäjän toimintaohje
  yleisimpään häiriöön.

## Tuki ja lisenssi

Vikailmoitukset tehdään projektin tikettijärjestelmään. Koodi on
lisensoitu MIT-lisenssillä.
