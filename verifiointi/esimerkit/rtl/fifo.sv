// Synkroninen FIFO, jonka lukupää näkyy suoraan lähdössä
// (first-word fall-through). Kirjoitus hyväksytään, kun jono ei ole
// täynnä, ja luku, kun jono ei ole tyhjä. Makrot BUGI_* lisäävät
// tarkoituksellisia vikoja, joita luvut 3-10 etsivät.
// @alku fifo
module fifo #(
    parameter int SYVYYS = 4,
    parameter int LEVEYS = 8
) (
    input  logic                        clk,
    input  logic                        rst,      // synkroninen
    input  logic                        push,
    input  logic [LEVEYS-1:0]           din,
    input  logic                        pop,
    output logic [LEVEYS-1:0]           dout,
    output logic                        tyhja,
    output logic                        taysi,
    output logic [$clog2(SYVYYS+1)-1:0] maara
);
    localparam int AW = $clog2(SYVYYS);
    logic [LEVEYS-1:0] muisti [SYVYYS];
    logic [AW-1:0]     kirj, luku;

    logic kirjoita, lue;
    assign kirjoita = push && !taysi;
`ifdef BUGI_TYHJA
    assign lue      = pop;               // vika: luku tyhjästä sallitaan
`else
    assign lue      = pop && !tyhja;
`endif

    always_ff @(posedge clk) begin
        if (rst) begin
            kirj  <= '0;
            luku  <= '0;
            maara <= '0;
        end else begin
            if (kirjoita) begin
                muisti[kirj] <= din;
                kirj <= (kirj == AW'(SYVYYS - 1)) ? '0 : kirj + 1'b1;
            end
            if (lue)
                luku <= (luku == AW'(SYVYYS - 1)) ? '0 : luku + 1'b1;
`ifdef BUGI_SAMANAIKAINEN
            if (kirjoita)       maara <= maara + 1'b1;   // vika
            else if (lue)       maara <= maara - 1'b1;
`else
            if (kirjoita && !lue)      maara <= maara + 1'b1;
            else if (lue && !kirjoita) maara <= maara - 1'b1;
`endif
        end
    end

    assign dout  = muisti[luku];
    assign tyhja = (maara == '0);
`ifdef BUGI_TAYSI
    assign taysi = (maara == $bits(maara)'(SYVYYS - 1));  // vika
`else
    assign taysi = (maara == $bits(maara)'(SYVYYS));
`endif
// @loppu fifo

`ifdef FORMAL
    // Formaalit ominaisuudet (luku 8). Ensimmäisessä tilassa
    // oletetaan nollaus; sen jälkeen syötteet ovat vapaita.
    // @alku formaali
    logic alku = 1'b1;
    always_ff @(posedge clk) alku <= 1'b0;
    always_comb if (alku) assume (rst);

    always_comb if (!alku) begin
        assert (maara <= $bits(maara)'(SYVYYS));
        assert (tyhja == (maara == '0));
        assert (taysi == (maara == $bits(maara)'(SYVYYS)));
        // Tyhjässä jonossa luku- ja kirjoitusosoitin ovat samat.
        if (tyhja) assert (kirj == luku);
    end

    always_ff @(posedge clk) if (!alku && !$past(rst)) begin
        // Hylätty luku tai kirjoitus ei muuta määrää.
        if ($past(pop && tyhja && !push)) assert ($stable(maara));
        if ($past(push && taysi && !pop)) assert ($stable(maara));
        // Hyväksytty kirjoitus ja luku yhtä aikaa: määrä ei muutu.
        if ($past(push && !taysi && pop && !tyhja))
            assert ($stable(maara));
    end

    // Kattavuustavoitteet: tilat, jotka on voitava saavuttaa.
    always_comb if (!alku) begin
        cover (taysi);
        cover (taysi && pop && push);
    end
    // @loppu formaali

    // @alku invariantti
`ifdef INVARIANTTI
    // Induktiota varten: osoittimien ero vastaa määrää.
    always_comb if (!alku)
        assert (32'(maara) % SYVYYS ==
                (32'(kirj) + SYVYYS - 32'(luku)) % SYVYYS);
`endif
    // @loppu invariantti
`endif
endmodule
