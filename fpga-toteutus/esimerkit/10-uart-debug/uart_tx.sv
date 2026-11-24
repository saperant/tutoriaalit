// UART-lähetin (8N1).
module uart_tx #(
  parameter int KELLOT_PER_BITTI = 104
) (
  input  logic       clk,
  input  logic       laheta,
  input  logic [7:0] tavu,
  output logic       valmis,
  output logic       tx
);
  localparam int L = $clog2(KELLOT_PER_BITTI);
  logic [9:0]   kehys = '1;      // lopetusbitti, data, aloitusbitti
  logic [3:0]   jaljella = '0;
  logic [L-1:0] ajastin = '0;

  assign valmis = jaljella == 0;
  assign tx = kehys[0];

  always_ff @(posedge clk) begin
    if (valmis) begin
      if (laheta) begin
        kehys    <= {1'b1, tavu, 1'b0};
        jaljella <= 4'd10;
        ajastin  <= L'(KELLOT_PER_BITTI - 1);
      end
    end else if (ajastin != 0) begin
      ajastin <= ajastin - 1'b1;
    end else begin
      ajastin  <= L'(KELLOT_PER_BITTI - 1);
      kehys    <= {1'b1, kehys[9:1]};
      jaljella <= jaljella - 1'b1;
    end
  end
endmodule
