-- @alku esittely
-- CRC-8-laskennan yhteiset määrittelyt (polynomi x^8 + x^2 + x + 1,
-- alkuarvo 0, ei käännöksiä; tunnetaan nimellä CRC-8/SMBUS).
library ieee;
use ieee.std_logic_1164.all;

package crc_pkg is
  subtype tavu_t is std_logic_vector(7 downto 0);
  type tavut_t is array (natural range <>) of tavu_t;

  constant POLYNOMI : tavu_t := x"07";
  constant ALKUARVO : tavu_t := x"00";

  -- Yhden tavun askel: synteesikelpoinen, puhdas funktio.
  function crc8(crc : tavu_t; tavu : tavu_t) return tavu_t;

  -- Kokonaisen viestin CRC (ylikuormitus): mallina testipenkeille.
  function crc8(viesti : tavut_t) return tavu_t;
  function crc8(viesti : string) return tavu_t;

  -- Bittien määrä, joka tarvitaan arvoille 0 .. n - 1.
  function bitit(n : positive) return natural;
end package crc_pkg;
-- @loppu esittely

-- @alku runko
library ieee;
use ieee.numeric_std.all;

package body crc_pkg is
  function crc8(crc : tavu_t; tavu : tavu_t) return tavu_t is
    variable r : tavu_t := crc xor tavu;
  begin
    for i in 1 to 8 loop                -- silmukka aukeaa logiikaksi
      if r(7) = '1' then
        r := (r(6 downto 0) & '0') xor POLYNOMI;
      else
        r := r(6 downto 0) & '0';
      end if;
    end loop;
    return r;
  end function crc8;

  function crc8(viesti : tavut_t) return tavu_t is
    variable crc : tavu_t := ALKUARVO;
  begin
    for i in viesti'range loop
      crc := crc8(crc, viesti(i));
    end loop;
    return crc;
  end function crc8;

  function crc8(viesti : string) return tavu_t is
    variable tavut : tavut_t(viesti'range);
  begin
    for i in viesti'range loop
      tavut(i) := tavu_t(to_unsigned(character'pos(viesti(i)), 8));
    end loop;
    return crc8(tavut);
  end function crc8;

  function bitit(n : positive) return natural is
    variable tulos : natural := 0;
  begin
    while 2**tulos < n loop
      tulos := tulos + 1;
    end loop;
    return tulos;
  end function bitit;
end package body crc_pkg;
-- @loppu runko
