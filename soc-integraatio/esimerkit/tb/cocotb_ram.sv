// cocotb-testien kääre RAM:lle: AXI4-Lite-väylä erillisinä
// signaaleina. Pakattu rakenne näkyisi Pythonille yhtenä leveänä
// vektorina, joten kenttiä ei voisi käsitellä nimeltä.
module cocotb_ram
  import vaylat::*;
#(
  parameter int SANAT = 64
)(
  input  logic        kello,
  input  logic        nollaus_n,
  input  logic [31:0] awaddr,
  input  logic        awvalid,
  output logic        awready,
  input  logic [31:0] wdata,
  input  logic [3:0]  wstrb,
  input  logic        wvalid,
  output logic        wready,
  output logic [1:0]  bresp,
  output logic        bvalid,
  input  logic        bready,
  input  logic [31:0] araddr,
  input  logic        arvalid,
  output logic        arready,
  output logic [31:0] rdata,
  output logic [1:0]  rresp,
  output logic        rvalid,
  input  logic        rready
);
  axil_m2s_t m;
  axil_s2m_t s;
  // Kenttien järjestys on sama kuin rakenteessa (ensimmäinen ylimpänä).
  assign m = {awaddr, awvalid, wdata, wstrb, wvalid, bready,
              araddr, arvalid, rready};
  assign {awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid} = s;

  ram #(.SANAT(SANAT)) u_ram (.kello, .nollaus_n, .m, .s);
endmodule
