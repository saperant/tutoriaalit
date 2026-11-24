// Tuotettu tiedostosta asetukset/rekisterit.toml (vuo/rekisterit.py).
// Älä muokkaa käsin: muutokset tehdään kuvaukseen.
module ajastin_regs (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        kirjoita,
  input  logic [7:0]  osoite,
  /* verilator lint_off UNUSEDSIGNAL */
  input  logic [31:0] wdata,   // kaikkia bittejä ei käytetä
  /* verilator lint_on UNUSEDSIGNAL */
  // CTRL: Ohjaus
  output logic        ctrl_en,
  output logic        ctrl_ie,
  output logic [7:0]  ctrl_jakaja,
  // STATUS: Tila
  input  logic        status_valmis_aseta,
  output logic        status_valmis,
  // LASKURI: Laskurin arvo
  input  logic [15:0] laskuri_arvo,
  // VERTAA: Vertailuarvo
  output logic [15:0] vertaa_arvo,
  output logic [31:0] rdata
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      ctrl_en <= 1'h0;
      ctrl_ie <= 1'h0;
      ctrl_jakaja <= 8'h1;
      status_valmis <= 1'h0;
      vertaa_arvo <= 16'hFFFF;
    end else begin
      if (kirjoita && osoite == 8'h00) begin
        ctrl_en <= wdata[0];
        ctrl_ie <= wdata[1];
        ctrl_jakaja <= wdata[15:8];
      end
      if (status_valmis_aseta) status_valmis <= 1'b1;
      else if (kirjoita && osoite == 8'h04 && wdata[0])
        status_valmis <= 1'b0;
      if (kirjoita && osoite == 8'h0C) begin
        vertaa_arvo <= wdata[15:0];
      end
    end
  end

  always_comb begin
    rdata = '0;
    case (osoite)
      8'h00: begin
        rdata[0] = ctrl_en;
        rdata[1] = ctrl_ie;
        rdata[15:8] = ctrl_jakaja;
      end
      8'h04: begin
        rdata[0] = status_valmis;
      end
      8'h08: begin
        rdata[15:0] = laskuri_arvo;
      end
      8'h0C: begin
        rdata[15:0] = vertaa_arvo;
      end
      default: ;
    endcase
  end
endmodule
