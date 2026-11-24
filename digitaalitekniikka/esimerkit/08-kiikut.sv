// D-salpa ja D-kiikku rinnakkain: sama syöte, eri käytös.

// @alku salpa
// D-salpa on läpinäkyvä, kun sallinta on 1: lähtö seuraa syötettä.
// Kun sallinta laskee, salpa pitää viimeisen arvon.
module d_salpa (
  input  logic en,
  input  logic d,
  output logic q
);
  always_latch begin
    if (en) q = d;
  end
endmodule
// @loppu salpa

// @alku kiikku
// D-kiikku näytteistää syötteen vain kellon nousevalla reunalla.
module d_kiikku (
  input  logic clk,
  input  logic d,
  output logic q
);
  always_ff @(posedge clk) q <= d;
endmodule
// @loppu kiikku

// @alku testipenkki
module testipenkki;
  logic clk = 1'b0, d = 1'b0;
  logic q_salpa, q_kiikku;

  d_salpa  u_salpa  (.en(clk), .d, .q(q_salpa));
  d_kiikku u_kiikku (.clk, .d, .q(q_kiikku));

  // Kello: ylhäällä hetkinä 10–19, 30–39, ...
  initial repeat (6) #10 clk = ~clk;

  // D muuttuu sekä kellon ollessa alhaalla että ylhäällä.
  initial begin
    #5  d = 1'b1;          // ennen ensimmäistä reunaa (hetki 5)
    #10 d = 1'b0;          // kellon ollessa ylhäällä (hetki 15)
    #20 d = 1'b1;          // taas ylhäällä (hetki 35)
  end

  // Näytteet hetkinä 2, 7, 12, ... eli muutosten välissä.
  initial begin
    $display("aika clk d  salpa kiikku");
    #2;
    repeat (10) begin
      $display("%4d  %b  %b    %b     %b", $time, clk, d, q_salpa,
               q_kiikku);
      #5;
    end
  end
endmodule
// @loppu testipenkki
