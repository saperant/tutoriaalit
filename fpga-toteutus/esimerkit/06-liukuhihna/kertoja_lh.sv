// @alku kertoja_lh
// Logiikkasoluilla toteutettu 8 x 8 bitin kertoja. VAIHEET = 1: tulo
// lasketaan yhdessä kellojaksossa. VAIHEET = 2: ensin kaksi 8 x 4 bitin
// osatuloa, seuraavalla jaksolla niiden summa. Lisävaihe lyhentää
// pisintä kombinatorista polkua mutta pidentää latenssia jaksolla.
module kertoja_lh #(
  parameter int VAIHEET = 2
) (
  input  logic        clk,
  input  logic [7:0]  a,
  input  logic [7:0]  b,
  output logic [15:0] tulo
);
  logic [7:0] ra, rb;
  always_ff @(posedge clk) begin
    ra <= a;
    rb <= b;
  end

  if (VAIHEET == 1) begin : g_yksi
    always_ff @(posedge clk) tulo <= ra * rb;
  end else begin : g_kaksi
    logic [11:0] ala, yla;
    always_ff @(posedge clk) begin
      ala  <= ra * rb[3:0];
      yla  <= ra * rb[7:4];
      tulo <= 16'(ala) + (16'(yla) << 4);
    end
  end
endmodule
// @loppu kertoja_lh
