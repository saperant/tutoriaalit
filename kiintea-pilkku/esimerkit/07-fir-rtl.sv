// Sama Q1.15-FIR laitteistokuvauskielellä: kavennus on bittileikkaus,
// ja tulos on bitilleen sama kuin C- ja Python-mallissa (sama tarkiste).
module testipenkki;
    localparam int TAPIT = 15;
    localparam int NAYTTEET = 200;

    localparam logic signed [15:0] H[TAPIT] = '{
        37, -128, -525, -667, 687, 4080, 8012, 9779,
        8012, 4080, 687, -667, -525, -128, 37};

    // @alku kavenna
    // Q6.30-kertymä (36 bittiä) -> Q1.15: pyöristys lähimpään
    // parilliseen ja saturaatio. >>> on aritmeettinen siirto, kun
    // operandi on signed.
    function automatic logic signed [15:0] kavenna(
        input logic signed [35:0] kertyma);
        logic signed [20:0] q;
        logic [14:0] jaannos;
        q = 21'(kertyma >>> 15);                 // lattia: 15 alinta pois
        jaannos = kertyma[14:0];
        if (jaannos > 15'h4000 || (jaannos == 15'h4000 && q[0]))
            q = q + 21'sd1;
        if (q > 21'sd32767) return 16'sd32767;   // ylimmät bitit eivät
        if (q < -21'sd32768) return -16'sd32768; // ole etumerkin kopioita
        return q[15:0];
    endfunction
    // @loppu kavenna

    logic signed [15:0] ikkuna[TAPIT];
    logic [31:0] tila = 32'd12345;
    logic [31:0] tarkiste = 32'd2166136261;
    logic signed [35:0] kertyma;
    logic signed [15:0] y;

    // @alku ajo
    initial begin
        for (int k = 0; k < TAPIT; k++) ikkuna[k] = '0;
        for (int n = 0; n < NAYTTEET; n++) begin
            tila = tila * 32'd1103515245 + 32'd12345;
            for (int k = TAPIT - 1; k > 0; k--) ikkuna[k] = ikkuna[k - 1];
            ikkuna[0] = 16'(tila[31:16]) - 16'sd32768;
            kertyma = '0;
            for (int k = 0; k < TAPIT; k++)      // 16 x 16 -> 32 -> 36
                kertyma += 36'(H[k] * ikkuna[k]);
            y = kavenna(kertyma);
            tarkiste = (tarkiste ^ {16'd0, y}) * 32'd16777619;
            if (n < 6) $display("y[%0d] = %6d", n, y);
        end
        $display("tarkiste %08x", tarkiste);
        #1;     // viive: simulaatio päättyy, kun tapahtumat loppuvat
    end
    // @loppu ajo
endmodule
