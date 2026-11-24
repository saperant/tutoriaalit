// @alku suodin
// Neljän kertoimen FIR-suodin y = k0 x[n] + k1 x[n-1] + k2 x[n-2]
// + k3 x[n-3]. Kertoimet kirjoitetaan ajon aikana x-väylän kautta.
// RINNAKKAIN = 1: neljä kertojaa, uusi näyte joka jaksolla.
// RINNAKKAIN = 0: yksi kertoja jaetaan, uusi näyte joka viides jakso.
module suodin #(
  parameter bit RINNAKKAIN = 1'b1
) (
  input  logic        clk,
  input  logic        nollaus,
  input  logic        k_kirjoita,   // x on kertoimen k_osoite arvo
  input  logic [1:0]  k_osoite,
  input  logic        x_kelpaa,
  input  logic [7:0]  x,
  output logic        valmis,       // suodin ottaa näytteen vastaan
  output logic        y_kelpaa,
  output logic [17:0] y
);
  logic [7:0] k0, k1, k2, k3;       // kertoimet

  always_ff @(posedge clk)
    if (k_kirjoita)
      case (k_osoite)
        2'd0: k0 <= x;
        2'd1: k1 <= x;
        2'd2: k2 <= x;
        default: k3 <= x;
      endcase
// @loppu suodin

// @alku rinnakkain
  if (RINNAKKAIN) begin : g_rinnakkain
    logic [7:0] x0, x1, x2;         // x[n-1], x[n-2], x[n-3]
    assign valmis = 1'b1;
    always_ff @(posedge clk) begin
      y_kelpaa <= 1'b0;
      if (nollaus) begin
        {x0, x1, x2} <= '0;
      end else if (x_kelpaa) begin
        {x0, x1, x2} <= {x, x0, x1};
        y <= 18'(k0 * x) + 18'(k1 * x0) + 18'(k2 * x1) + 18'(k3 * x2);
        y_kelpaa <= 1'b1;
      end
    end
// @loppu rinnakkain
// @alku jaettu
  end else begin : g_jaettu
    logic [7:0]  x0, x1, x2, x3;     // x[n], x[n-1], x[n-2], x[n-3]
    logic [1:0]  vaihe;
    logic        laskee;
    logic [17:0] summa;
    logic [7:0]  k, xv;
    assign valmis = !laskee;
    // Multiplekseri valitsee vaiheen kertoimen ja näytteen yhdelle
    // kertojalle.
    always_comb
      case (vaihe)
        2'd0:    begin k = k0; xv = x0; end
        2'd1:    begin k = k1; xv = x1; end
        2'd2:    begin k = k2; xv = x2; end
        default: begin k = k3; xv = x3; end
      endcase
    always_ff @(posedge clk) begin
      y_kelpaa <= 1'b0;
      if (nollaus) begin
        {x0, x1, x2, x3} <= '0;
        laskee <= 1'b0;
        vaihe  <= '0;
      end else if (!laskee && x_kelpaa) begin
        {x0, x1, x2, x3} <= {x, x0, x1, x2};
        summa  <= '0;
        vaihe  <= '0;
        laskee <= 1'b1;
      end else if (laskee) begin
        summa <= summa + 18'(k * xv);
        vaihe <= vaihe + 1'b1;
        if (vaihe == 2'd3) begin
          y        <= summa + 18'(k * xv);
          y_kelpaa <= 1'b1;
          laskee   <= 1'b0;
        end
      end
    end
  end
endmodule
// @loppu jaettu
