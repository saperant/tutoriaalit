"""Koodin tuottaminen: tilakone ja datapolku Verilogina (FSMD).

Jokainen lehti on tilakoneen tila. Tilan sisällä laskuri ks kertoo
jakson aloitusvälin sisällä ja bittivektori v, mitkä liukuhihnan
vaiheet ovat käytössä. Datapolun operaatiot ovat jatkuvia johtoja;
rekisterit, muistiportit ja virrat ohjataan jakson aktiivisuussignaalilla.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .dfg import Jako, Operandi, Solmu, Vakaa, Vakio
from .muunnokset import Lehti, Ulompi
from .puu import Funktio, KaannosVirhe
from .sidonta import Lehtiajoitus, rekisterit


def bitit(maara: int) -> int:
    """Leveys, jolla esitetään arvot 0 ... maara - 1."""
    return max(1, (maara - 1).bit_length())


def vakio(arvo: int, leveys: int = 32) -> str:
    if leveys == 1:
        return f"1'b{arvo & 1}"
    return f"32'sd{arvo}" if arvo >= 0 else f"-32'sd{-arvo}"


def rekisterinimi(nimi: str) -> str:
    """Muuttuja s -> m_s, paikallisen taulukon alkio z[3] -> m_z_3."""
    return "m_" + nimi.replace("[", "_").replace("]", "")


@dataclass(frozen=True)
class Portti:
    """Muistipankin portti: taulukko, pankki, luku- tai kirjoitusportti."""
    taulu: str
    pankki: int
    kirjoitus: bool


class Tuottaja:
    def __init__(self, f: Funktio, jaot: dict[str, Jako],
                 lehdet: list[Lehtiajoitus], rakenne: list[Lehti | Ulompi],
                 kartta: dict[int, Lehtiajoitus],
                 kertojat: dict[int, int]) -> None:
        self.f, self.jaot, self.lehdet = f, jaot, lehdet
        self.rakenne, self.kartta, self.kertojat = rakenne, kartta, kertojat
        self.datapolku: list[str] = []
        self.rekisterit: list[str] = []
        self.paivitykset: list[str] = []
        self.aktiiviset: set[tuple[int, int]] = set()
        self.portit: dict[Portti, list[tuple[str, str, str]]] = {}
        self.virrat: dict[str, list[tuple[str, str]]] = {}
        self.virtasuunta: dict[str, str] = {}
        self.yksikot: dict[int, list[tuple[str, str, str]]] = {}
        self.muuttujat: set[str] = set()
        self.ulommat: list[Ulompi] = []

    # --- apufunktiot ----------------------------------------------------
    def pankit(self, taulu: str) -> tuple[int, int]:
        p = self.f.parametri(taulu)
        koko = p.koko if p is not None else self.f.paikalliset[taulu]
        jako = self.jaot.get(taulu, Jako("none"))
        maara = 1 if jako.laji == "none" else jako.tekija
        return maara, koko // maara

    def pankin_nimi(self, taulu: str, pankki: int) -> str:
        maara, _ = self.pankit(taulu)
        return taulu if maara == 1 else f"{taulu}_{pankki}"

    def aktiivisuus(self, lehti: Lehtiajoitus, jakso: int) -> str:
        self.aktiiviset.add((lehti.numero, jakso))
        return f"l{lehti.numero}_j{jakso}"

    def operandi(self, lehti: Lehtiajoitus, o: Operandi, jakso: int,
                 leveys: int = 32) -> str:
        """Operandin lähde jaksolla jakso: johto, jos arvo valmistuu
        samalla jaksolla, muuten vaiherekisteri."""
        if isinstance(o, Vakio):
            return vakio(o.arvo, leveys)
        if isinstance(o, Vakaa):
            return o.nimi
        if lehti.t.johto[o.solmu] == jakso:
            return f"t{o.solmu}"
        return f"t{o.solmu}_v{lehti.vaihe(jakso)}"

    def lopussa(self, lehti: Lehtiajoitus) -> str:
        """Kierroksen viimeinen jakso: vaiheet siirtyvät eteenpäin."""
        tila = f"tila == S_{lehti.nimi.upper()}"
        if lehti.ii == 1:
            return tila
        return f"{tila} && l{lehti.numero}_ks == {lehti_ks(lehti)}"

    # --- datapolku ------------------------------------------------------
    # @alku datapolku
    def lehti(self, lehti: Lehtiajoitus) -> None:
        g, t = lehti.g, lehti.t
        self.datapolku.append(f"    // {lehti.nimi}: II {lehti.ii}, "
                              f"vaiheita {lehti.vaiheet}")
        for i in sorted(g.solmut):
            s = g.solmut[i]
            jakso = t.jakso[i]
            lauseke = self.lauseke(lehti, s, jakso)
            if lauseke is not None:
                leveys = "signed [31:0] " if s.leveys == 32 else ""
                self.datapolku.append(f"    wire {leveys}t{i} = {lauseke};")
            self.vaikutus(lehti, s, jakso)
        for i, (ensin, viimeinen) in sorted(rekisterit(lehti).items()):
            leveys = "signed [31:0] " if g.solmut[i].leveys == 32 else ""
            for vaihe in range(ensin, viimeinen + 1):
                self.rekisterit.append(f"    reg {leveys}t{i}_v{vaihe};")
            ehto = self.aktiivisuus(lehti, t.johto[i])
            self.paivitykset.append(f"        if ({ehto}) t{i}_v{ensin} "
                                    f"<= t{i};")
            for vaihe in range(ensin + 1, viimeinen + 1):
                self.paivitykset.append(
                    f"        if ({self.lopussa(lehti)}) t{i}_v{vaihe} "
                    f"<= t{i}_v{vaihe - 1};")
    # @loppu datapolku

    def lauseke(self, lehti: Lehtiajoitus, s: Solmu,
                jakso: int) -> str | None:
        def o(n: int) -> str:
            leveys = 1 if s.leveys == 1 and s.laji not in VERTAILU else 32
            return self.operandi(lehti, s.syotteet[n], jakso, leveys)

        laji = s.laji
        if laji == "iteraatio":
            n = f"{{{32 - bitit(lehti.kierrokset)}'d0, l{lehti.numero}_n}}"
            if (lehti.alku, lehti.askel) == (0, 1):
                return n
            return f"{vakio(lehti.alku)} + {vakio(lehti.askel)} * {n}"
        if laji == "muuttuja":
            self.muuttujat.add(s.kohde)
            return rekisterinimi(s.kohde)
        if laji == "lataa":
            return f"{self.pankin_nimi(s.kohde, s.pankki)}_q0"
        if laji == "lue_virta":
            return f"{s.kohde}_TDATA"
        if laji == "*" and s.id in self.kertojat:
            yksikko = self.kertojat[s.id]
            if sum(1 for v in self.kertojat.values() if v == yksikko) > 1:
                ehto = self.aktiivisuus(lehti, jakso)
                self.yksikot.setdefault(yksikko, []).append((ehto, o(0),
                                                             o(1)))
                return f"mul{yksikko}_y"
        if laji == ">>":
            return f"{o(0)} >>> {o(1)}"
        if laji == "laajenna":
            bitti = self.operandi(lehti, s.syotteet[0], jakso, 1)
            return f"{{31'd0, {bitti}}}"
        if laji == "valinta":
            ehto = self.operandi(lehti, s.syotteet[0], jakso, 1)
            return f"{ehto} ? {o(1)} : {o(2)}"
        if laji == "~":
            return f"~{o(0)}"
        if laji in BINAARISET:
            return f"{o(0)} {laji} {o(1)}"
        return None

    def vaikutus(self, lehti: Lehtiajoitus, s: Solmu, jakso: int) -> None:
        """Rekisterit, muistiportit ja virrat, joita solmu ohjaa."""
        if s.laji in ("kirjoita", "palauta"):
            kohde = "ap_return" if s.laji == "palauta" else \
                rekisterinimi(s.kohde)
            if s.laji == "kirjoita":
                self.muuttujat.add(s.kohde)
            arvo = self.operandi(lehti, s.syotteet[0], jakso, s.leveys)
            ehto = self.aktiivisuus(lehti, jakso)
            self.paivitykset.append(f"        if ({ehto}) {kohde} <= {arvo};")
        elif s.laji in ("lataa", "tallenna"):
            portti = Portti(s.kohde, s.pankki, s.laji == "tallenna")
            _, koko = self.pankit(s.kohde)
            osoite = self.osoite(lehti, s.syotteet[0], jakso, bitit(koko))
            ehto = self.aktiivisuus(lehti, jakso)
            if s.ehto is not None:
                ehto = f"{ehto} && {self.operandi(lehti, s.ehto, jakso, 1)}"
            data = "" if s.laji == "lataa" else \
                self.operandi(lehti, s.syotteet[1], jakso)
            self.portit.setdefault(portti, []).append((ehto, osoite, data))
        elif s.laji in ("lue_virta", "kirjoita_virta"):
            suunta = "sisaan" if s.laji == "lue_virta" else "ulos"
            if self.virtasuunta.setdefault(s.kohde, suunta) != suunta:
                raise KaannosVirhe(s.rivi, f"virtaa {s.kohde} sekä luetaan "
                                   "että kirjoitetaan")
            data = "" if suunta == "sisaan" else \
                self.operandi(lehti, s.syotteet[0], jakso)
            ehto = self.aktiivisuus(lehti, jakso)
            self.virrat.setdefault(s.kohde, []).append((ehto, data))

    def osoite(self, lehti: Lehtiajoitus, o: Operandi, jakso: int,
               leveys: int) -> str:
        if isinstance(o, Vakio):
            return f"{leveys}'d{o.arvo}"
        return f"{self.operandi(lehti, o, jakso)}[{leveys - 1}:0]"

    # --- tilakone -------------------------------------------------------
    def tilat(self) -> list[str]:
        return ["S_IDLE", *(f"S_{x.nimi.upper()}" for x in self.lehdet),
                "S_DONE"]

    def aloita(self, alue: Lehti | Ulompi, sisennys: str) -> list[str]:
        while isinstance(alue, Ulompi):
            alue = alue.runko[0]
        lehti = self.kartta[id(alue)]
        rivit = [f"{sisennys}tila <= S_{lehti.nimi.upper()};"]
        if lehti.kierrokset > 1:
            rivit.append(f"{sisennys}l{lehti.numero}_n <= 0;")
        if lehti.ii > 1:
            rivit.append(f"{sisennys}l{lehti.numero}_ks <= 0;")
        if lehti.vaiheet > 1:
            rivit.append(f"{sisennys}l{lehti.numero}_v <= 1;")
        return rivit

    # @alku siirtyma
    def jatko(self, polku: list[tuple[list[Lehti | Ulompi], int, Ulompi |
                                      None]], sisennys: str) -> list[str]:
        """Siirtymä lehden jälkeen: seuraava alue, ulomman silmukan
        seuraava kierros tai lopetus."""
        alueet, kohta, vanhempi = polku[-1]
        if kohta + 1 < len(alueet):
            return self.aloita(alueet[kohta + 1], sisennys)
        if vanhempi is None:
            return [f"{sisennys}tila <= S_DONE;"]
        m = rekisterinimi(vanhempi.muuttuja)
        viimeinen = vanhempi.alku + vanhempi.askel * (vanhempi.kierrokset - 1)
        return [f"{sisennys}if ({m} != {vakio(viimeinen)}) begin",
                f"{sisennys}    {m} <= {m} + {vakio(vanhempi.askel)};",
                *self.aloita(vanhempi.runko[0], sisennys + "    "),
                f"{sisennys}end else begin",
                f"{sisennys}    {m} <= {vakio(vanhempi.alku)};",
                *self.jatko(polku[:-1], sisennys + "    "),
                f"{sisennys}end"]
    # @loppu siirtyma

    def ohjaus(self) -> list[str]:
        rivit: list[str] = []
        ulommat: list[Ulompi] = []

        def kay(alueet: list[Lehti | Ulompi], polku: list[tuple[
                list[Lehti | Ulompi], int, Ulompi | None]]) -> None:
            for kohta, alue in enumerate(alueet):
                if isinstance(alue, Ulompi):
                    ulommat.append(alue)
                    kay(alue.runko, [*polku[:-1], (alueet, kohta,
                                                   polku[-1][2]),
                                     (alue.runko, 0, alue)])
                    continue
                oma = [*polku[:-1], (alueet, kohta, polku[-1][2])]
                rivit.extend(self.tilan_ohjaus(self.kartta[id(alue)], oma))

        kay(self.rakenne, [(self.rakenne, 0, None)])
        alku = ["            S_IDLE: if (ap_start) begin"]
        alku += [f"                {rekisterinimi(u.muuttuja)} <= "
                 f"{vakio(u.alku)};" for u in ulommat]
        alku += self.aloita(self.rakenne[0], "                ")
        alku.append("            end")
        self.ulommat = ulommat
        return alku + rivit + ["            S_DONE: tila <= S_IDLE;",
                               "            default: tila <= S_IDLE;"]

    def tilan_ohjaus(self, lehti: Lehtiajoitus, polku: list[tuple[
            list[Lehti | Ulompi], int, Ulompi | None]]) -> list[str]:
        k, s = lehti.numero, "                "
        rivit = [f"            S_{lehti.nimi.upper()}: begin"]
        if lehti.ii > 1:
            rivit += [f"{s}l{k}_ks <= l{k}_ks == {lehti_ks(lehti)} ? "
                      f"{bitit(lehti.ii)}'d0 : l{k}_ks + 1'b1;",
                      f"{s}if (l{k}_ks == {lehti_ks(lehti)}) begin"]
            s += "    "
        n = f"l{k}_n"
        viimeinen = f"{bitit(lehti.kierrokset)}'d{lehti.kierrokset - 1}"
        if lehti.vaiheet == 1:
            if lehti.kierrokset == 1:
                rivit += self.jatko(polku, s)
            else:
                rivit += [f"{s}if ({n} != {viimeinen}) {n} <= {n} + 1'b1;",
                          f"{s}else begin",
                          *self.jatko(polku, s + "    "), f"{s}end"]
        else:
            seur = f"l{k}_vs"
            rivit += [f"{s}l{k}_v <= {seur};",
                      f"{s}if (l{k}_uusi) {n} <= {n} + 1'b1;",
                      f"{s}if ({seur} == 0) begin",
                      *self.jatko(polku, s + "    "), f"{s}end"]
        if lehti.ii > 1:
            rivit.append(f"{s[:-4]}end")
        rivit.append("            end")
        return rivit

    def laskurit(self) -> list[str]:
        rivit = []
        for x in self.lehdet:
            k = x.numero
            if x.kierrokset > 1:
                rivit.append(f"    reg [{bitit(x.kierrokset) - 1}:0] "
                             f"l{k}_n;")
            if x.ii > 1:
                rivit.append(f"    reg [{bitit(x.ii) - 1}:0] l{k}_ks;")
            if x.vaiheet > 1:
                rivit.append(f"    reg [{x.vaiheet - 1}:0] l{k}_v;")
                viimeinen = f"{bitit(x.kierrokset)}'d{x.kierrokset - 1}"
                rivit.append(f"    wire l{k}_uusi = l{k}_v[0] && "
                             f"l{k}_n != {viimeinen};")
                vanhat = "" if x.vaiheet == 1 else \
                    f"l{k}_v[{x.vaiheet - 2}:0], "
                rivit.append(f"    wire [{x.vaiheet - 1}:0] l{k}_vs = "
                             f"{{{vanhat}l{k}_uusi}};")
        return rivit

    def aktiivisuussignaalit(self) -> list[str]:
        rivit = []
        for k, jakso in sorted(self.aktiiviset):
            x = self.lehdet[k - 1]
            ehdot = [f"tila == S_{x.nimi.upper()}"]
            if x.ii > 1:
                ehdot.append(f"l{k}_ks == {bitit(x.ii)}'d{jakso % x.ii}")
            if x.vaiheet > 1:
                ehdot.append(f"l{k}_v[{x.vaihe(jakso)}]")
            rivit.append(f"    wire l{k}_j{jakso} = {' && '.join(ehdot)};")
        return rivit

    # --- rajapinta ------------------------------------------------------
    def rajapinta(self) -> tuple[list[str], list[str]]:
        """Porttiluettelo ja porttien kytkennät (assign)."""
        portit = ["input  wire               clk",
                  "input  wire               rst",
                  "input  wire               ap_start",
                  "output wire               ap_done",
                  "output wire               ap_idle",
                  "output wire               ap_ready"]
        kytkennat: list[str] = []
        for p in self.f.parametrit:
            if p.laji == "skalaari":
                portit.append(f"input  wire signed [31:0] {p.nimi}")
            elif p.laji == "taulu":
                portit += self.muisti(p.nimi, kytkennat, ulkoinen=True)
            elif p.nimi in self.virrat:
                kaytot = self.virrat[p.nimi]
                if self.virtasuunta[p.nimi] == "sisaan":
                    portit += [f"input  wire signed [31:0] {p.nimi}_TDATA",
                               f"input  wire               {p.nimi}_TVALID",
                               f"output wire               {p.nimi}_TREADY"]
                    kytkennat.append(f"    assign {p.nimi}_TREADY = "
                                     f"{p.nimi}_tarve && en;")
                else:
                    muut = [f"{v}_ok" for v in sorted(self.virrat)
                            if v != p.nimi]
                    kelpaa = " && ".join([f"{p.nimi}_tarve", *muut])
                    portit += [f"output wire signed [31:0] {p.nimi}_TDATA",
                               f"output wire               {p.nimi}_TVALID",
                               f"input  wire               {p.nimi}_TREADY"]
                    kytkennat += [
                        f"    assign {p.nimi}_TDATA = "
                        f"{valitse(kaytot, 1, vakio(0))};",
                        f"    assign {p.nimi}_TVALID = {kelpaa};"]
        if self.f.palauttaa:
            portit.append("output reg  signed [31:0] ap_return")
        for nimi in sorted(self.f.paikalliset):
            if self.jaot.get(nimi, Jako("none")).laji != "complete":
                self.muisti(nimi, kytkennat, ulkoinen=False)
        return portit, kytkennat

    # @alku muisti
    def muisti(self, taulu: str, kytkennat: list[str],
               ulkoinen: bool) -> list[str]:
        """Taulukon pankkien portit. Parametritaulukon muisti on piirin
        ulkopuolella (ap_memory); paikallinen taulukko on sisäinen RAM."""
        maara, koko = self.pankit(taulu)
        w = bitit(koko)
        en = " && en" if self.virrat else ""
        portit: list[str] = []
        for pankki in range(maara):
            nimi = self.pankin_nimi(taulu, pankki)
            luku = self.portit.get(Portti(taulu, pankki, False))
            kirj = self.portit.get(Portti(taulu, pankki, True))
            if not ulkoinen and (luku or kirj):
                kytkennat += [f"    // sisäinen muisti {nimi}: {koko} x 32",
                              f"    reg signed [31:0] {nimi}_m "
                              f"[0:{koko - 1}];"]
            oletus = f"{w}'d0"
            if luku:
                osoite = valitse(luku, 1, oletus)
                if ulkoinen:
                    portit += [f"output wire {f'[{w - 1}:0]':>13} "
                               f"{nimi}_address0",
                               f"output wire               {nimi}_ce0",
                               f"input  wire signed [31:0] {nimi}_q0"]
                    kytkennat += [f"    assign {nimi}_address0 = {osoite};",
                                  f"    assign {nimi}_ce0 = {tai(luku)}{en};"]
                else:
                    kytkennat += [
                        f"    wire [{w - 1}:0] {nimi}_address0 = {osoite};",
                        f"    wire {nimi}_ce0 = {tai(luku)}{en};",
                        f"    reg signed [31:0] {nimi}_q0;",
                        "    always @(posedge clk)",
                        f"        if ({nimi}_ce0) {nimi}_q0 <= "
                        f"{nimi}_m[{nimi}_address0];"]
            if kirj:
                osoite = valitse(kirj, 1, oletus)
                data = valitse(kirj, 2, vakio(0))
                if ulkoinen:
                    portit += [f"output wire {f'[{w - 1}:0]':>13} "
                               f"{nimi}_address1",
                               f"output wire               {nimi}_we1",
                               f"output wire signed [31:0] {nimi}_d1"]
                    kytkennat += [f"    assign {nimi}_address1 = {osoite};",
                                  f"    assign {nimi}_we1 = {tai(kirj)}{en};",
                                  f"    assign {nimi}_d1 = {data};"]
                else:
                    kytkennat += [
                        f"    wire [{w - 1}:0] {nimi}_address1 = {osoite};",
                        f"    wire {nimi}_we1 = {tai(kirj)}{en};",
                        f"    wire signed [31:0] {nimi}_d1 = {data};",
                        "    always @(posedge clk)",
                        f"        if ({nimi}_we1) {nimi}_m[{nimi}_address1] "
                        f"<= {nimi}_d1;"]
        return portit
    # @loppu muisti

    def virtojen_ohjaus(self) -> list[str]:
        rivit = []
        for virta, kaytot in sorted(self.virrat.items()):
            valmis = "TVALID" if self.virtasuunta[virta] == "sisaan" \
                else "TREADY"
            rivit += [f"    wire {virta}_tarve = {tai(kaytot)};",
                      f"    wire {virta}_ok = !{virta}_tarve || "
                      f"{virta}_{valmis};"]
        rivit.append("    wire en = " + " && ".join(
            f"{v}_ok" for v in sorted(self.virrat)) + ";")
        return rivit

    def kertojayksikot(self) -> list[str]:
        rivit = []
        for yksikko, kaytot in sorted(self.yksikot.items()):
            a = [(ehto, x, "") for ehto, x, _ in kaytot]
            b = [(ehto, y, "") for ehto, _, y in kaytot]
            rivit += [f"    // kertoja {yksikko}: {len(kaytot)} operaatiota",
                      f"    wire signed [31:0] mul{yksikko}_a = "
                      f"{valitse(a, 1, vakio(0))};",
                      f"    wire signed [31:0] mul{yksikko}_b = "
                      f"{valitse(b, 1, vakio(0))};",
                      f"    wire signed [31:0] mul{yksikko}_y = "
                      f"mul{yksikko}_a * mul{yksikko}_b;"]
        return rivit

    # --- kokonaisuus ------------------------------------------------------
    # @alku moduuli
    def moduuli(self) -> str:
        for lehti in self.lehdet:
            self.lehti(lehti)
        ohjaus = self.ohjaus()
        portit, kytkennat = self.rajapinta()
        tilat = self.tilat()
        w = bitit(len(tilat))
        muuttujat = [f"    reg signed [31:0] {rekisterinimi(m)};"
                     for m in sorted(self.muuttujat)
                     if m not in {u.muuttuja for u in self.ulommat}]
        muuttujat += [f"    reg signed [31:0] {rekisterinimi(u.muuttuja)};"
                      for u in self.ulommat]
        rivit = [f"// Tuottanut minihls: {self.f.nimi}",
                 f"module {self.f.nimi} (",
                 ",\n".join(f"    {p}" for p in portit),
                 ");",
                 "    // Tilakone",
                 *(f"    localparam {t} = {w}'d{i};"
                   for i, t in enumerate(tilat)),
                 f"    reg [{w - 1}:0] tila;",
                 *self.laskurit(),
                 *self.aktiivisuussignaalit(),
                 "    assign ap_done = tila == S_DONE;",
                 "    assign ap_idle = tila == S_IDLE;",
                 "    assign ap_ready = tila == S_DONE;"]
        if self.virrat:
            rivit += ["    // Virrat: koko piiri pysähtyy, jos tarvittu",
                      "    // virta ei ole valmis", *self.virtojen_ohjaus()]
        rivit += ["    // Muuttujat ja vaiherekisterit", *muuttujat,
                  *self.rekisterit, "    // Datapolku", *self.datapolku,
                  *self.kertojayksikot(), "    // Portit", *kytkennat]
        ehto = "if (en) " if self.virrat else ""
        rivit += ["    always @(posedge clk) begin",
                  "        if (rst) begin",
                  "            tila <= S_IDLE;",
                  f"        end else {ehto}begin",
                  "            case (tila)", *ohjaus,
                  "            endcase", "        end", "    end",
                  f"    always @(posedge clk) {ehto}begin",
                  *self.paivitykset, "    end", "endmodule", ""]
        return "\n".join(rivita(r) for r in rivit)
    # @loppu moduuli


VERTAILU = {"<", "<=", ">", ">=", "==", "!="}
BINAARISET = {"+", "-", "*", "&", "|", "^", "<<", *VERTAILU}


def rivita(rivi: str, leveys: int = 78) -> str:
    """Jakaa pitkän rivin operaattorien kohdalta useaksi riviksi."""
    if len(rivi) <= leveys or "=" not in rivi:
        return rivi
    alku = rivi.index("=") + 2
    if rivi[alku - 3] in "<":                   # <=
        alku += 1
    sisennys = " " * min(alku, 40)
    osat = re.split(r"(?<= :) | (?=\|\| )| (?=&& )", rivi[alku:])
    tulos, nykyinen = [], rivi[:alku]
    for osa in osat:
        if len(nykyinen) + len(osa) > leveys and nykyinen.strip():
            tulos.append(nykyinen.rstrip())
            nykyinen = sisennys
        nykyinen += osa + " "
    tulos.append(nykyinen.rstrip())
    return "\n".join(tulos)


def lehti_ks(lehti: Lehtiajoitus) -> str:
    return f"{bitit(lehti.ii)}'d{lehti.ii - 1}"


def tai(kaytot: Sequence[tuple[str, ...]]) -> str:
    ehdot = [k[0] for k in kaytot]
    if len(ehdot) == 1:
        return ehdot[0]
    return " || ".join(f"({e})" if "&&" in e else e for e in ehdot)


def valitse(kaytot: Sequence[tuple[str, ...]], kentta: int,
            oletus: str) -> str:
    """Ehtoketju: e1 ? x1 : e2 ? x2 : oletus. Yksi käyttö ilman ehtoa."""
    if len(kaytot) == 1:
        return kaytot[0][kentta]
    osat = [f"({k[0]}) ? {k[kentta]} :" for k in kaytot]
    return " ".join([*osat, oletus])
