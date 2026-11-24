// @alku taysisummain
// Täyssummain porttitasolla: summa ja muistibitti kolmesta bitistä.
module taysisummain (
  input  logic a,
  input  logic b,
  input  logic cin,
  output logic s,
  output logic cout
);
  logic x;
  assign x    = a ^ b;
  assign s    = x ^ cin;
  assign cout = (a & b) | (x & cin);
endmodule
// @loppu taysisummain
