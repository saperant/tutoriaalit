-- Lämpötila-anturin raaka-arvo (0,25 °C / LSB, nollakohta -40 °C)
-- celsiusasteiksi. Funktiot ovat oletuksena puhtaita (pure): tulos
-- riippuu vain parametreista, joten funktio ei saa lukea signaalia.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity anturi is
  port (
    raaka     : in  unsigned(9 downto 0);
    siirto    : in  integer range -8 to 7;   -- kalibrointi
    lampotila : out integer range -48 to 223
  );
end entity anturi;

architecture rtl of anturi is
  -- @alku funktio
  function celsius(r : unsigned) return integer is
  begin
    return to_integer(r) / 4 - 40 + siirto;  -- @virhe: lukee signaalia
    return to_integer(r) / 4 - 40;
  end function celsius;
  -- @loppu funktio
begin
  lampotila <= celsius(raaka) + siirto;
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal raaka     : unsigned(9 downto 0) := (others => '0');
  signal siirto    : integer range -8 to 7 := 0;
  signal lampotila : integer range -48 to 223;
begin
  dut : entity work.anturi
    port map (raaka => raaka, siirto => siirto, lampotila => lampotila);

  testi : process
    variable rivi : line;
  begin
    raaka  <= to_unsigned(260, 10);         -- 260 / 4 - 40 = 25 °C
    siirto <= -2;
    wait for 1 ns;
    write(rivi, "lämpötila: " & integer'image(lampotila) & " °C");
    writeline(output, rivi);
    wait;
  end process testi;
end architecture sim;
