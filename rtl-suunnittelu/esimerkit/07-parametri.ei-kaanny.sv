// @alku tarkistus
// Baudijakaja tarkistaa parametrinsa käännösaikana: jos jakojäännös
// on suuri, UART-bitin ajoitus ryömii ja vastaanotin näytteistää
// väärästä kohdasta. Virhe kaatuu jo käännökseen, ei laboratorioon.
module baudijakaja #(
  parameter int KELLO_HZ = 50_000_000,
  parameter int BAUD     = 115_200
) (
  output int jakso
);
  localparam int JAKSO = KELLO_HZ / BAUD;
  localparam int VIRHE_PROMILLE =
      1000 * (KELLO_HZ - JAKSO * BAUD) / KELLO_HZ;

  if (JAKSO < 8) begin : g_liian_nopea
    $error("baudijakaja: %0d Hz on liian hidas %0d baudille",
           KELLO_HZ, BAUD);
  end
  if (VIRHE_PROMILLE > 20) begin : g_epatarkka
    $error("baudijakaja: ajoitusvirhe %0d promillea", VIRHE_PROMILLE);
  end

  assign jakso = JAKSO;
endmodule
// @loppu tarkistus

module testipenkki;
  int jakso_ok;
  int jakso_huono;                                              // @virhe
  baudijakaja #(.KELLO_HZ(50_000_000), .BAUD(115_200)) u_ok (
    .jakso(jakso_ok));
  baudijakaja #(.KELLO_HZ(1_000_000), .BAUD(115_200)) u_huono (  // @virhe
    .jakso(jakso_huono));                                         // @virhe
  initial begin
    #1 $display("50 MHz / 115200 baudia: %0d jaksoa bitille", jakso_ok);
    $display("1 MHz: %0d", jakso_huono);                         // @virhe
  end
endmodule
