-- Hälytyksen pito: tapahtuma nostaa hälytyksen, joka pysyy päällä,
-- kunnes ohjain kuittaa sen. Tuloporttiin ei voi sijoittaa.
library ieee;
use ieee.std_logic_1164.all;

entity halytys is
  port (
    clk       : in  std_logic;
    tapahtuma : in  std_logic;
    kuittaus  : in  std_logic;
    paalla    : out std_logic := '0'
  );
end entity halytys;

architecture rtl of halytys is
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if tapahtuma = '1' then
        paalla <= '1';
      elsif kuittaus = '1' then
        paalla <= '0';
        kuittaus <= '0';   -- @virhe: tulo on vain luettavissa
      end if;
    end if;
  end process;
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk, tapahtuma, kuittaus, paalla : std_logic := '0';
begin
  dut : entity work.halytys
    port map (clk => clk, tapahtuma => tapahtuma, kuittaus => kuittaus,
              paalla => paalla);

  testi : process
    procedure jakso is
    begin
      clk <= '1'; wait for 5 ns;
      clk <= '0'; wait for 5 ns;
    end procedure;
    variable rivi : line;
  begin
    tapahtuma <= '1'; jakso; tapahtuma <= '0'; jakso; jakso;
    write(rivi, "tapahtuman jälkeen: " & to_string(paalla));
    writeline(output, rivi);
    kuittaus <= '1'; jakso; kuittaus <= '0'; jakso;
    write(rivi, "kuittauksen jälkeen: " & to_string(paalla));
    writeline(output, rivi);
    wait;
  end process testi;
end architecture sim;
