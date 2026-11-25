# Lopuksi {.runko-lahteet}

Kehitysympäristö on osa ohjelmaa. Kun se kuvataan tiedostona koodin
vieressä, uusi kehittäjä pääsee töihin minuuteissa, CI ajaa samaa
ympäristöä kuin kehittäjät, ja ympäristön muutos on katselmoitava
muutos eikä jonkun koneelle kertynyt salaisuus.

## Nyrkkisäännöt

1. **Ympäristö versionhallintaan.** `devcontainer.json` ja Dockerfile
   kuuluvat repositorioon kuten koodi.
2. **Lukitse versiot.** Kuvat, ominaisuudet, työkalut ja kirjastot.
3. **Yhdet komennot.** Kehittäjä, kontti ja CI ajavat saman
   `make testaa` -komennon.
4. **Kontti on kertakäyttöinen.** Pysyvä tila lähdekoodiin tai
   taltioon, käsin tehdyt asennukset Dockerfileen.
5. **Tavallinen käyttäjä ja vähimmät oikeudet.** Ei rootia, ei
   Docker-sokettia ilman syytä.
6. **Salaisuudet ajon aikana.** Ei kuvaan eikä konfiguraatioon.
7. **Testaa ympäristö.** CI rakentaa kontin tyhjästä ja ajaa testit
   siinä, jolloin rikkinäinen ympäristö huomataan ennen uutta
   kehittäjää.
8. **Kevein riittävä väline.** Virtuaaliympäristö, versionhallitsin,
   kontti, Nix tai virtuaalikone tarpeen mukaan.

## Mitä jäi pois

- **Dockerin käyttö:** kuvien rakentaminen, kerrokset, verkot ja
  Compose (taito *Kontit ja pilvi-infrastruktuuri*).
- **Omien ominaisuuksien ja mallipohjien julkaisu**
  (`devcontainer features` ja `templates`).
- **Codespacesin hallinta organisaatiossa:** esirakennukset, käytännöt
  ja kustannusten seuranta.
- **Etäkehitys SSH:lla** ja muut VS Coden etäkäyttötavat.

## Jatkotaidot

- *Komentorivi ja Linux* on tämän taidon esitieto.
- *Kontit ja pilvi-infrastruktuuri* opettaa kontit ja kuvat
  perusteellisesti.
- *Virtualisointi* selittää, miten kontin eristys ja virtuaalikone
  toimivat.
- *Tietoturva kehitystyössä* käsittelee toistettavat rakennusympäristöt,
  salaisuudet ja toimitusketjun.
- *Integraatiotestaus ja Testcontainers* käynnistää kontteja testeistä
  kehityskontin sisältä.

## Lähteet

- Development Containers. *Development Container Specification* ja
  *devcontainer.json reference.* <https://containers.dev/>
- Development Containers. *Dev Container CLI* (`@devcontainers/cli`).
  <https://github.com/devcontainers/cli>
- Microsoft. *Developing inside a Container* ja *Advanced container
  configuration* (Visual Studio Coden dokumentaatio).
  <https://code.visualstudio.com/docs/devcontainers/containers>
- GitHub. *GitHub Codespaces* -dokumentaatio.
  <https://docs.github.com/codespaces>
- Docker. *Dockerfile reference* ja *Bind mounts.*
  <https://docs.docker.com/>
- Python Software Foundation. *venv — Creation of virtual
  environments.* <https://docs.python.org/3/library/venv.html>
- Astral. *uv*-dokumentaatio. <https://docs.astral.sh/uv/>
- *mise*-dokumentaatio. <https://mise.jdx.dev/>
- *asdf*-dokumentaatio. <https://asdf-vm.com/>
- NixOS Foundation. *Nix Reference Manual.* <https://nixos.org/>
- HashiCorp. *Vagrant*-dokumentaatio.
  <https://developer.hashicorp.com/vagrant>

Lähteitä on käytetty tosiasioiden tarkistamiseen; tekstiä ei ole
kopioitu. Esimerkit käyttävät kehityskonttien peruskuvaa
`mcr.microsoft.com/devcontainers/base` (MIT-lisensoidut määrittelyt,
Ubuntu-pohja) sekä työkaluja pytest (MIT), ruff (MIT) ja mypy (MIT).
Komentorivityökalu `@devcontainers/cli` on MIT-lisensoitu.
