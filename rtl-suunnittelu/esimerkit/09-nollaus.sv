// @alku tahdistin
// Nollauksen tahdistin: nollaus kytkeytyy päälle heti (asynkronisesti)
// mutta vapautuu vasta kellon reunalla kahden kiikun kautta. Näin
// vapautus ei osu kiikkujen asetus- ja pitoaikaikkunaan.
module nollaus_tahdistin (
  input  logic clk,
  input  logic rst_n_ulkoinen,        // esim. nappi tai PLL:n lukitus
  output logic rst_n                  // käytetään koko kellotusalueessa
);
  logic [1:0] ketju;
  always_ff @(posedge clk or negedge rst_n_ulkoinen) begin
    if (!rst_n_ulkoinen) ketju <= 2'b00;
    else                 ketju <= {ketju[0], 1'b1};
  end
  assign rst_n = ketju[1];
endmodule
// @loppu tahdistin

// @alku tyylit
// Asynkroninen nollaus: herkkyyslistassa, toimii ilman kelloa.
module rekisteri_async (
  input  logic       clk, rst_n,
  input  logic [7:0] d,
  output logic [7:0] q
);
  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) q <= '0;
    else        q <= d;
endmodule

// Synkroninen nollaus: vain tavallinen ehto, vaatii kellon reunan.
module rekisteri_sync (
  input  logic       clk, rst_n,
  input  logic [7:0] d,
  output logic [7:0] q
);
  always_ff @(posedge clk)
    if (!rst_n) q <= '0;
    else        q <= d;
endmodule
// @loppu tyylit

module testipenkki;
  logic       clk = 1'b0, kello_kay = 1'b1, kaynnissa = 1'b1;
  logic       rst_n_ulk = 1'b0, rst_n, rst_n_kaikille = 1'b1;
  logic       rst_n_sync = 1'b1;
  logic [7:0] d = 8'h5A, q_async, q_sync;

  nollaus_tahdistin u_nt (.clk, .rst_n_ulkoinen(rst_n_ulk), .rst_n);
  rekisteri_async   u_a  (.clk, .rst_n(rst_n_kaikille), .d, .q(q_async));
  rekisteri_sync    u_s  (.clk, .rst_n(rst_n_sync), .d, .q(q_sync));

  initial while (kaynnissa) begin
    #5 if (kello_kay) clk = ~clk;
  end

  initial begin
    // Ulkoinen nollaus vapautuu keskellä jaksoa (t = 23).
    #23 rst_n_ulk = 1'b1;
    @(posedge rst_n);
    $display("ulkoinen vapautus t = 23, tahdistettu t = %0t", $time);
    // Kello pysähtyy, ja molempiin rekistereihin tulee nollaus.
    @(posedge clk); #1;
    $display("ennen nollausta: async %h, sync %h", q_async, q_sync);
    kello_kay      = 1'b0;
    rst_n_kaikille = 1'b0;
    rst_n_sync     = 1'b0;
    #30;
    $display("kello seis:      async %h, sync %h", q_async, q_sync);
    kello_kay = 1'b1;
    @(posedge clk); #1;
    $display("reunan jälkeen:  async %h, sync %h", q_async, q_sync);
    if (q_sync != 8'h00) $fatal(1, "synkroninen nollaus ei toiminut");
    kaynnissa = 1'b0;
  end
endmodule
