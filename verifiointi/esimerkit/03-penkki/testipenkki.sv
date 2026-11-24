// Kerroksellinen testipenkki FIFOlle: generaattori tuottaa
// toimenpiteitä, ajuri vie ne liitäntään, monitori havainnoi
// hyväksytyt kirjoitukset ja luvut, ja tulostaulu vertaa niitä
// referenssimalliin. Siemen annetaan argumenttina +siemen=N.
module testipenkki;
    localparam int SYVYYS = 4;
    logic       clk = 1'b0, rst = 1'b1, push = 1'b0, pop = 1'b0;
    logic [7:0] din = '0, dout;
    logic       tyhja, taysi;
    logic [2:0] maara;
    logic       kaynnissa = 1'b1;

    fifo #(.SYVYYS(SYVYYS), .LEVEYS(8)) dut (.*);
    initial while (kaynnissa) #5 clk = ~clk;

    // @alku transaktio
    typedef struct {
        bit         push;
        bit         pop;
        logic [7:0] data;
    } toimenpide_t;
    // @loppu transaktio

    // @alku generaattori
    toimenpide_t jono[$];
    int unsigned siemen = 1;

    function automatic toimenpide_t arvo_toimenpide();
        toimenpide_t t;
        int unsigned r = $urandom_range(99);
        // Painotus: 40 % kirjoituksia, 30 % lukuja, 20 % molempia,
        // 10 % tyhjäkäyntiä.
        t.push = (r < 40) || (r >= 70 && r < 90);
        t.pop  = (r >= 40 && r < 90);
        t.data = 8'($urandom);
        return t;
    endfunction
    // @loppu generaattori

    // @alku ajuri
    // Ajuri vie seuraavan toimenpiteen liitäntään kellon laskevalla
    // reunalla, jotta signaalit ovat vakaat nousevalla reunalla.
    initial forever begin
        @(negedge clk);
        if (!rst && jono.size() > 0) begin
            toimenpide_t t = jono.pop_front();
            push = t.push; pop = t.pop; din = t.data;
        end else begin
            push = 1'b0; pop = 1'b0;
        end
    end
    // @loppu ajuri

    // @alku tulostaulu
    logic [7:0] malli[$];          // referenssimalli: jono
    int kirjoituksia = 0, lukuja = 0, virheita = 0;

    function automatic void vika(string viesti);
        if (virheita < 3) $display("VIRHE %0t: %s", $time, viesti);
        virheita++;
    endfunction

    // Monitori ja tulostaulu: nousevalla reunalla havaitaan, mitä DUT
    // hyväksyi, ja verrataan malliin ennen kuin tila päivittyy.
    initial forever begin
        bit kirjoitus;
        @(posedge clk);
        if (rst) continue;
        // Malli päättää hyväksynnät omasta tilastaan, ei DUT:n lipuista.
        kirjoitus = push && malli.size() < SYVYYS;
        if (int'(maara) != malli.size())
            vika($sformatf("maara=%0d, mallissa %0d", maara, malli.size()));
        if (tyhja != (malli.size() == 0))
            vika($sformatf("tyhja=%0b, mallissa %0d", tyhja, malli.size()));
        if (taysi != (malli.size() == SYVYYS))
            vika($sformatf("taysi=%0b, mallissa %0d", taysi, malli.size()));
        if (pop && malli.size() > 0) begin
            logic [7:0] odotettu = malli.pop_front();
            if (dout !== odotettu)
                vika($sformatf("luettiin %02h, odotettiin %02h",
                               dout, odotettu));
            lukuja++;
        end
        if (kirjoitus) begin
            malli.push_back(din);
            kirjoituksia++;
        end
    end
    // @loppu tulostaulu

    // @alku testi
    initial begin
        void'($value$plusargs("siemen=%d", siemen));
        void'($urandom(siemen));
        repeat (2000) jono.push_back(arvo_toimenpide());
        @(negedge clk) rst = 1'b0;
        wait (jono.size() == 0);
        repeat (2) @(posedge clk);
        $display("siemen %0d: %0d kirjoitusta, %0d lukua, %0d virhettä",
                 siemen, kirjoituksia, lukuja, virheita);
        kaynnissa = 1'b0;
        if (virheita != 0) $error("tulostaulu löysi virheitä");
    end
    // @loppu testi
endmodule
