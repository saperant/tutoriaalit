// Yksinkertaistettu PLIC-tyylinen keskeytysohjain.
//
// Lähteet 1..LAHTEET ovat tasoliipaistuja. Ohjelmisto lunastaa (claim)
// odottavan keskeytyksen lukemalla LUNASTA-rekisterin, joka palauttaa
// pienimmän numeron sallituista odottavista lähteistä (pienin numero =
// korkein prioriteetti). Lunastettu lähde peitetään, kunnes ohjelmisto
// kirjoittaa sen numeron takaisin (complete). Oikeassa PLICissä on
// lisäksi lähdekohtaiset prioriteetit ja kynnys kullekin kontekstille.
//   0x0 ODOTTAA (luku)   0x4 SALLI   0x8 LUNASTA / VALMIS
module plic
  import vaylat::*;
#(
  parameter int LAHTEET = 2
)(
  input  logic               kello,
  input  logic               nollaus_n,
  input  apb_m2s_t           apb_m,
  output apb_s2m_t           apb_s,
  input  logic [LAHTEET:1]   lahteet,
  output logic               ulkoinen_kesk
);

  logic [LAHTEET:1] salli, lunastettu, odottaa;
  logic [31:0]      paras;
  logic             kirjoita, lue;

  assign kirjoita = apb_m.psel && apb_m.penable && apb_m.pwrite;
  assign lue      = apb_m.psel && apb_m.penable && !apb_m.pwrite;

  // @alku lunastus
  assign odottaa = lahteet & ~lunastettu;
  always_comb begin
    paras = 32'd0;                             // 0 = ei keskeytystä
    for (int i = LAHTEET; i >= 1; i--)
      if (odottaa[i] && salli[i]) paras = 32'(i);
  end
  assign ulkoinen_kesk = (paras != 32'd0);
  // @loppu lunastus

  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    // Rekisterit ovat sanoja: osittainen kirjoitus on virhe.
    apb_s.pslverr = apb_m.psel && apb_m.penable && apb_m.pwrite &&
                    apb_m.pstrb != 4'b1111;
    case (apb_m.paddr)
      12'h000: apb_s.prdata = 32'(odottaa);
      12'h004: apb_s.prdata = 32'(salli);
      12'h008: apb_s.prdata = paras;
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      salli      <= '0;
      lunastettu <= '0;
    end else begin
      if (kirjoita && apb_m.paddr == 12'h004)
        salli <= apb_m.pwdata[LAHTEET:1];
      if (lue && apb_m.paddr == 12'h008 && paras != 32'd0)
        lunastettu[paras[$clog2(LAHTEET+1)-1:0]] <= 1'b1;
      if (kirjoita && apb_m.paddr == 12'h008)
        for (int i = 1; i <= LAHTEET; i++)
          if (apb_m.pwdata == 32'(i)) lunastettu[i] <= 1'b0;
    end
  end

endmodule
