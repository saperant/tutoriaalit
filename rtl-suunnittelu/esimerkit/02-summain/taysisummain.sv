// Yhden bitin täysisummain.
module taysisummain (
  input  logic a,
  input  logic b,
  input  logic muistibitti_sisaan,
  output logic summa,
  output logic muistibitti_ulos
);
  assign summa            = a ^ b ^ muistibitti_sisaan;
  assign muistibitti_ulos = (a & b) | (muistibitti_sisaan & (a ^ b));
endmodule
