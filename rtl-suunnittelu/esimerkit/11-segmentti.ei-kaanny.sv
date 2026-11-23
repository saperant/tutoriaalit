// Virheellinen: BCD-dekooderi kattaa vain numerot 0-9. Arvoilla 10-15
// segmentit jäävät edelliseen arvoon, eli syntyy salpa.
module segmentit_vajaa (                    // @virhe
  input  logic [3:0] numero,                // @virhe
  output logic [6:0] seg                    // @virhe
);                                          // @virhe
  always_comb begin                         // @virhe
    case (numero)                           // @virhe
      4'd0: seg = 7'b011_1111;              // @virhe
      4'd1: seg = 7'b000_0110;              // @virhe
      4'd2: seg = 7'b101_1011;              // @virhe
      4'd3: seg = 7'b100_1111;              // @virhe
      4'd4: seg = 7'b110_0110;              // @virhe
      4'd5: seg = 7'b110_1101;              // @virhe
      4'd6: seg = 7'b111_1101;              // @virhe
      4'd7: seg = 7'b000_0111;              // @virhe
      4'd8: seg = 7'b111_1111;              // @virhe
      4'd9: seg = 7'b110_1111;              // @virhe
    endcase                                 // @virhe
  end                                       // @virhe
endmodule                                   // @virhe

// @alku oikein
// Oikein: default kertoo, mitä virheellinen syöte näyttää (viiva).
// Segmentit gfedcba, 1 = palaa.
module segmentit (
  input  logic [3:0] numero,
  output logic [6:0] seg
);
  always_comb begin
    case (numero)
      4'd0:    seg = 7'b011_1111;
      4'd1:    seg = 7'b000_0110;
      4'd2:    seg = 7'b101_1011;
      4'd3:    seg = 7'b100_1111;
      4'd4:    seg = 7'b110_0110;
      4'd5:    seg = 7'b110_1101;
      4'd6:    seg = 7'b111_1101;
      4'd7:    seg = 7'b000_0111;
      4'd8:    seg = 7'b111_1111;
      4'd9:    seg = 7'b110_1111;
      default: seg = 7'b100_0000;           // keskiviiva: ei BCD-luku
    endcase
  end
endmodule
// @loppu oikein

module testipenkki;
  logic [3:0] numero = 4'd7;
  logic [6:0] seg;
  logic [6:0] seg_vajaa;                    // @virhe
  segmentit       u_s (.numero, .seg);
  segmentit_vajaa u_v (.numero, .seg(seg_vajaa));   // @virhe
  initial begin
    #1 $display("numero 7:  seg = %b", seg);
    numero = 4'd12;
    #1 $display("numero 12: seg = %b", seg);
    $display("vajaa: %b", seg_vajaa);       // @virhe
  end
endmodule
