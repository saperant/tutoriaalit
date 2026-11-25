// Heksanumeroiden 8x8-pistematriisi (omat merkit). Rivi on kahdeksan
// pikseliä vasemmalta oikealle, ylin bitti vasemmalla. Vakiotaulukko,
// jota luetaan ilman kelloa, syntetisoituu hakutauluiksi (luku 4).
module fontti (
  input  logic [3:0] merkki,
  input  logic [2:0] rivi,
  output logic [7:0] pikselit
);
  always_comb
    unique case ({merkki, rivi})
      7'h00: pikselit = 8'b00111100; 7'h01: pikselit = 8'b01100110;
      7'h02: pikselit = 8'b01101110; 7'h03: pikselit = 8'b01110110;
      7'h04: pikselit = 8'b01100110; 7'h05: pikselit = 8'b01100110;
      7'h06: pikselit = 8'b00111100; 7'h07: pikselit = 8'b00000000;
      7'h08: pikselit = 8'b00011000; 7'h09: pikselit = 8'b00111000;
      7'h0a: pikselit = 8'b00011000; 7'h0b: pikselit = 8'b00011000;
      7'h0c: pikselit = 8'b00011000; 7'h0d: pikselit = 8'b00011000;
      7'h0e: pikselit = 8'b00111100; 7'h0f: pikselit = 8'b00000000;
      7'h10: pikselit = 8'b00111100; 7'h11: pikselit = 8'b01100110;
      7'h12: pikselit = 8'b00000110; 7'h13: pikselit = 8'b00001100;
      7'h14: pikselit = 8'b00011000; 7'h15: pikselit = 8'b00110000;
      7'h16: pikselit = 8'b01111110; 7'h17: pikselit = 8'b00000000;
      7'h18: pikselit = 8'b00111100; 7'h19: pikselit = 8'b01100110;
      7'h1a: pikselit = 8'b00000110; 7'h1b: pikselit = 8'b00011100;
      7'h1c: pikselit = 8'b00000110; 7'h1d: pikselit = 8'b01100110;
      7'h1e: pikselit = 8'b00111100; 7'h1f: pikselit = 8'b00000000;
      7'h20: pikselit = 8'b00001100; 7'h21: pikselit = 8'b00011100;
      7'h22: pikselit = 8'b00111100; 7'h23: pikselit = 8'b01101100;
      7'h24: pikselit = 8'b01111110; 7'h25: pikselit = 8'b00001100;
      7'h26: pikselit = 8'b00001100; 7'h27: pikselit = 8'b00000000;
      7'h28: pikselit = 8'b01111110; 7'h29: pikselit = 8'b01100000;
      7'h2a: pikselit = 8'b01111100; 7'h2b: pikselit = 8'b00000110;
      7'h2c: pikselit = 8'b00000110; 7'h2d: pikselit = 8'b01100110;
      7'h2e: pikselit = 8'b00111100; 7'h2f: pikselit = 8'b00000000;
      7'h30: pikselit = 8'b00011100; 7'h31: pikselit = 8'b00110000;
      7'h32: pikselit = 8'b01100000; 7'h33: pikselit = 8'b01111100;
      7'h34: pikselit = 8'b01100110; 7'h35: pikselit = 8'b01100110;
      7'h36: pikselit = 8'b00111100; 7'h37: pikselit = 8'b00000000;
      7'h38: pikselit = 8'b01111110; 7'h39: pikselit = 8'b00000110;
      7'h3a: pikselit = 8'b00001100; 7'h3b: pikselit = 8'b00011000;
      7'h3c: pikselit = 8'b00110000; 7'h3d: pikselit = 8'b00110000;
      7'h3e: pikselit = 8'b00110000; 7'h3f: pikselit = 8'b00000000;
      7'h40: pikselit = 8'b00111100; 7'h41: pikselit = 8'b01100110;
      7'h42: pikselit = 8'b01100110; 7'h43: pikselit = 8'b00111100;
      7'h44: pikselit = 8'b01100110; 7'h45: pikselit = 8'b01100110;
      7'h46: pikselit = 8'b00111100; 7'h47: pikselit = 8'b00000000;
      7'h48: pikselit = 8'b00111100; 7'h49: pikselit = 8'b01100110;
      7'h4a: pikselit = 8'b01100110; 7'h4b: pikselit = 8'b00111110;
      7'h4c: pikselit = 8'b00000110; 7'h4d: pikselit = 8'b00001100;
      7'h4e: pikselit = 8'b00111000; 7'h4f: pikselit = 8'b00000000;
      7'h50: pikselit = 8'b00011000; 7'h51: pikselit = 8'b00111100;
      7'h52: pikselit = 8'b01100110; 7'h53: pikselit = 8'b01100110;
      7'h54: pikselit = 8'b01111110; 7'h55: pikselit = 8'b01100110;
      7'h56: pikselit = 8'b01100110; 7'h57: pikselit = 8'b00000000;
      7'h58: pikselit = 8'b01111100; 7'h59: pikselit = 8'b01100110;
      7'h5a: pikselit = 8'b01100110; 7'h5b: pikselit = 8'b01111100;
      7'h5c: pikselit = 8'b01100110; 7'h5d: pikselit = 8'b01100110;
      7'h5e: pikselit = 8'b01111100; 7'h5f: pikselit = 8'b00000000;
      7'h60: pikselit = 8'b00111100; 7'h61: pikselit = 8'b01100110;
      7'h62: pikselit = 8'b01100000; 7'h63: pikselit = 8'b01100000;
      7'h64: pikselit = 8'b01100000; 7'h65: pikselit = 8'b01100110;
      7'h66: pikselit = 8'b00111100; 7'h67: pikselit = 8'b00000000;
      7'h68: pikselit = 8'b01111000; 7'h69: pikselit = 8'b01101100;
      7'h6a: pikselit = 8'b01100110; 7'h6b: pikselit = 8'b01100110;
      7'h6c: pikselit = 8'b01100110; 7'h6d: pikselit = 8'b01101100;
      7'h6e: pikselit = 8'b01111000; 7'h6f: pikselit = 8'b00000000;
      7'h70: pikselit = 8'b01111110; 7'h71: pikselit = 8'b01100000;
      7'h72: pikselit = 8'b01100000; 7'h73: pikselit = 8'b01111100;
      7'h74: pikselit = 8'b01100000; 7'h75: pikselit = 8'b01100000;
      7'h76: pikselit = 8'b01111110; 7'h77: pikselit = 8'b00000000;
      7'h78: pikselit = 8'b01111110; 7'h79: pikselit = 8'b01100000;
      7'h7a: pikselit = 8'b01100000; 7'h7b: pikselit = 8'b01111100;
      7'h7c: pikselit = 8'b01100000; 7'h7d: pikselit = 8'b01100000;
      7'h7e: pikselit = 8'b01100000; 7'h7f: pikselit = 8'b00000000;
      default: pikselit = '0;
    endcase
endmodule
