// GPIO: generoitu rekisterilohko ja sen ympärille käsin kirjoitettu
// logiikka (tulojen tahdistus ja nousevan reunan tunnistus).
module gpio
  import vaylat::*;
(
  input  logic       kello,
  input  logic       nollaus_n,
  input  apb_m2s_t   apb_m,
  output apb_s2m_t   apb_s,
  output logic [7:0] ulos,
  input  logic [7:0] sisaan,
  output logic       keskeytys
);

  // @alku kaytto
  logic [7:0] tahd1, tahd2, edellinen, salli, reunat;

  gpio_regs u_regs (
    .kello, .nollaus_n, .apb_m, .apb_s,
    .ulos_q     (ulos),
    .sisaan_d   (tahd2),
    .salli_q    (salli),
    .reunat_set (tahd2 & ~edellinen),     // nouseva reuna
    .reunat_q   (reunat)
  );

  assign keskeytys = |(reunat & salli);
  // @loppu kaytto

  // Ulkoiset tulot tahdistetaan kahdella kiikulla (ks. rtl-suunnittelu).
  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tahd1     <= '0;
      tahd2     <= '0;
      edellinen <= '0;
    end else begin
      tahd1     <= sisaan;
      tahd2     <= tahd1;
      edellinen <= tahd2;
    end
  end

endmodule
