# Johdanto {.runko-johdanto}

”Minun koneellani se toimii” on ohjelmistokehityksen vanhimpia
vikailmoituksia. Ohjelma riippuu kääntäjän versiosta, kirjastoista,
ympäristömuuttujista ja käyttöjärjestelmästä, ja jokaisen kehittäjän
koneella ne ovat vähän erilaiset. Uusi kehittäjä käyttää ensimmäisen
päivänsä asennusohjeen seuraamiseen, ja ohje on vanhentunut jo ennen
kuin hän pääsee sen loppuun.

Ratkaisu on kuvata kehitysympäristö tiedostona, joka on
versionhallinnassa koodin vieressä. Ympäristö rakennetaan tiedostosta
automaattisesti, joten se on sama jokaisella kehittäjällä ja
CI-palvelimella, ja se muuttuu vain katselmoidun muutoksen kautta.
*Dev Containers* on tähän tarkoitettu avoin määrittely: tiedosto
`devcontainer.json` kertoo, mistä kontista ympäristö tehdään ja miten
editori siihen liittyy.

```{.dot otsikko="Sama tiedosto tuottaa saman ympäristön kolmella työkalulla"}
digraph {
  rankdir=LR; nodesep=0.25;
  tiedosto [label="devcontainer.json\n(+ Dockerfile)"];
  vscode [label="VS Code\nomalla koneella"];
  codespaces [label="GitHub Codespaces\npilvessä"];
  cli [label="devcontainer-komento\nCI:ssä"];
  kontti [label="kontti:\ntyökalut asennettuina,\nlähdekoodi liitettynä"];
  tiedosto -> vscode; tiedosto -> codespaces; tiedosto -> cli;
  vscode -> kontti; codespaces -> kontti; cli -> kontti;
}
```

Tällä tutoriaalilla on kaksi tehtävää:

1. **Käyttöohje näiden tutoriaalien esimerkeille.** Jokaisella
   tutoriaalilla on oma kehityskonttinsa. Luku 2 kertoo, miten
   esimerkit saa auki selaimessa, omalla koneella kontissa tai ilman
   konttia ja miten ne ajetaan ja testataan.
2. **Yleinen taito.** Luvut 3–6 opettavat määrittelyn, oman projektin
   kehityskontin rakentamisen, tavallisimmat ongelmat ja vaihtoehdot.

Jos haluat vain päästä kokeilemaan jonkin tutoriaalin esimerkkejä, lue
luku 2 ja palaa loppuun myöhemmin.

## Kontti lyhyesti

*Kontti* on eristetty prosessiryhmä, jolla on oma tiedostojärjestelmänsä.
Tiedostojärjestelmä tulee *kuvasta* (image), joka sisältää
käyttöjärjestelmän kirjastot ja asennetut työkalut. Kuva rakennetaan
reseptistä, jota kutsutaan *Dockerfileksi*. Kontti käynnistyy sekunneissa,
koska se käyttää isäntäkoneen ydintä eikä käynnistä omaa
käyttöjärjestelmää.

Tämän tutoriaalin lukemiseen riittää tuo kuva: kontti on laatikko, jossa
työkalut ovat valmiina, ja lähdekoodisi näkyy laatikon sisällä.
Dockerin komentoja ei tarvitse osata. Kuvien rakentamisen ja konttien
ajamisen opettaa taito *Kontit ja pilvi-infrastruktuuri*, ja eristyksen toteutuksen
ytimessä taito *Virtualisointi*.

## Esitiedot ja rajaus

Osaat liikkua komentorivillä ja ajaa komentoja (taito *Komentorivi ja
Linux*). Oman koneen kehityskontteihin tarvitset Dockerin tai muun
konttiajurin ja Visual Studio Coden; selaimessa toimivaan
Codespacesiin riittää GitHub-tili.

## Esimerkit

Tutoriaalin esimerkit ovat hakemistossa `esimerkit/`:

- `projekti/`: pieni Python-projekti kehityskontteineen (luku 4),
- `muunnelmat/`: `devcontainer.json`-tiedostoja eri tarpeisiin ja
  kolme virheellistä (luku 3),
- `devkontti.py`: tiedostojen tarkistin,
- `aja_kontissa.py`: rakentaa projektin kontin Dockerilla ja ajaa
  siinä komennon,
- `kokoelma.py`: tarkistaa tämän tutoriaalikokoelman kaikki
  kehityskontit.

Komento `make -C esimerkit` ajaa kaikki tarkistukset. Kontin rakennus
ohitetaan, jos Docker ei ole käytettävissä.
