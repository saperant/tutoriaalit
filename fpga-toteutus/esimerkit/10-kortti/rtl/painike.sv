// @alku painike
// Painikkeen tahdistus ja kosketinvärähtelyn suodatus. Tulo on
// asynkroninen, joten se tahdistetaan kahdella kiikulla (luku 8). Uusi
// tila hyväksytään vasta, kun tulo on poikennut nykyisestä tilasta
// 2**LEVEYS peräkkäistä kellojaksoa: 2**17 / 25,125 MHz = 5,2 ms.
module painike #(
  parameter int LEVEYS = 17
) (
  input  logic clk,
  input  logic nollaus,
  input  logic tulo,        // 1 = painettu
  output logic tila,        // suodatettu tila
  output logic painettu     // yhden jakson pulssi, kun tila nousee
);
  logic [1:0]        tahdistin = '0;
  logic [LEVEYS-1:0] laskuri = '0;

  initial begin tila = 1'b0; painettu = 1'b0; end

  always_ff @(posedge clk) begin
    tahdistin <= {tahdistin[0], tulo};
    painettu  <= 1'b0;
    if (nollaus) begin
      tila    <= 1'b0;
      laskuri <= '0;
    end else if (tahdistin[1] == tila) begin
      laskuri <= '0;              // värähdys: aloitetaan alusta
    end else begin
      laskuri <= laskuri + 1'b1;
      if (&laskuri) begin
        tila     <= tahdistin[1];
        painettu <= tahdistin[1];
      end
    end
  end
endmodule
// @loppu painike
