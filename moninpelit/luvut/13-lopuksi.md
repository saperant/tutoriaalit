# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Palvelin on auktoriteetti; asiakas lähettää aikeita, ei
   lopputuloksia.
2. Tila epäluotettavasti UDP:llä, tärkeät tapahtumat oman
   luotettavuuskerroksen kautta. Ei koko peliä TCP:llä.
3. Yhteys alkaa haasteella: palvelin ei varaa mitään varmistamattomalle
   osoitteelle. Sekvenssinumerot kiertävät: vertaa etumerkillisellä
   erotuksella.
4. Kuittaukset vastakkaisen liikenteen mukana kuittauskenttänä.
5. Vedokset kvantisoituna, deltana kuitattuun vedokseen ja vain
   kiinnostusalueelta.
6. Oma hahmo ennustetaan ja täsmäytetään; syötteet toistetaan
   paketeissa, ja asiakkaan tikit pidetään palvelimen edellä tahtia
   säätämällä.
7. Muut pelaajat interpoloidaan kahden vedosvälin ja värinän
   puskurilla.
8. Osumat ratkaistaan kelaamalla ampujan näkemään hetkeen, ylärajan
   kanssa.
9. Lukitusaskel ja rollback vaativat täydellisen determinismin;
   tarkistussumma paljastaa eriytymisen.
10. Mitä ei lähetetä, sitä ei voi huijata esiin.
11. Testaa simuloidulla huonolla verkolla, kiinteällä siemenellä.

## Mallit

| Malli | Ratkaisee | Luku |
|-------|-----------|------|
| palvelimen auktoriteetti | huijaaminen, eriävä tila | Arkkitehtuurit |
| haaste kättelyssä | väärennetyt lähdeosoitteet | Luotettavuuskerros |
| kuittauskenttä | luotettavuus ilman erillisiä kuittauksia | Luotettavuuskerros |
| delta kuitattuun vedokseen | kaista | Tilan synkronointi |
| kiinnostusalue | kaista ja tiedon rajaus | Tilan synkronointi |
| asiakkaan ennustus ja täsmäytys | oman ohjauksen viive | Ennustus |
| tahdin säätö palautteesta | myöhästyvät syötteet | Ennustus |
| entiteettien interpolointi | muiden pelaajien nykiminen | Interpolointi |
| takaisinkelaus | osumat viiveellä | Viiveen kompensointi |
| lukitusaskel | suuri tila, pieni kaista | Lukitusaskel |
| rollback | syöteviive taistelupeleissä | Lukitusaskel |
| syötebudjetti | nopeushuijaus, tulvitus | Huijaamisen esto |
| laajeneva haku | otteluiden muodostus | Pelipalvelimet |

## Mihin tästä eteenpäin

- *Verkko-ohjelmointi*: soketit, tapahtumasilmukat, protokollien
  suunnittelu ja vikasietoisuus syvemmin.
- *Hajautetut järjestelmät* ja *Skaalautuvien järjestelmien suunnittelu*:
  pelipalvelinten taustajärjestelmät, skaalaus ja tietokannat.
- *Kontit ja pilvi-infrastruktuuri*: pelipalvelinten ajaminen konteissa
  ja klustereissa.
- *Web-sovellusten tietoturva* ja *Palveluarkkitehtuurin tietoturva*:
  todennus ja palvelinten suojaus.

## Lähteet ja lisälukemista

- Glenn Fiedler: *Networking for Game Programmers*, *Networked
  Physics* ja *Building a Game Network Protocol*.
  <https://gafferongames.com/>. Kuittauskenttä, vedokset ja
  delta-pakkaus.
- Yahn Bernier: *Latency Compensating Methods in Client/Server In-game
  Protocol Design and Optimization*. Game Developers Conference 2001.
  Viiveen kompensoinnin klassikko (Valve).
- Valve Developer Community: *Source Multiplayer Networking*.
  <https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking>.
- Gabriel Gambetta: *Fast-Paced Multiplayer*.
  <https://www.gabrielgambetta.com/client-server-game-architecture.html>.
  Ennustus, täsmäytys ja interpolointi havainnollisesti.
- Mark Terrano ja Paul Bettner: *1500 Archers on a 28.8: Network
  Programming in Age of Empires and Beyond*. Gamasutra, 2001.
  Lukitusaskeleen perusteos.
- Tony Cannon: GGPO-rollback-kirjasto ja dokumentaatio.
  <https://www.ggpo.net/>. MIT-lisensoitu.
- Timothy Ford: *Overwatch Gameplay Architecture and Netcode*. GDC 2017.
- Mark E. Glickman: *The Glicko System* ja *Example of the Glicko-2
  System*. <http://www.glicko.net/>.
- Arpad Elo: *The Rating of Chessplayers, Past and Present*. Arco, 1978.
- Valmiit kirjastot: ENet (<http://enet.bespin.org/>, MIT),
  yojimbo (<https://github.com/mas-bandwidth/yojimbo>, BSD) ja
  GameNetworkingSockets (<https://github.com/ValveSoftware/GameNetworkingSockets>,
  BSD).
- Agones: pelipalvelimet Kubernetesissa. <https://agones.dev/>.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien koodi on samalla
lisenssillä.
