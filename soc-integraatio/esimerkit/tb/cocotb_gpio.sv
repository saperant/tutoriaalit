// cocotb-testien kääre GPIOlle: APB-väylä erillisinä signaaleina.
module cocotb_gpio
  import vaylat::*;
(
  input  logic        kello,
  input  logic        nollaus_n,
  input  logic [11:0] paddr,
  input  logic        psel,
  input  logic        penable,
  input  logic        pwrite,
  input  logic [31:0] pwdata,
  input  logic [3:0]  pstrb,
  output logic [31:0] prdata,
  output logic        pready,
  output logic        pslverr,
  output logic [7:0]  ulos,
  input  logic [7:0]  sisaan,
  output logic        keskeytys
);
  apb_m2s_t apb_m;
  apb_s2m_t apb_s;
  assign apb_m = {paddr, psel, penable, pwrite, pwdata, pstrb};
  assign {prdata, pready, pslverr} = apb_s;

  gpio u_gpio (.kello, .nollaus_n, .apb_m, .apb_s, .ulos, .sisaan,
               .keskeytys);
endmodule
