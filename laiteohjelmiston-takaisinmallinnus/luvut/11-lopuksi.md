# Lopuksi {.runko-lahteet}

Tämä paketti eteni raa'asta binäärikuvasta sen muodon ja arkkitehtuurin
tunnistukseen, koodin lukemiseen ja laitteen ajamiseen emulaattorissa.
Punaisena lankana oli, että takaisinmallinnus on ymmärryksen työkalu:
jokaisessa luvussa selvitettiin, mitä LT-100-laite tekee, ja
samalla nähtiin, mikä sen suojauksissa pettää ja miten se korjataan.

## Puolustuksen yhteenveto

Analyysi paljasti laitteesta useita heikkouksia, joista jokaisella on
oikea korjaus:

| Heikkous | Miksi pettää | Korjaus |
|----------|--------------|---------|
| CRC aitoustakuuna | hyökkääjä laskee CRC:n uudelleen | allekirjoitus julkisella avaimella |
| kovakoodattu jaettu avain | näkyy jokaisessa kuvassa | laitekohtainen avain suojatussa varastossa |
| avoin debug-portti | antaa täyden pääsyn | portin lukitus ja piirin lukkobitti |
| tarkistamaton jäsennin | puskurin ylivuoto | pituustarkistus ennen kopiointia |
| allekirjoittamaton päivitys | kuka tahansa muuttaa | allekirjoitettu ja versioitu päivitys |

Korjausten toteutus — luottamusketju, allekirjoitukset, avainvarastot,
debug-lukitus ja salaus — on taidossa *Sulautettujen järjestelmien
tietoturva*. Takaisinmallinnuksen rooli puolustuksessa on osoittaa,
mikä pettää ja miksi, jotta korjaus kohdistuu oikein. Hyvä sääntö:
suojaus, joka perustuu salaamiseen tai hämäryyteen, ei kestä
takaisinmallinnusta; vain kryptografiaan ja pääsynvalvontaan perustuva
suojaus kestää.

## Ghidra ja muut työkalut

Tässä paketissa käytettiin radare2:ta, objdumpia, gdb:tä, QEMU:ta ja
Unicornia, koska ne ovat kevyitä ja skriptattavia. Ammattityössä
yleisin kehys on **Ghidra**, NSA:n avoimeksi julkaisema
takaisinmallinnusalusta, jonka dekompilaattori on avoimista paras ja
joka tukee lukuisia arkkitehtuureja, myös ARM/Thumbia. Ghidra osaa
tuoda raa'an kuvan annettuun latausosoitteeseen, soveltaa SVD-kuvausta
oheislaitteiden nimeämiseen ja ajaa skriptejä (`analyzeHeadless`)
eräajona. Tämän paketin työkaluilla tehdyt päättelyt — latausosoite,
oheislaitekartta, funktioiden ja algoritmien tunnistus — vastaavat
sitä, minkä Ghidra tekee automaattisesti; käsin tehtynä ne opettavat,
mihin työkalun automaatio perustuu. Muita työkaluja ovat kaupallinen
IDA Pro, sen Hex-Rays-dekompilaattori ja radare2:n haara Rizin
graafisella Cutter-käyttöliittymällä.

Laitteiston puolella fyysiseen analyysiin kuuluvat
logiikka-analysaattori (SPI-, I2C- ja UART-väylien kuuntelu),
JTAG/SWD-sovittimet (esim. OpenOCD) ja flash-muistin lukeminen suoraan
piiriltä. Nämä vaativat laitteiston, joten ne jäivät tämän paketin
ulkopuolelle, mutta periaatteet ovat samat: hae kuva, tunnista
arkkitehtuuri, lue koodi, aja emulaattorissa.

## Miten jatkaa

Taitoa harjoittaa parhaiten omilla laitteilla ja avoimilla kohteilla:

- **CTF-tapahtumat.** Monessa CTF-kilpailussa on sulautettuja ja
  laitteisto-osioita (*embedded*, *hardware*, *rev*). Tapahtumat ja
  tulokset ovat sivustolla CTFtime.org. CTF-tehtävät ovat laillisia
  harjoituskohteita, jotka on tehty ratkaistaviksi.
- **Avoin laiteohjelmisto.** Zephyr, RIOT ja Apache NuttX ovat avoimia
  sulautettuja käyttöjärjestelmiä, joiden kuvia voi kääntää itse ja
  tutkia lähdekoodi vieressä — paras tapa harjoitella, koska vastaus on
  saatavilla. Reititin- ja IoT-puolella OpenWrt on avoin ja hyvin
  dokumentoitu.
- **Oma laite.** Käännä itse tehty laiteohjelmisto (esim.
  *Mikrokontrollerit*-taidon esimerkit), riisu symbolit ja tutki sitä
  kuin tuntematonta. Vertaa päättelyäsi lähdekoodiin.

Muista rajat: vieraan laitteen tai kaupallisen tuotteen suojausten
kiertäminen ilman lupaa ei kuulu näihin harjoituksiin, ja
tietoturvaheikkoudet ilmoitetaan vastuullisesti valmistajalle.

## Lähitaidot taitopuussa

*Takaisinmallinnus* on tämän paketin suora esitieto (x86-64, ELF,
työkalut) ja *Mikrokontrollerit ja bare-metal-ohjelmointi* antaa
Cortex-M:n perustan. *Objektitiedostot, linkitys ja ABI* selittää
ELF:n, symbolit ja linkkerin osakarsinnan. *Sulautettujen järjestelmien
tietoturva* kattaa korjaukset: turvallisen käynnistyksen,
allekirjoitukset, avainvarastot ja debug-lukituksen. *Haavoittuvuuksien
analyysi ja hyödyntäminen* syventää muistiturvallisuuden virheet.
*Oheislaiteväylät* ja *Reaaliaikakäyttöjärjestelmät* auttavat
tunnistamaan väylä- ja RTOS-rakenteita laiteohjelmistosta.

## Lähteet

- Joseph Yiu: *The Definitive Guide to Arm Cortex-M3 and Cortex-M4
  Processors*. Newnes, 2014 (vektoritaulu, poikkeukset, SCS).
- ARM: *ARMv7-M Architecture Reference Manual* ja *ARM Architecture
  Procedure Call Standard (AAPCS)*. developer.arm.com.
- Dennis Andriesse: *Practical Binary Analysis*. No Starch Press, 2019.
- radare2-dokumentaatio: book.rada.re. Ghidra: ghidra-sre.org.
- QEMU-dokumentaatio (System emulation, Arm System emulator):
  qemu.org. Unicorn Engine: unicorn-engine.org. Capstone:
  capstone-engine.org.
- Euroopan parlamentin ja neuvoston direktiivi 2009/24/EY
  tietokoneohjelmien oikeudellisesta suojasta (6 artikla, dekompilointi)
  ja tekijänoikeuslaki 404/1961, 25 j ja 25 k § (finlex.fi).

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
