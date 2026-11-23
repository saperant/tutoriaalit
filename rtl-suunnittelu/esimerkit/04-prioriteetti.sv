// @alku enkooderi
// Palauttaa korkeimman aktiivisen pyynnön indeksin.
module prioriteettienkooderi #(
  parameter int N = 8
) (
  input  logic [N-1:0]         pyynnot,
  output logic [$clog2(N)-1:0] indeksi,
  output logic                 kelvollinen
);
  always_comb begin
    indeksi     = '0;
    kelvollinen = 1'b0;
    // Silmukka puretaan synteesissä rinnakkaiseksi logiikaksi;
    // myöhempi (korkeampi) osuma ohittaa aiemman.
    for (int i = 0; i < N; i++) begin
      if (pyynnot[i]) begin
        indeksi     = i[$clog2(N)-1:0];
        kelvollinen = 1'b1;
      end
    end
  end
endmodule
// @loppu enkooderi

module testipenkki;
  logic [7:0] pyynnot;
  logic [2:0] indeksi;
  logic       kelvollinen;
  int         virheita = 0;

  prioriteettienkooderi #(.N(8)) dut (.pyynnot, .indeksi, .kelvollinen);

  // Viitemalli: suoraviivainen, eri tavalla kirjoitettu.
  function automatic int malli(logic [7:0] p);
    for (int i = 7; i >= 0; i--) if (p[i]) return i;
    return -1;
  endfunction

  initial begin
    for (int i = 0; i < 256; i++) begin
      pyynnot = 8'(i);
      #1;
      if (kelvollinen != (i != 0) ||
          (kelvollinen && int'(indeksi) != malli(pyynnot))) begin
        virheita++;
        $display("VIRHE: %b -> %0d", pyynnot, indeksi);
      end
    end
    $display("prioriteettienkooderi: 256 syötettä, %0d virhettä",
             virheita);
    if (virheita != 0) $fatal(1, "enkooderi toimii väärin");
  end
endmodule
