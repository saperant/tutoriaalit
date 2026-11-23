-- Osoitedekooderi, josta puuttuu oletussijoitus. Kun osoite ei osu
-- mihinkään alueeseen, valintasignaalit pitävät vanhan arvonsa:
-- synteesi tekee niistä salpoja, ja simulointi näyttää saman.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity dekooderi is
  port (
    osoite  : in  unsigned(15 downto 0);
    cs_ram  : out std_logic;
    cs_uart : out std_logic
  );
end entity dekooderi;

architecture rtl of dekooderi is
begin
  -- @alku virhe
  process (all)
  begin
    if osoite < x"8000" then                   -- 0000–7FFF: RAM
      cs_ram  <= '1';
      cs_uart <= '0';
    elsif osoite(15 downto 4) = x"C00" then    -- C000–C00F: UART
      cs_ram  <= '0';
      cs_uart <= '1';
    end if;               -- muut osoitteet: ei sijoitusta -> salpa
  end process;
  -- @loppu virhe
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal osoite          : unsigned(15 downto 0) := x"0000";
  signal cs_ram, cs_uart : std_logic;
begin
  dut : entity work.dekooderi
    port map (osoite => osoite, cs_ram => cs_ram, cs_uart => cs_uart);

  testi : process
  begin
    osoite <= x"1234";
    wait for 1 ns;
    assert cs_ram = '1' severity failure;
    osoite <= x"F000";                          -- ei kenenkään aluetta
    wait for 1 ns;
    assert cs_ram = '0' and cs_uart = '0'
      report "valinta jäi päälle osoitteessa F000" severity failure;
    wait;
  end process testi;
end architecture sim;
