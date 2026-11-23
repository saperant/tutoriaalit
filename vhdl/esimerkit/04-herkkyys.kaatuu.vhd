-- Kolmen kanavan enemmistöäänestin (TMR). Herkkyyslistasta puuttuu c:
-- simulaattori ei herätä prosessia, kun vain c muuttuu, mutta synteesi
-- tekee silti oikean logiikan. Simulointi ja laitteisto eroavat.
library ieee;
use ieee.std_logic_1164.all;

entity aanestin is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity aanestin;

architecture rtl of aanestin is
begin
  -- @alku virhe
  process (a, b)                  -- VHDL-93-tyyli: c unohtui
  begin
    y <= (a and b) or (a and c) or (b and c);
  end process;
  -- Oikein: process (all)
  -- @loppu virhe
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal a, b, c, y : std_logic := '0';
begin
  dut : entity work.aanestin port map (a => a, b => b, c => c, y => y);

  testi : process
  begin
    a <= '1';
    wait for 1 ns;
    assert y = '0' severity failure;
    c <= '1';                     -- kaksi kolmesta: y:n pitää nousta
    wait for 1 ns;
    assert y = '1' report "äänestin ei reagoinut c:hen"
      severity failure;
    wait;
  end process testi;
end architecture sim;
