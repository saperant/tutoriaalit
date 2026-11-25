// @alku rajapinta
// Kättelyväylä rajapintana: signaalit esitellään kerran, ja modport
// kertoo suunnat kummankin osapuolen näkökulmasta.
interface virta_if #(parameter int W = 8);
  logic         kelv;
  logic         valmis;
  logic [W-1:0] data;

  modport lahde (output kelv, data, input  valmis);
  modport nielu (input  kelv, data, output valmis);
endinterface
// @loppu rajapinta

// @alku vaihe
// Sama rekisterivaihe kuin edellä, mutta portteina kaksi rajapintaa.
module vaihe_if (
  input logic   clk,
  input logic   rst_n,
  virta_if.nielu sisaan,
  virta_if.lahde ulos
);
  assign sisaan.valmis = !ulos.kelv || ulos.valmis;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)             ulos.kelv <= 1'b0;
    else if (sisaan.valmis) ulos.kelv <= sisaan.kelv;
  end

  always_ff @(posedge clk) begin
    if (sisaan.valmis && sisaan.kelv) ulos.data <= sisaan.data + 8'd1;
  end
endmodule
// @loppu vaihe

module testipenkki;
  logic clk = 1'b0, rst_n = 1'b0, kaynnissa = 1'b1;
  int   perilla = 0;

  // @alku kytkenta
  virta_if #(.W(8)) a (), b (), c ();

  vaihe_if u_1 (.clk, .rst_n, .sisaan(a), .ulos(b));
  vaihe_if u_2 (.clk, .rst_n, .sisaan(b), .ulos(c));
  // @loppu kytkenta

  initial while (kaynnissa) #5 clk = ~clk;

  always @(posedge clk) begin
    if (c.kelv && c.valmis) begin
      if (c.data != 8'(perilla + 2)) $fatal(1, "väärä sana %0d", c.data);
      perilla <= perilla + 1;
    end
  end

  initial begin
    a.kelv = 1'b0; a.data = '0; c.valmis = 1'b0;
    #12 rst_n = 1'b1;
    @(posedge clk); #1;
    for (int i = 0; i < 20; i++) begin
      a.kelv   = 1'b1;
      a.data   = 8'(i);
      c.valmis = (i % 3 != 1);              // joka kolmas jakso seis
      @(negedge clk);
      while (!a.valmis) begin               // odota, kunnes sana siirtyy
        @(posedge clk); #1 c.valmis = 1'b1;
        @(negedge clk);
      end
      @(posedge clk); #1;
    end
    a.kelv   = 1'b0;
    c.valmis = 1'b1;
    repeat (4) @(posedge clk);
    $display("rajapinnan läpi %0d sanaa, kumpikin vaihe lisäsi 1",
             perilla);
    if (perilla != 20) $fatal(1, "sanoja katosi");
    kaynnissa = 1'b0;
  end
endmodule
