// Puutteellinen herkkyyslista: simulaattori laskee y:n uudelleen vain,
// kun a muuttuu, mutta synteesi tekee tavallisen JA-portin.
// @alku epasuhta
module epasuhta (input wire a, b, output reg y);
  always @(a)          // b puuttuu herkkyyslistasta
    y = a & b;
endmodule
// @loppu epasuhta
