"""C/RTL-yhteissimulaation testipenkki.

C-simulaatio (testi.cpp) kirjoittaa jokaisen testitapauksen syötteet ja
odotetut tulokset tiedostoihin. Tuotettu testipenkki lataa ne, ajaa
RTL:n jokaisella tapauksella, mittaa latenssin ja vertaa tulokset.
"""

from __future__ import annotations

from collections.abc import Callable

from .verilog import Portti, Tuottaja, bitit

ENINTAAN = 16                   # testitapauksia enintään


def testipenkki(tuottaja: Tuottaja, virtamaarat: dict[str, int],
                paine: bool) -> str:
    f = tuottaja.f
    r = ["// Tuottanut minihls: testipenkki",
         "module tb;",
         "    reg clk = 1'b0;",
         "    reg rst = 1'b1;",
         "    reg ap_start = 1'b0;",
         "    wire ap_done, ap_idle, ap_ready;",
         "    always #5 clk = ~clk;",
         "    // Satunnainen vastapaine virroille (LFSR)",
         "    reg [15:0] lfsr = 16'hACE1;",
         "    always @(posedge clk)",
         "        lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ "
         "lfsr[10]};",
         f"    wire paine = {'1' if paine else '0'};",
         "    integer tapaus, j, jaksot, virheet, pienin, suurin;",
         "    reg [31:0] tapauksia [0:0];"]
    kytkenta = [".clk(clk)", ".rst(rst)", ".ap_start(ap_start)",
                ".ap_done(ap_done)", ".ap_idle(ap_idle)",
                ".ap_ready(ap_ready)"]
    lataus, tarkistus, alustus = [], [], []
    for p in f.parametrit:
        if p.laji == "skalaari":
            r += [f"    reg signed [31:0] {p.nimi};",
                  f"    reg signed [31:0] {p.nimi}_syote [0:{ENINTAAN - 1}];"]
            alustus.append(f'        $readmemh("{p.nimi}.in.hex", '
                           f'{p.nimi}_syote);')
            lataus.append(f"            {p.nimi} = {p.nimi}_syote[tapaus];")
            kytkenta.append(f".{p.nimi}({p.nimi})")
        elif p.laji == "taulu":
            maara, koko = tuottaja.pankit(p.nimi)
            w = bitit(koko)
            kaikki = ENINTAAN * p.koko - 1
            r.append(f"    reg signed [31:0] {p.nimi}_syote [0:{kaikki}];")
            alustus.append(f'        $readmemh("{p.nimi}.in.hex", '
                           f'{p.nimi}_syote);')
            kirjoitetaan = any(Portti(p.nimi, b, True) in tuottaja.portit
                               for b in range(maara))
            if kirjoitetaan:
                r.append(f"    reg signed [31:0] {p.nimi}_odotettu "
                         f"[0:{kaikki}];")
                alustus.append(f'        $readmemh("{p.nimi}.out.hex", '
                               f'{p.nimi}_odotettu);')
            for b in range(maara):
                nimi = tuottaja.pankin_nimi(p.nimi, b)
                r.append(f"    reg signed [31:0] {nimi}_m [0:{koko - 1}];")
                if Portti(p.nimi, b, False) in tuottaja.portit:
                    r += [f"    wire [{w - 1}:0] {nimi}_address0;",
                          f"    wire {nimi}_ce0;",
                          f"    reg signed [31:0] {nimi}_q0;",
                          "    always @(posedge clk)",
                          f"        if ({nimi}_ce0) {nimi}_q0 <= "
                          f"{nimi}_m[{nimi}_address0];"]
                    kytkenta += [f".{nimi}_address0({nimi}_address0)",
                                 f".{nimi}_ce0({nimi}_ce0)",
                                 f".{nimi}_q0({nimi}_q0)"]
                if Portti(p.nimi, b, True) in tuottaja.portit:
                    r += [f"    wire [{w - 1}:0] {nimi}_address1;",
                          f"    wire {nimi}_we1;",
                          f"    wire signed [31:0] {nimi}_d1;",
                          "    always @(posedge clk)",
                          f"        if ({nimi}_we1) {nimi}_m[{nimi}_address1]"
                          f" <= {nimi}_d1;"]
                    kytkenta += [f".{nimi}_address1({nimi}_address1)",
                                 f".{nimi}_we1({nimi}_we1)",
                                 f".{nimi}_d1({nimi}_d1)"]
            sijainti = pankki_ja_paikka(tuottaja, p.nimi, maara, koko)
            for b in range(maara):
                nimi = tuottaja.pankin_nimi(p.nimi, b)
                ehto, paikka = sijainti(b)
                jos = "" if ehto == "1" else f"if ({ehto}) "
                lataus += [f"            for (j = 0; j < {p.koko}; j++)",
                           f"                {jos}{nimi}_m[{paikka}]"
                           f" = {p.nimi}_syote[tapaus * {p.koko} + j];"]
                ehdossa = "" if ehto == "1" else f"({ehto}) && "
                if kirjoitetaan:
                    tarkistus += [
                        f"            for (j = 0; j < {p.koko}; j++)",
                        f"                if ({ehdossa}{nimi}_m[{paikka}]"
                        f" !== {p.nimi}_odotettu[tapaus * {p.koko} + j])"
                        " begin",
                        "                    if (virheet < 5)",
                        f'                    $display("tapaus %0d: '
                        f'{p.nimi}[%0d] = %0d, odotettiin %0d", tapaus, j, '
                        f"{nimi}_m[{paikka}], "
                        f"{p.nimi}_odotettu[tapaus * {p.koko} + j]);",
                        "                    virheet = virheet + 1;",
                        "                end"]
        elif p.nimi in tuottaja.virrat:
            maara = virtamaarat[p.nimi]
            kaikki = ENINTAAN * maara - 1
            if tuottaja.virtasuunta[p.nimi] == "sisaan":
                r += [f"    reg signed [31:0] {p.nimi}_syote [0:{kaikki}];",
                      f"    integer {p.nimi}_i = 0, {p.nimi}_raja = 0;",
                      f"    wire {p.nimi}_TVALID = {p.nimi}_i < "
                      f"{p.nimi}_raja && (!paine || lfsr[3]);",
                      f"    wire signed [31:0] {p.nimi}_TDATA = "
                      f"{p.nimi}_syote[{p.nimi}_i];",
                      f"    wire {p.nimi}_TREADY;",
                      "    always @(posedge clk)",
                      f"        if ({p.nimi}_TVALID && {p.nimi}_TREADY) "
                      f"{p.nimi}_i <= {p.nimi}_i + 1;"]
                alustus.append(f'        $readmemh("{p.nimi}.in.hex", '
                               f'{p.nimi}_syote);')
                lataus.append(f"            {p.nimi}_raja = (tapaus + 1) * "
                              f"{maara};")
            else:
                r += [f"    reg signed [31:0] {p.nimi}_odotettu "
                      f"[0:{kaikki}];",
                      f"    integer {p.nimi}_i = 0;",
                      f"    wire {p.nimi}_TREADY = !paine || lfsr[7];",
                      f"    wire signed [31:0] {p.nimi}_TDATA;",
                      f"    wire {p.nimi}_TVALID;",
                      "    always @(posedge clk)",
                      f"        if ({p.nimi}_TVALID && {p.nimi}_TREADY) "
                      "begin",
                      f"            if ({p.nimi}_TDATA !== "
                      f"{p.nimi}_odotettu[{p.nimi}_i]) begin",
                      f'                $display("{p.nimi}[%0d] = %0d, '
                      f'odotettiin %0d", {p.nimi}_i, {p.nimi}_TDATA, '
                      f"{p.nimi}_odotettu[{p.nimi}_i]);",
                      "                virheet = virheet + 1;",
                      "            end",
                      f"            {p.nimi}_i <= {p.nimi}_i + 1;",
                      "        end"]
                alustus.append(f'        $readmemh("{p.nimi}.out.hex", '
                               f'{p.nimi}_odotettu);')
                tarkistus += [
                    f"            if ({p.nimi}_i != (tapaus + 1) * {maara}) "
                    "begin",
                    f'                $display("tapaus %0d: {p.nimi}: '
                    f'%0d arvoa, odotettiin {maara}", tapaus, '
                    f"{p.nimi}_i - tapaus * {maara});",
                    "                virheet = virheet + 1;",
                    "            end"]
            for portti in ("TDATA", "TVALID", "TREADY"):
                kytkenta.append(f".{p.nimi}_{portti}({p.nimi}_{portti})")
    if f.palauttaa:
        r += ["    wire signed [31:0] ap_return;",
              f"    reg signed [31:0] paluu_odotettu [0:{ENINTAAN - 1}];"]
        kytkenta.append(".ap_return(ap_return)")
        alustus.append('        $readmemh("paluu.out.hex", paluu_odotettu);')
        tarkistus += [
            "            if (ap_return !== paluu_odotettu[tapaus]) begin",
            '                $display("tapaus %0d: paluuarvo %0d, '
            'odotettiin %0d", tapaus, ap_return, paluu_odotettu[tapaus]);',
            "                virheet = virheet + 1;",
            "            end"]
    r += [f"    {f.nimi} dut (",
          ",\n".join(f"        {k}" for k in kytkenta),
          "    );",
          "    initial begin",
          '        $readmemh("tapaukset.hex", tapauksia);',
          *alustus,
          "        virheet = 0;",
          "        pienin = 1 << 30;",
          "        suurin = 0;",
          "        repeat (2) @(negedge clk);",
          "        rst = 1'b0;",
          "        for (tapaus = 0; tapaus < tapauksia[0]; tapaus++) begin",
          *lataus,
          "            @(negedge clk) ap_start = 1'b1;",
          "            @(negedge clk) ap_start = 1'b0;",
          "            jaksot = 1;",
          "            while (!ap_done) begin",
          "                @(negedge clk);",
          "                jaksot = jaksot + 1;",
          "                if (jaksot > 100000) $fatal(1, \"aikakatkaisu\");",
          "            end",
          "            if (jaksot < pienin) pienin = jaksot;",
          "            if (jaksot > suurin) suurin = jaksot;",
          *tarkistus,
          "        end",
          '        $write("RTL-simulaatio: %0d tapausta, latenssi ",',
          "               tapauksia[0]);",
          "        if (pienin == suurin)",
          '            $write("%0d jaksoa", pienin);',
          "        else",
          '            $write("%0d-%0d jaksoa", pienin, suurin);',
          '        $display(", virheitä %0d", virheet);',
          "        $finish;",
          "    end",
          "endmodule",
          ""]
    return "\n".join(rivita(rivi) for rivi in r)


def rivita(rivi: str) -> str:
    """Pitkästä $display-kutsusta argumentit omalle rivilleen."""
    if len(rivi) <= 78 or '$display("' not in rivi:
        return rivi
    alku = rivi.index('$display("')
    loppu = rivi.index('", ', alku) + 2
    sisennys = " " * (alku + 4)
    return f"{rivi[:loppu]}\n{sisennys}{rivi[loppu + 1:]}"


def pankki_ja_paikka(tuottaja: Tuottaja, taulu: str, maara: int,
                     koko: int) -> Callable[[int], tuple[str, str]]:
    """Testipenkin lauseke, joka kertoo, onko alkio j pankissa b, ja
    alkion paikka pankissa."""
    jako = tuottaja.jaot.get(taulu)

    def sijainti(b: int) -> tuple[str, str]:
        if maara == 1 or jako is None:
            return "1", "j"
        if jako.laji == "cyclic":
            return f"j % {maara} == {b}", f"j / {maara}"
        return f"j / {koko} == {b}", f"j % {koko}"
    return sijainti
