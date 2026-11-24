// GENEROITU: python3 -m malli.generoi. Älä muokkaa käsin.
// CORDIC: atan(2**-i), täysi kierros = 2**18.
function automatic logic signed [17:0] cordic_kulma(input int i);
  case (i)
    0: cordic_kulma = 18'sd32768;
    1: cordic_kulma = 18'sd19344;
    2: cordic_kulma = 18'sd10221;
    3: cordic_kulma = 18'sd5188;
    4: cordic_kulma = 18'sd2604;
    5: cordic_kulma = 18'sd1303;
    6: cordic_kulma = 18'sd652;
    7: cordic_kulma = 18'sd326;
    8: cordic_kulma = 18'sd163;
    9: cordic_kulma = 18'sd81;
    10: cordic_kulma = 18'sd41;
    11: cordic_kulma = 18'sd20;
    12: cordic_kulma = 18'sd10;
    13: cordic_kulma = 18'sd5;
    14: cordic_kulma = 18'sd3;
    15: cordic_kulma = 18'sd1;
    default: cordic_kulma = 18'sd0;
  endcase
endfunction
