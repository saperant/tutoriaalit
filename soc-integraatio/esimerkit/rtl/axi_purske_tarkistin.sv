// Purskeiden protokollatarkistin (vain simulaatio). Valvoo kahta
// sääntöä, joita AXI4-Litessä ei ole:
//   1. purske ei saa ylittää 4 KiB:n rajaa
//   2. xLAST on ylhäällä täsmälleen purskeen viimeisessä datasiirrossa
// Rikkomus tulostetaan; testipenkki laskee ne.
module axi_purske_tarkistin (
  input logic        kello,
  input logic        nollaus_n,
  /* verilator lint_off UNUSEDSIGNAL */
  input logic [31:0] araddr, awaddr,
  /* verilator lint_on UNUSEDSIGNAL */
  input logic [7:0]  arlen,
  input logic        arvalid, arready,
  input logic        rlast, rvalid, rready,
  input logic [7:0]  awlen,
  input logic        awvalid, awready,
  input logic        wlast, wvalid, wready
);

  int rikkomuksia = 0;
  logic [7:0] r_pituus, r_nro, w_pituus, w_nro;

  // @alku saannot
  // Purskeen viimeinen tavu: alkuosoite + siirtoja * 4 - 1. Sen on oltava
  // samalla 4 KiB:n sivulla kuin ensimmäisen.
  function automatic logic ylittaa(input logic [11:0] siirtyma,
                                   input logic [7:0]  len);
    return ({1'b0, siirtyma} + {3'd0, len, 2'b11}) > 13'd4095;
  endfunction

  // Laskuri on simulaation kirjanpitoa, ei piirin tilaa: se kasvaa
  // heti, vaikka samalla jaksolla olisi kaksi rikkomusta.
  /* verilator lint_off BLKSEQ */
  task automatic rikkomus(input string viesti);
    rikkomuksia++;
    $display("tarkistin: %s", viesti);
  endtask
  /* verilator lint_on BLKSEQ */

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      r_pituus <= 8'd0;
      r_nro    <= 8'd0;
      w_pituus <= 8'd0;
      w_nro    <= 8'd0;
    end else begin
      if (arvalid && arready) begin
        r_pituus <= arlen;
        r_nro    <= 8'd0;
        if (ylittaa(araddr[11:0], arlen))
          rikkomus($sformatf(
            "lukupurske 0x%h, %0d siirtoa ylittää 4 KiB:n rajan",
            araddr[15:0], int'(arlen) + 1));
      end
      if (awvalid && awready) begin
        w_pituus <= awlen;
        w_nro    <= 8'd0;
        if (ylittaa(awaddr[11:0], awlen))
          rikkomus($sformatf(
            "kirjoituspurske 0x%h, %0d siirtoa ylittää 4 KiB:n rajan",
            awaddr[15:0], int'(awlen) + 1));
      end
      if (rvalid && rready) begin
        r_nro <= r_nro + 8'd1;
        if (rlast != (r_nro == r_pituus))
          rikkomus($sformatf("RLAST väärin siirrossa %0d/%0d",
                             int'(r_nro) + 1, int'(r_pituus) + 1));
      end
      if (wvalid && wready) begin
        w_nro <= w_nro + 8'd1;
        if (wlast != (w_nro == w_pituus))
          rikkomus($sformatf("WLAST väärin siirrossa %0d/%0d",
                             int'(w_nro) + 1, int'(w_pituus) + 1));
      end
    end
  end
  // @loppu saannot

endmodule
