// N-bittinen ripple-carry-summain täysisummaimista.
module summain #(
  parameter int N = 8
) (
  input  logic [N-1:0] a,
  input  logic [N-1:0] b,
  input  logic         muistibitti_sisaan,
  output logic [N-1:0] summa,
  output logic         muistibitti_ulos
);
  // muisti[i] on bitin i muistibitti sisään.
  logic [N:0] muisti;
  assign muisti[0] = muistibitti_sisaan;

  for (genvar i = 0; i < N; i++) begin : g_bitti
    taysisummain u_ts (
      .a                 (a[i]),
      .b                 (b[i]),
      .muistibitti_sisaan(muisti[i]),
      .summa             (summa[i]),
      .muistibitti_ulos  (muisti[i+1])
    );
  end

  assign muistibitti_ulos = muisti[N];
endmodule
