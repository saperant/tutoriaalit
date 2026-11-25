// RAM: AXI4-orja, joka tukee INCR-purskeita (32-bittinen data).
//
// Yksi osoitekättely aloittaa purskeen, jossa on AxLEN + 1 datasiirtoa.
// Orja laskee osoitteen itse: jokainen siirto kasvattaa sanaindeksiä.
// Tunnisteita (AxID) ja muita purskelajeja (WRAP, FIXED) ei ole. Lohko
// ei kuulu Pikku-SoC:hen, jonka kytkin on AXI4-Lite; sitä ajetaan omassa
// testipenkissään (tb/tb_purske.sv).
module ram_purske #(
  parameter int SANAT = 2048           // 8 KiB: kaksi 4 KiB:n sivua
)(
  input  logic        kello,
  input  logic        nollaus_n,
  /* verilator lint_off UNUSEDSIGNAL */
  input  logic [31:0] araddr,
  input  logic [31:0] awaddr,
  input  logic        wlast,           // tarkistin valvoo, orja laskee itse
  /* verilator lint_on UNUSEDSIGNAL */
  input  logic [7:0]  arlen,
  input  logic        arvalid,
  output logic        arready,
  output logic [31:0] rdata,
  output logic        rlast,
  output logic        rvalid,
  input  logic        rready,
  input  logic [7:0]  awlen,
  input  logic        awvalid,
  output logic        awready,
  input  logic [31:0] wdata,
  input  logic        wvalid,
  output logic        wready,
  output logic        bvalid,
  input  logic        bready
);

  localparam int AB = $clog2(SANAT);
  logic [31:0]   muisti [SANAT];
  logic [AB-1:0] r_ind, w_ind;
  logic [7:0]    r_jaljella, w_jaljella;
  logic          r_kaynnissa, w_kaynnissa;

  // @alku purske
  assign arready = !r_kaynnissa;
  assign rvalid  = r_kaynnissa;
  assign rdata   = muisti[r_ind];
  assign rlast   = r_kaynnissa && (r_jaljella == 8'd0);
  assign awready = !w_kaynnissa && !bvalid;
  assign wready  = w_kaynnissa;

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      r_kaynnissa <= 1'b0;
      w_kaynnissa <= 1'b0;
      bvalid      <= 1'b0;
      r_ind       <= '0;
      w_ind       <= '0;
      r_jaljella  <= 8'd0;
      w_jaljella  <= 8'd0;
    end else begin
      if (arvalid && arready) begin          // osoite: purske alkaa
        r_kaynnissa <= 1'b1;
        r_ind       <= araddr[AB+1:2];
        r_jaljella  <= arlen;
      end else if (rvalid && rready) begin   // datasiirto: seuraava sana
        r_ind      <= r_ind + 1'b1;
        r_jaljella <= r_jaljella - 8'd1;
        if (r_jaljella == 8'd0) r_kaynnissa <= 1'b0;
      end
      if (awvalid && awready) begin
        w_kaynnissa <= 1'b1;
        w_ind       <= awaddr[AB+1:2];
        w_jaljella  <= awlen;
      end else if (wvalid && wready) begin
        w_ind      <= w_ind + 1'b1;
        w_jaljella <= w_jaljella - 8'd1;
        if (w_jaljella == 8'd0) begin        // viimeinen: yksi vastaus
          w_kaynnissa <= 1'b0;
          bvalid      <= 1'b1;
        end
      end
      if (bvalid && bready) bvalid <= 1'b0;
    end
  end
  // @loppu purske

  always_ff @(posedge kello)
    if (wvalid && wready) muisti[w_ind] <= wdata;

endmodule
