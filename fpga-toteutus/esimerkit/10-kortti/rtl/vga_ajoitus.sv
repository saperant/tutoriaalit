// @alku ajoitus
// VGA-ajoitus 640 x 480, 60 Hz. Rivi koostuu näkyvästä osasta,
// etukuistista, tahdistuspulssista ja takakuistista; kehys riveistä
// samassa järjestyksessä. Tahdistuspulssit ovat aktiivisia alhaalla.
module vga_ajoitus #(
  parameter int H_NAKYVA = 640, H_ETU = 16, H_TAHTI = 96, H_TAKA = 48,
  parameter int V_NAKYVA = 480, V_ETU = 10, V_TAHTI = 2,  V_TAKA = 33
) (
  input  logic       clk,
  input  logic       nollaus,
  output logic [9:0] x,          // pikselin paikka rivillä, 0..799
  output logic [9:0] y,          // rivi, 0..524
  output logic       nakyva,     // pikseli on kuva-alueella
  output logic       hsync_n,
  output logic       vsync_n,
  output logic       kehys       // pulssi kehyksen viimeisellä pikselillä
);
  localparam int H_YHT = H_NAKYVA + H_ETU + H_TAHTI + H_TAKA;   // 800
  localparam int V_YHT = V_NAKYVA + V_ETU + V_TAHTI + V_TAKA;   // 525

  initial begin x = '0; y = '0; end

  always_ff @(posedge clk)
    if (nollaus) begin
      x <= '0;
      y <= '0;
    end else if (x == 10'(H_YHT - 1)) begin
      x <= '0;
      y <= (y == 10'(V_YHT - 1)) ? '0 : y + 1'b1;
    end else begin
      x <= x + 1'b1;
    end

  assign nakyva  = x < 10'(H_NAKYVA) && y < 10'(V_NAKYVA);
  assign hsync_n = !(x >= 10'(H_NAKYVA + H_ETU) &&
                     x <  10'(H_NAKYVA + H_ETU + H_TAHTI));
  assign vsync_n = !(y >= 10'(V_NAKYVA + V_ETU) &&
                     y <  10'(V_NAKYVA + V_ETU + V_TAHTI));
  assign kehys   = x == 10'(H_YHT - 1) && y == 10'(V_YHT - 1);
endmodule
// @loppu ajoitus
