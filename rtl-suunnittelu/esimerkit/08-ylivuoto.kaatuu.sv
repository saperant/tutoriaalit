// Laskuriin perustuva FIFO, jossa on simulaation aikainen tarkistus:
// kirjoitus täyteen jonoon on aina suunnitteluvirhe kutsujassa.
module pieni_fifo #(parameter int SYVYYS = 4) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       kirjoita,
  input  logic [7:0] k_data,
  input  logic       lue,
  output logic [7:0] l_data,
  output logic       taynna,
  output logic       tyhja
);
  localparam int AW = $clog2(SYVYYS);
  logic [7:0]  muisti [SYVYYS];
  logic [AW-1:0] k_os, l_os;
  logic [AW:0]   maara;               // 0..SYVYYS

  assign taynna = (maara == (AW+1)'(SYVYYS));
  assign tyhja  = (maara == '0);
  assign l_data = muisti[l_os];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      {k_os, l_os, maara} <= '0;
    end else begin
      if (kirjoita && !taynna) begin
        muisti[k_os] <= k_data;
        k_os         <= k_os + 1'b1;
      end
      if (lue && !tyhja) l_os <= l_os + 1'b1;
      maara <= maara + (AW+1)'(kirjoita && !taynna)
                     - (AW+1)'(lue && !tyhja);
    end
  end

  // @alku tarkistus
  // Ei syntetisoidu laitteistoksi; synteesityökalu ohittaa $fatalin.
  always_ff @(posedge clk) begin
    if (kirjoita && taynna)
      $fatal(1, "pieni_fifo: kirjoitus täyteen jonoon, data %h",
             k_data);
    if (lue && tyhja)
      $fatal(1, "pieni_fifo: luku tyhjästä jonosta");
  end
  // @loppu tarkistus
endmodule

module testipenkki;
  logic       clk = 1'b0, rst_n = 1'b0;
  logic       kirjoita = 1'b0, lue = 1'b0, taynna;
  logic [7:0] k_data = '0;
  // Kuluttaja puuttuu tästä esimerkistä tarkoituksella.
  /* verilator lint_off UNUSEDSIGNAL */
  logic       tyhja;
  logic [7:0] l_data;
  /* verilator lint_on UNUSEDSIGNAL */

  pieni_fifo u_f (.clk, .rst_n, .kirjoita, .k_data, .lue, .l_data,
                  .taynna, .tyhja);

  initial forever #5 clk = ~clk;

  // @alku tuottaja
  // Virhe: tuottaja ei katso taynna-lippua.
  initial begin
    #12 rst_n = 1'b1;
    for (int i = 0; i < 6; i++) begin
      kirjoita = 1'b1;
      k_data   = 8'hA0 + 8'(i);
      $display("kirjoitetaan %h, taynna = %b", k_data, taynna);
      @(posedge clk); #1;
    end
  end
  // @loppu tuottaja
endmodule
