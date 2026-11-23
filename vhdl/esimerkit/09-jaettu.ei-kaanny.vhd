-- Kaksi tarkistinprosessia kirjaa virheet yhteiseen laskuriin.
-- VHDL-2008 sallii jaetun muuttujan vain suojattua tyyppiä.
library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  -- @alku laskuri
  type laskuri_t is protected
    procedure kasvata;
    impure function arvo return natural;
  end protected laskuri_t;

  type laskuri_t is protected body
    variable n : natural := 0;
    procedure kasvata is
    begin
      n := n + 1;
    end procedure kasvata;
    impure function arvo return natural is
    begin
      return n;
    end function arvo;
  end protected body laskuri_t;

  shared variable virheet : natural := 0;  -- @virhe: ei suojattu
  shared variable virheet : laskuri_t;
  -- @loppu laskuri
  signal pariteetti_ok, pituus_ok : std_logic := '1';
begin
  -- Kaksi virhetilannetta eri hetkinä.
  pariteetti_ok <= '0' after 10 ns, '1' after 20 ns;
  pituus_ok     <= '0' after 30 ns;

  pariteetti : process (pariteetti_ok)
  begin
    if pariteetti_ok = '0' then
      virheet.kasvata;
    end if;
  end process pariteetti;

  pituus : process (pituus_ok)
  begin
    if pituus_ok = '0' then
      virheet.kasvata;
    end if;
  end process pituus;

  raportti : process
    variable rivi : line;
  begin
    wait for 50 ns;
    write(rivi, "virheitä: " & integer'image(virheet.arvo));
    writeline(output, rivi);
    wait;
  end process raportti;
end architecture sim;
