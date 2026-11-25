# Kehitysympäristöt ja Dev Containers

Toistettava kehitysympäristö koodina ja käyttöohje näiden tutoriaalien
esimerkeille: miten minkä tahansa tutoriaalin esimerkit avataan GitHub
Codespacesissa, VS Coden kehityskontissa, zip-paketista tai ilman
konttia ja miten ne testataan; Dev Containers -määrittely
(`devcontainer.json`), oman projektin kehityskontti, tavallisimmat
ongelmat ja vaihtoehdot (venv ja uv, mise, Nix, virtuaalikoneet). Valmis
dokumentti:
[kehitysymparistot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kehitysymparistot.pdf),
pikaopas:
[kehitysymparistot-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kehitysymparistot-pikaopas.pdf).

Esitiedot: taito *Komentorivi ja Linux*. Dockeria ei tarvitse osata.

## Sisältö

1. Johdanto – miksi ympäristö kuvataan koodina
2. Tutoriaalien esimerkit käyttöön – Codespaces, VS Code, zip, ilman
   konttia, testien ajaminen
3. Dev Containers -määrittely – kuva, ominaisuudet, elinkaarikomennot,
   liitokset, työkalut ja tarkistin
4. Oman projektin kehityskontti – askel askeleelta, sama ympäristö CI:ssä
5. Yleiset ongelmat – omistaja, hitaat liitokset, välimuistit,
   salaisuudet, välityspalvelin, Docker-soketti
6. Vaihtoehdot ja täydentäjät – venv ja uv, asdf ja mise, Nix,
   virtuaalikoneet
7. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/`:

- `projekti/` – pieni Python-projekti *kesto* kehityskontteineen
- `muunnelmat/` – `devcontainer.json`-tiedostoja eri tarpeisiin ja
  kolme virheellistä
- `devkontti.py` – `devcontainer.json`-tiedostojen tarkistin
- `aja_kontissa.py` – rakentaa projektin kehityskontin Dockerilla ja
  ajaa siinä komennon
- `kokoelma.py` – tarkistaa tämän repositorion kaikki kehityskontit ja
  tulostaa paketin tarvitsemat työkalut

```text
make -C esimerkit                        # kaikki tarkistukset
python3 esimerkit/devkontti.py .devcontainer/devcontainer.json
python3 esimerkit/kokoelma.py tyokalut rust
python3 esimerkit/aja_kontissa.py esimerkit/projekti make testaa
```

Kontin rakennus (`make -C esimerkit kontti`) tarvitsee Dockerin ja
ohitetaan, jos Docker ei ole käytettävissä, esimerkiksi tämän
tutoriaalin omassa kehityskontissa.

Lisenssi: CC BY-SA 4.0.
