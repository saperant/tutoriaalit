`line 1 "12-muller.sv" 0
// (`line kiinnittää tiedostonimen, jonka Verilator tulostaa $finishissä.)
// Asynkroninen piiri: Mullerin C-elementti ja kolmivaiheinen
// Muller-liukuhihna, joka siirtää dataa nelivaiheisella kättelyllä
// ilman kelloa (bundled data: data on vakaa ennen pyyntöä).

// @alku c-elementti
// Lähtö seuraa tuloja, kun ne ovat samat, ja muuten pitää arvonsa.
module c_elementti (input logic a, b, output logic c);
  initial c = 1'b0;
  always @(a or b) if (a == b) c <= #1 a;
endmodule
// @loppu c-elementti

// @alku liukuhihna
// Vaihe i: c[i] = C(c[i-1], !c[i+1]). c[i] on samalla vaiheen i
// pyyntö eteenpäin ja kuittaus taaksepäin; salpa ottaa datan, kun
// c[i] nousee.
module liukuhihna (input  logic       pyynto, kuittaus_ulos,
                   input  logic [7:0] data_sisaan,
                   output logic       kuittaus, pyynto_ulos,
                   output logic [7:0] data_ulos);
  logic [2:0] c;
  logic [7:0] salpa0, salpa1, salpa2;
  c_elementti v0 (.a(pyynto), .b(~c[1]),        .c(c[0]));
  c_elementti v1 (.a(c[0]),   .b(~c[2]),        .c(c[1]));
  c_elementti v2 (.a(c[1]),   .b(~kuittaus_ulos), .c(c[2]));
  always @(posedge c[0]) salpa0 <= data_sisaan;
  always @(posedge c[1]) salpa1 <= salpa0;
  always @(posedge c[2]) salpa2 <= salpa1;
  assign kuittaus = c[0];
  // Viive-elementti (matched delay): pyyntö lähtee vasta, kun salpa
  // on ehtinyt ottaa datan – bundled data -oletus.
  assign #1 pyynto_ulos = c[2];
  assign data_ulos = salpa2;
endmodule
// @loppu liukuhihna

// @alku testipenkki
module testipenkki;
  logic       pyynto = 1'b0, kuittaus, pyynto_ulos, kuittaus_ulos = 1'b0;
  logic [7:0] data = 8'h00, data_ulos;
  liukuhihna u (.pyynto, .kuittaus_ulos, .data_sisaan(data), .kuittaus,
                .pyynto_ulos, .data_ulos);

  initial begin                    // tuottaja: nelivaiheinen kättely
    for (int i = 1; i <= 3; i++) begin
      data = 8'(i * 17);           // data ensin, sitten pyyntö
      #1 pyynto = 1'b1;
      wait (kuittaus == 1'b1);
      #1 pyynto = 1'b0;
      wait (kuittaus == 1'b0);
    end
  end

  initial begin                    // kuluttaja: hidas, 10 aikayksikköä
    for (int i = 1; i <= 3; i++) begin
      wait (pyynto_ulos == 1'b1);
      $display("%3t: vastaanotettu %0d", $time, data_ulos);
      #10 kuittaus_ulos = 1'b1;
      wait (pyynto_ulos == 1'b0);
      #1 kuittaus_ulos = 1'b0;
    end
    $finish;
  end
endmodule
// @loppu testipenkki
