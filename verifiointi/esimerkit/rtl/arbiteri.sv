// Vuorotteleva (round-robin) arbiteri neljälle pyytäjälle. Myönnetty
// pyytäjä saa vuoron yhdeksi jaksoksi, ja seuraavalla kierroksella
// etusija siirtyy sen seuraajalle. Myöntö on rekisteröity.
// @alku arbiteri
module arbiteri (
    input  logic       clk,
    input  logic       rst,
    input  logic [3:0] pyynto,
    output logic [3:0] myonto      // korkeintaan yksi bitti päällä
);
    logic [1:0] viimeisin;          // edellinen myönnetty pyytäjä
    logic [3:0] seuraava;
    logic [1:0] voittaja;
    logic [1:0] ehdokas;

    always_comb begin
        seuraava = '0;
        voittaja = viimeisin;
        ehdokas  = '0;
        // Etsitään ensimmäinen pyytäjä viimeisimmän jälkeen.
        for (int i = 1; i <= 4; i++) begin
`ifdef BUGI_KIINTEA
            ehdokas = 2'(i - 1);                // vika: kiinteä etusija
`else
            ehdokas = viimeisin + 2'(i);
`endif
            if (pyynto[ehdokas] && seuraava == '0) begin
                seuraava[ehdokas] = 1'b1;
                voittaja = ehdokas;
            end
        end
`ifdef BUGI_KAKSI
        if (pyynto == 4'b1111) seuraava = 4'b0011;  // vika: kaksi myöntöä
`endif
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            myonto    <= '0;
            viimeisin <= 2'd3;          // pyytäjä 0 aloittaa
        end else begin
            myonto <= seuraava;
            if (seuraava != '0) viimeisin <= voittaja;
        end
    end
// @loppu arbiteri

`ifdef FORMAL
    // @alku formaali
    logic alku = 1'b1;
    always_ff @(posedge clk) alku <= 1'b0;
    always_comb if (alku) assume (rst);

    always_comb if (!alku) assert ($onehot0(myonto));
    // Myöntö menee vain pyytäjälle (myöntö on rekisteröity).
    always_ff @(posedge clk) if (!alku && !$past(rst))
        assert ((myonto & ~$past(pyynto)) == '0);

    for (genvar i = 0; i < 4; i++) begin : reilu
        // Ympäristön lupaus: pyyntö pysyy, kunnes se myönnetään.
        always_ff @(posedge clk) if (!alku && !$past(rst))
            if ($past(pyynto[i] && !myonto[i])) assume (pyynto[i]);
        // Odotuslaskuri: montako jaksoa pyyntö on odottanut.
        logic [2:0] odotus = '0;
        always_ff @(posedge clk)
            if (rst || !pyynto[i] || myonto[i]) odotus <= '0;
            else if (odotus != 3'd7)            odotus <= odotus + 1'b1;
        always_comb if (!alku) assert (odotus <= 3'd4);
        always_comb if (!alku) cover (odotus == 3'd4);
    end
    // @loppu formaali
`endif
endmodule
