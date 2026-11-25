# Asynkroniset piirit lyhyesti

Kello on ollut tämän tutoriaalin jokaisen vaiheen suurin kysymys: se
määrää ajoituksen (luku 4), sen jakelu vaatii oman puunsa (luku 8),
ja se kuluttaa suuren osan tehosta (luku 9). Tämä luku katsoo lyhyesti,
mitä tapahtuu, jos kellosta luovutaan. Aihe kuuluu ASIC-toteutukseen,
koska asynkroninen piiri tarvitsee erikoissoluja, joita luvun 2
kirjastossa ei ole, ja koska vuon työkalut olettavat kellon.

Synkroninen piiri jakaa ajan kellojaksoihin, ja jokaisen polun on
valmistuttava pahimmassa kulmassa ennen seuraavaa reunaa. Asynkroninen
piiri luopuu kellosta: vaiheet viestivät keskenään kättelyillä ja
etenevät heti, kun data on valmis. Etuja ovat pieni tehonkulutus
tyhjäkäynnillä (ei kelloa, joka vaihtaa tilaa), sietokyky jännitteen ja
lämpötilan vaihtelulle ja keskimääräinen eikä pahimman tapauksen
nopeus. Hintoja ovat vaikeampi suunnittelu, verifiointi ja testaus,
koska valtavirran työkalut olettavat kellon.

## Kättely ja C-elementti

Nelivaiheinen kättely (four-phase handshake) etenee: lähettäjä nostaa
pyynnön, vastaanottaja nostaa kuittauksen, lähettäjä laskee pyynnön ja
vastaanottaja kuittauksen. Kaksivaiheisessa kättelyssä jokainen
siirtymä on tapahtuma, ja paluu nollaan säästetään.

```{.ajoituskaavio otsikko="Nelivaiheinen kättely: data on voimassa pyynnön noususta kuittauksen nousuun"}
{"signal": [
  {"name": "data", "wave": "x=..x.=..x", "data": ["D1", "D2"]},
  {"name": "pyynto", "wave": "0.1.0..1.0"},
  {"name": "kuittaus", "wave": "0..1.0..1."},
  {"name": "vaihe", "wave": "z3456z3456", "data": ["1", "2", "3", "4", "1", "2", "3", "4"]}
]}
```

Kaaviossa ei ole kelloa: sarakkeet ovat vain tapahtumien järjestys.
Vaiheet 1–4 ovat pyynnön nousu, kuittauksen nousu, pyynnön lasku ja
kuittauksen lasku.

Mullerin C-elementti on asynkronisen suunnittelun perusportti: sen
lähtö seuraa tuloja, kun ne ovat samat, ja muuten muistaa arvonsa.

```{.systemverilog tiedosto="esimerkit/12-muller.sv" osa="c-elementti"}
```

## Muller-liukuhihna

C-elementeistä tehdään liukuhihna, jossa vaihe ottaa uuden datan, kun
edellinen vaihe tarjoaa sitä ja seuraava on tyhjentänyt edellisen.
Data kulkee erillään ohjauksesta (bundled data): se on ehdittävä
salpaan ennen kuin pyyntö etenee, mikä varmistetaan viive-elementillä,
jonka viive on vähintään datapolun viive.

```{.systemverilog tiedosto="esimerkit/12-muller.sv" osa="liukuhihna"}
```

```{.systemverilog tiedosto="esimerkit/12-muller.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/12-muller.odotettu"}
```

Hidas kuluttaja määrää tahdin: liukuhihna täyttyy ja tuottaja odottaa
kuittausta. Kelloa ei ole, mutta kättely ja C-elementit pitävät
järjestyksen.

Bundled data -tekniikan ajoitusoletus on sama kuin synkronisessa
piirissä, mutta paikallinen. Viiveettömät (delay-insensitive)
koodaukset, kuten kaksikiskokoodaus (dual-rail), jossa jokainen bitti
on kaksi johdinta ja valmis-tieto on koodattu dataan, toimivat millä
tahansa porttiviiveillä. Käytännön kompromissi on lähes
viiveetön (quasi delay-insensitive, QDI) suunnittelu.

## Käytännössä

- **Asynkronisuus on harvinaista, mutta ei kuriositeetti.** Sitä
  käytetään erittäin pienen tehon antureissa, kellotusalueiden
  välisissä FIFOissa ja neuromorfisissa piireissä.
- **GALS on yleisempi.** Globaalisti asynkroninen, paikallisesti
  synkroninen piiri koostuu synkronisista saarekkeista, jotka
  keskustelevat asynkronisilla tai tahdistetuilla rajapinnoilla.
- **Työkalut olettavat kellon.** Asynkronisen piirin ajoitus
  tarkistetaan suhteellisina rajoitteina, ja C-elementit ovat usein
  erikoissoluja, joita tavallinen kirjasto ei sisällä.
- **Hasardit ovat virheitä.** Synkronisessa piirissä häiriöpulssi
  ehtii asettua ennen kellon reunaa; asynkronisessa se voi olla
  väärä tapahtuma. Logiikan on oltava hasarditonta.

## Itsearviointi

- Osaat kuvata nelivaiheisen kättelyn ja C-elementin toiminnan.
- Osaat selittää Muller-liukuhihnan ja bundled data -oletuksen.
- Osaat vertailla asynkronista ja synkronista suunnittelua tehon,
  nopeuden ja suunnittelutyön kannalta.
