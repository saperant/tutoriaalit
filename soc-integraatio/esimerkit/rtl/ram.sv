// RAM: AXI4-Lite-orja, jonka muisti on 32-bittisiä sanoja.
//
// Luku: AR-kättelyä seuraavalla kellojaksolla R-kanavalla on data.
// Kirjoitus: AW ja W hyväksytään samalla jaksolla, kun molemmat ovat
// voimassa (AXI sallii orjan odottaa molempia), ja vastaus tulee
// seuraavalla jaksolla. Ohjelma ladataan simulaatiossa testipenkistä.
module ram
  import vaylat::*;
#(
  parameter int SANAT = 4096           // 16 KiB
)(
  input  logic      kello,
  input  logic      nollaus_n,
  input  axil_m2s_t m,
  output axil_s2m_t s
);

  localparam int AB = $clog2(SANAT);
  logic [31:0] muisti [SANAT];

  logic [AB-1:0] luku_ind, kirj_ind;
  assign luku_ind = m.araddr[AB+1:2];
  assign kirj_ind = m.awaddr[AB+1:2];

  logic        r_voimassa, b_voimassa;
  logic [31:0] r_data;

  // @alku orja
  logic kirjoita;
  always_comb begin
    s         = '0;
    s.arready = !r_voimassa;
    s.awready = m.awvalid && m.wvalid && !b_voimassa;
    s.wready  = s.awready;
    s.rvalid  = r_voimassa;
    s.rdata   = r_data;
    s.bvalid  = b_voimassa;
    s.rresp   = OKAY;
    s.bresp   = OKAY;
  end
  assign kirjoita = s.awready;   // AW ja W kättelevät samalla jaksolla
  // @loppu orja

  // Tavukohtainen kirjoitus maskilla: WSTRB:n bitti valitsee tavun.
  logic [31:0] maski;
  assign maski = {{8{m.wstrb[3]}}, {8{m.wstrb[2]}},
                  {8{m.wstrb[1]}}, {8{m.wstrb[0]}}};
  always_ff @(posedge kello) begin
    if (kirjoita)
      muisti[kirj_ind] <= (muisti[kirj_ind] & ~maski) | (m.wdata & maski);
  end

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      r_voimassa <= 1'b0;
      b_voimassa <= 1'b0;
      r_data     <= 32'd0;
    end else begin
      if (m.arvalid && s.arready) begin
        r_voimassa <= 1'b1;
        r_data     <= muisti[luku_ind];
      end else if (m.rready) begin
        r_voimassa <= 1'b0;
      end
      if (kirjoita)       b_voimassa <= 1'b1;
      else if (m.bready)  b_voimassa <= 1'b0;
    end
  end

endmodule
