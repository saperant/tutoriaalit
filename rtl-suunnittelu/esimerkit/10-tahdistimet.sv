// @alku taso
// Kahden kiikun tahdistin yksibittiselle tasosignaalille. Ensimmäinen
// kiikku voi joutua metastabiiliin tilaan; toinen antaa sille kokonaisen
// kellojakson aikaa asettua. Synteesissä kiikut merkitään (esim.
// ASYNC_REG), jotta ne sijoitetaan vierekkäin.
module tahdistin (
  input  logic clk,                   // vastaanottavan alueen kello
  input  logic rst_n,
  input  logic d,                     // toisesta kellotusalueesta
  output logic q
);
  logic meta;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) {q, meta} <= 2'b00;
    else        {q, meta} <= {meta, d};
  end
endmodule
// @loppu taso

// @alku pulssi
// Pulssin siirto: lähtöpuolella pulssi kääntää tasoa, taso
// tahdistetaan, ja vastaanottopuoli tunnistaa muutoksen. Toimii mihin
// tahansa suuntaan, kunhan pulssien väli on ainakin kolme hitaamman
// kellon jaksoa.
module pulssi_cdc (
  input  logic clk_a, rst_a_n,
  input  logic pulssi_a,
  input  logic clk_b, rst_b_n,
  output logic pulssi_b
);
  logic taso_a, taso_b, taso_b_ed;

  always_ff @(posedge clk_a or negedge rst_a_n) begin
    if (!rst_a_n)     taso_a <= 1'b0;
    else if (pulssi_a) taso_a <= ~taso_a;
  end

  tahdistin u_t (.clk(clk_b), .rst_n(rst_b_n), .d(taso_a), .q(taso_b));

  always_ff @(posedge clk_b or negedge rst_b_n) begin
    if (!rst_b_n) taso_b_ed <= 1'b0;
    else          taso_b_ed <= taso_b;
  end
  assign pulssi_b = taso_b ^ taso_b_ed;
endmodule
// @loppu pulssi

// @alku kattely
// Monibittisen arvon siirto nelivaiheisella kättelyllä: data pysyy
// vakaana, kun pyyntö kulkee tahdistimen läpi. Vain yksibittiset
// pyynto ja kuittaus ylittävät rajan tahdistettuina.
module kattely_cdc #(parameter int W = 16) (
  input  logic         clk_a, rst_a_n,
  input  logic         laheta,        // pulssi, kun vapaa = 1
  input  logic [W-1:0] data_a,
  output logic         vapaa,
  input  logic         clk_b, rst_b_n,
  output logic         saapui,        // pulssi
  output logic [W-1:0] data_b
);
  logic         pyynto, kuittaus;     // pyynto: A, kuittaus: B
  logic         pyynto_b, kuittaus_a;
  logic [W-1:0] pito;                 // vakaa rajan yli siirron ajan

  tahdistin u_req (.clk(clk_b), .rst_n(rst_b_n), .d(pyynto),
                   .q(pyynto_b));
  tahdistin u_ack (.clk(clk_a), .rst_n(rst_a_n), .d(kuittaus),
                   .q(kuittaus_a));

  assign vapaa = !pyynto && !kuittaus_a;

  always_ff @(posedge clk_a or negedge rst_a_n) begin
    if (!rst_a_n) begin
      pyynto <= 1'b0;
      pito   <= '0;
    end else if (laheta && vapaa) begin
      pyynto <= 1'b1;
      pito   <= data_a;
    end else if (kuittaus_a) begin
      pyynto <= 1'b0;
    end
  end

  always_ff @(posedge clk_b or negedge rst_b_n) begin
    if (!rst_b_n) begin
      kuittaus <= 1'b0;
      saapui   <= 1'b0;
      data_b   <= '0;
    end else begin
      saapui   <= pyynto_b && !kuittaus;
      if (pyynto_b && !kuittaus) data_b <= pito;  // pito on vakaa
      kuittaus <= pyynto_b;
    end
  end
endmodule
// @loppu kattely

module testipenkki;
  logic        clk_a = 1'b0, clk_b = 1'b0, kaynnissa = 1'b1;
  logic        rst_n = 1'b0;
  logic        pulssi_a = 1'b0, pulssi_b;
  logic        laheta = 1'b0, vapaa, saapui;
  logic [15:0] data_a = '0, data_b;
  int          pulsseja_b = 0, saapuneita = 0, summa_b = 0;

  pulssi_cdc u_p (.clk_a, .rst_a_n(rst_n), .pulssi_a, .clk_b,
                  .rst_b_n(rst_n), .pulssi_b);
  kattely_cdc #(.W(16)) u_k (.clk_a, .rst_a_n(rst_n), .laheta, .data_a,
                             .vapaa, .clk_b, .rst_b_n(rst_n), .saapui,
                             .data_b);

  // Kellot ilman yhteistä jaksoa: 100 MHz ja noin 27 MHz.
  initial while (kaynnissa) #5  clk_a = ~clk_a;
  initial while (kaynnissa) #18 clk_b = ~clk_b;

  always @(posedge clk_b) begin
    if (pulssi_b) pulsseja_b <= pulsseja_b + 1;
    if (saapui) begin
      saapuneita <= saapuneita + 1;
      summa_b    <= summa_b + int'(data_b);
    end
  end

  initial begin
    int summa_a = 0;
    #40 rst_n = 1'b1;
    @(posedge clk_a); #1;
    for (int i = 0; i < 10; i++) begin    // 10 pulssia 12 jakson välein
      pulssi_a = 1'b1;
      @(posedge clk_a); #1;
      pulssi_a = 1'b0;
      repeat (11) @(posedge clk_a);
      #1;
    end
    for (int i = 1; i <= 8; i++) begin    // 8 sanaa kättelyllä
      while (!vapaa) begin
        @(posedge clk_a); #1;
      end
      data_a  = 16'(1000 * i);
      summa_a += 1000 * i;
      laheta  = 1'b1;
      @(posedge clk_a); #1;
      laheta  = 1'b0;
    end
    repeat (40) @(posedge clk_a);
    #1;
    $display("pulsseja lähetetty 10, vastaanotettu %0d", pulsseja_b);
    $display("sanoja 8, saapui %0d, summa %0d / %0d", saapuneita,
             summa_b, summa_a);
    if (pulsseja_b != 10 || summa_b != summa_a) $fatal(1, "CDC väärin");
    kaynnissa = 1'b0;
  end
endmodule
