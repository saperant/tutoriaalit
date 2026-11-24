"""CI:n OIDC-luottamus: kuka saa vaihtaa tunnisteen pilvioikeuksiin.

CI-ajo saa lyhytikäisen OIDC-tunnisteen ja vaihtaa sen pilvipalvelun
väliaikaisiin tunnuksiin; pysyviä avaimia ei tarvita. Luottamusehto
ratkaisee, mikä ajo vaihdon saa tehdä. Liian väljä ehto antaa
tuotanto-oikeudet esimerkiksi minkä tahansa haaran tai pull requestin
ajolle.
"""

from fnmatch import fnmatchcase

Vaatimukset = dict[str, str]

# @alku ehdot
EHDOT = {
    "väljä": {"iss": "https://token.actions.githubusercontent.com",
              "aud": "sts.amazonaws.com", "sub": "repo:yritys/*"},
    "tiukka": {"iss": "https://token.actions.githubusercontent.com",
               "aud": "sts.amazonaws.com",
               "sub": "repo:yritys/palvelu:environment:tuotanto"},
}


def sallittu(ehto: Vaatimukset, tunniste: Vaatimukset) -> bool:
    return all(fnmatchcase(tunniste.get(k, ""), malli)
               for k, malli in ehto.items())
# @loppu ehdot


# @alku ajot
def ajo(sub: str) -> Vaatimukset:
    return {"iss": "https://token.actions.githubusercontent.com",
            "aud": "sts.amazonaws.com", "sub": sub}


AJOT = {
    "julkaisu tuotantoympäristöön":
        ajo("repo:yritys/palvelu:environment:tuotanto"),
    "pull request": ajo("repo:yritys/palvelu:pull_request"),
    "kokeiluhaara": ajo("repo:yritys/palvelu:ref:refs/heads/kokeilu"),
    "toinen repositorio": ajo("repo:yritys/harjoitus:ref:refs/heads/main"),
}
# @loppu ajot


def main() -> None:
    for nimi, ehto in EHDOT.items():
        print(f"ehto {nimi}:")
        for kuvaus, tunniste in AJOT.items():
            tulos = "saa oikeudet" if sallittu(ehto, tunniste) else "-"
            print(f"  {kuvaus:30} {tulos}")


if __name__ == "__main__":
    main()
