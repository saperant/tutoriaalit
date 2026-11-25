// FIR-suodin RTL-tasolla: sama aritmetiikka kuin mallissa
// ../08-fir/fir.hpp. Yksi näyte kellojaksossa, tulos jakson viiveellä.
// @alku rtl
module fir #(
    parameter int PYORISTYS = 1  // 0: katkaisu (virheellinen versio)
) (
    input  logic               clk,
    input  logic               rst,
    input  logic               sisaan_kelpaa,
    input  logic signed [15:0] x,
    output logic               ulos_kelpaa,
    output logic signed [15:0] y
);
    localparam int N = 8;
    // Kertoimet Q1.15:nä, katkaistuina kuten sc_fixed<16, 1> (SC_TRN).
    localparam logic signed [15:0] C[N] = '{
        -16'sd656, -16'sd1639, 16'sd5570, 16'sd13107,
        16'sd13107, 16'sd5570, -16'sd1639, -16'sd656
    };

    logic signed [15:0] viive[N-1];  // x[n-1] ... x[n-7]
    logic signed [34:0] summa;       // Q5.30: kolme vartijabittiä
    logic signed [34:0] pyoristetty;
    logic signed [19:0] siirretty;   // Q5.15 ennen saturaatiota

    always_comb begin
        summa = 35'(x) * 35'(C[0]);
        for (int k = 1; k < N; k++) begin
            summa += 35'(viive[k-1]) * 35'(C[k]);
        end
        // Pyöristys kohti +ääretöntä kuten SC_RND: lisätään puoli LSB:tä.
        pyoristetty = (PYORISTYS != 0) ? summa + 35'sd16384 : summa;
        siirretty = 20'(pyoristetty >>> 15);
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            for (int k = 0; k < N - 1; k++) viive[k] <= '0;
            ulos_kelpaa <= 1'b0;
            y <= '0;
        end else begin
            ulos_kelpaa <= sisaan_kelpaa;
            if (sisaan_kelpaa) begin
                viive[0] <= x;
                for (int k = 1; k < N - 1; k++) viive[k] <= viive[k-1];
                // Saturaatio Q1.15:n alueelle (SC_SAT).
                if (siirretty > 20'sd32767) y <= 16'sd32767;
                else if (siirretty < -20'sd32768) y <= -16'sd32768;
                else y <= siirretty[15:0];
            end
        end
    end
endmodule
// @loppu rtl
