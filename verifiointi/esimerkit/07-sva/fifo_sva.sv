// FIFOn väitteet SystemVerilogin väitekielellä (SVA). Moduuli
// liitetään FIFOon bind-lauseella, joten FIFOn lähdettä ei muuteta.
// Väitteet tarkistetaan, kun Verilatoria käytetään valitsimella --assert.
// @alku sva
module fifo_sva #(parameter int SYVYYS = 4) (
    input logic       clk, rst, push, pop, tyhja, taysi,
    input logic [2:0] maara
);
    // Yhdistelmäväitteet: tilaliput vastaavat määrää.
    property liput_oikein;
        @(posedge clk) disable iff (rst)
            (tyhja == (maara == 0)) && (taysi == (maara == 3'(SYVYYS)));
    endproperty
    a_liput: assert property (liput_oikein)
        else $error("liput: maara=%0d tyhja=%b taysi=%b",
                    maara, tyhja, taysi);

    a_raja: assert property (@(posedge clk) disable iff (rst)
        maara <= 3'(SYVYYS))
        else $error("maara=%0d ylittää syvyyden", maara);

    // Aikaväitteet: |=> tarkoittaa "seuraavalla jaksolla".
    property samanaikainen_sailyttaa;
        @(posedge clk) disable iff (rst)
            (push && pop && !tyhja && !taysi) |=> $stable(maara);
    endproperty
    a_samanaikainen: assert property (samanaikainen_sailyttaa)
        else $error("push+pop muutti määrää: %0d -> %0d",
                    $past(maara), maara);

    a_tyhja_luku: assert property (@(posedge clk) disable iff (rst)
        (pop && !push && tyhja) |=> tyhja)
        else $error("luku tyhjästä muutti tilaa: maara=%0d", maara);

    // Kattavuus: tapahtuiko kiinnostava tilanne ainakin kerran?
    c_taysi_samanaikainen: cover property (@(posedge clk) disable iff (rst)
        taysi && push && pop);
endmodule

bind fifo fifo_sva #(.SYVYYS(SYVYYS)) sva (.*);
// @loppu sva
