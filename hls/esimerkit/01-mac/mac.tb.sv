// Tuottanut minihls: testipenkki
module tb;
    reg clk = 1'b0;
    reg rst = 1'b1;
    reg ap_start = 1'b0;
    wire ap_done, ap_idle, ap_ready;
    always #5 clk = ~clk;
    // Satunnainen vastapaine virroille (LFSR)
    reg [15:0] lfsr = 16'hACE1;
    always @(posedge clk)
        lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
    wire paine = 0;
    integer tapaus, j, jaksot, virheet, pienin, suurin;
    reg [31:0] tapauksia [0:0];
// @alku muistit
    reg signed [31:0] a_syote [0:127];
    reg signed [31:0] a_m [0:7];
    wire [2:0] a_address0;
    wire a_ce0;
    reg signed [31:0] a_q0;
    always @(posedge clk)
        if (a_ce0) a_q0 <= a_m[a_address0];
    reg signed [31:0] b_syote [0:127];
    reg signed [31:0] b_m [0:7];
    wire [2:0] b_address0;
    wire b_ce0;
    reg signed [31:0] b_q0;
    always @(posedge clk)
        if (b_ce0) b_q0 <= b_m[b_address0];
// @loppu muistit
    wire signed [31:0] ap_return;
    reg signed [31:0] paluu_odotettu [0:15];
    mac dut (
        .clk(clk),
        .rst(rst),
        .ap_start(ap_start),
        .ap_done(ap_done),
        .ap_idle(ap_idle),
        .ap_ready(ap_ready),
        .a_address0(a_address0),
        .a_ce0(a_ce0),
        .a_q0(a_q0),
        .b_address0(b_address0),
        .b_ce0(b_ce0),
        .b_q0(b_q0),
        .ap_return(ap_return)
    );
// @alku ajo
    initial begin
        $readmemh("tapaukset.hex", tapauksia);
        $readmemh("a.in.hex", a_syote);
        $readmemh("b.in.hex", b_syote);
        $readmemh("paluu.out.hex", paluu_odotettu);
        virheet = 0;
        pienin = 1 << 30;
        suurin = 0;
        repeat (2) @(negedge clk);
        rst = 1'b0;
        for (tapaus = 0; tapaus < tapauksia[0]; tapaus++) begin
            for (j = 0; j < 8; j++)
                a_m[j] = a_syote[tapaus * 8 + j];
            for (j = 0; j < 8; j++)
                b_m[j] = b_syote[tapaus * 8 + j];
            @(negedge clk) ap_start = 1'b1;
            @(negedge clk) ap_start = 1'b0;
            jaksot = 1;
            while (!ap_done) begin
                @(negedge clk);
                jaksot = jaksot + 1;
                if (jaksot > 100000) $fatal(1, "aikakatkaisu");
            end
            if (jaksot < pienin) pienin = jaksot;
            if (jaksot > suurin) suurin = jaksot;
            if (ap_return !== paluu_odotettu[tapaus]) begin
                $display("tapaus %0d: paluuarvo %0d, odotettiin %0d",
                    tapaus, ap_return, paluu_odotettu[tapaus]);
                virheet = virheet + 1;
            end
        end
        $write("RTL-simulaatio: %0d tapausta, latenssi ",
               tapauksia[0]);
        if (pienin == suurin)
            $write("%0d jaksoa", pienin);
        else
            $write("%0d-%0d jaksoa", pienin, suurin);
        $display(", virheitä %0d", virheet);
        $finish;
    end
// @loppu ajo
endmodule
