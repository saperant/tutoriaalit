"""Koosteet: sama taulukko Markdownina ja HTML:nä."""

from __future__ import annotations

import html
from collections.abc import Sequence


# @alku markdown
def markdown(otsikot: Sequence[str],
             rivit: Sequence[Sequence[object]]) -> str:
    """Markdown-taulukko; sarakkeet tasataan tekstinä luettaviksi."""
    solut = [list(otsikot)] + [[str(s) for s in r] for r in rivit]
    leveys = [max(len(r[i]) for r in solut) for i in range(len(otsikot))]

    def rivi(r: list[str]) -> str:
        tasatut = (s.ljust(w) for s, w in zip(r, leveys, strict=True))
        return "| " + " | ".join(tasatut) + " |"

    erotin = "|" + "|".join("-" * (w + 2) for w in leveys) + "|"
    return "\n".join([rivi(solut[0]), erotin] + [rivi(r) for r in solut[1:]])
# @loppu markdown


# @alku html
def html_taulukko(otsikot: Sequence[str],
                  rivit: Sequence[Sequence[object]],
                  korosta: str = "VIRHE") -> str:
    """HTML-taulukko; solu, jossa on sana `korosta`, saa luokan."""
    def solu(arvo: object, tagi: str = "td") -> str:
        teksti = html.escape(str(arvo))
        luokka = ' class="huono"' if korosta in teksti else ""
        return f"<{tagi}{luokka}>{teksti}</{tagi}>"

    osat = ["<table>", "<tr>" + "".join(solu(o, "th") for o in otsikot)
            + "</tr>"]
    osat += ["<tr>" + "".join(solu(s) for s in r) + "</tr>" for r in rivit]
    osat.append("</table>")
    return "\n".join(osat)
# @loppu html
