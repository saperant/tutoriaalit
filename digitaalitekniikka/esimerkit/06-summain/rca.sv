// @alku rca
// Ripple-carry-summain: N täyssummainta ketjussa. Muistibitti kulkee
// bitistä seuraavaan, joten viive kasvaa lineaarisesti.
module rca #(
  parameter int N = 8
) (
  input  logic [N-1:0] a,
  input  logic [N-1:0] b,
  input  logic         cin,
  output logic [N-1:0] s,
  output logic         cout
);
  logic [N:0] c;
  assign c[0] = cin;

  for (genvar i = 0; i < N; i++) begin : g_bitti
    taysisummain u_fa (.a(a[i]), .b(b[i]), .cin(c[i]),
                       .s(s[i]), .cout(c[i+1]));
  end

  assign cout = c[N];
endmodule
// @loppu rca
