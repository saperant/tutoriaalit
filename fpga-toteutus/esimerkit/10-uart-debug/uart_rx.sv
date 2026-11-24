// UART-vastaanotin (8N1). Tulo tahdistetaan kellotusalueeseen kahdella
// kiikulla, ja bitit näytteistetään bittiajan keskeltä.
module uart_rx #(
  parameter int KELLOT_PER_BITTI = 104      // 12 MHz / 115200
) (
  input  logic       clk,
  input  logic       rx,
  output logic       kelpaa,
  output logic [7:0] tavu
);
  localparam int L = $clog2(KELLOT_PER_BITTI);
  logic [1:0]   tahdistin = 2'b11;
  logic         lepo = 1'b1;
  logic [L-1:0] ajastin = '0;
  logic [3:0]   bitti = '0;
  logic [7:0]   siirto = '0;

  always_ff @(posedge clk) begin
    tahdistin <= {tahdistin[0], rx};
    kelpaa <= 1'b0;
    if (lepo) begin
      if (!tahdistin[1]) begin              // aloitusbitin reuna
        lepo    <= 1'b0;
        ajastin <= L'(KELLOT_PER_BITTI / 2);
        bitti   <= '0;
      end
    end else if (ajastin != 0) begin
      ajastin <= ajastin - 1'b1;
    end else begin
      ajastin <= L'(KELLOT_PER_BITTI - 1);
      bitti   <= bitti + 1'b1;
      if (bitti >= 4'd1 && bitti <= 4'd8)
        siirto <= {tahdistin[1], siirto[7:1]};
      if (bitti == 4'd9) begin               // lopetusbitti
        lepo   <= 1'b1;
        kelpaa <= tahdistin[1];
        tavu   <= siirto;
      end
    end
  end
endmodule
