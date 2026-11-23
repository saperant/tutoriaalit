-- Väylän varaustila: kaksi lausetta ohjaa samaa signaalia. std_logic
-- on ratkaistu tyyppi, joten kaksi ajuria on sallittu, ja niiden
-- ristiriita näkyy vasta simuloinnissa arvona 'X'. Jos varattu olisi
-- std_ulogic, elaborointi hylkäisi mallin heti.
library ieee;
use ieee.std_logic_1164.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk     : std_logic := '0';
  signal pyynto  : std_logic := '0';
  signal vapauta : std_logic := '0';
  -- @alku ajurit
  signal varattu : std_logic := '0';
begin
  varaus : process (clk)
  begin
    if rising_edge(clk) then
      if pyynto = '1' then
        varattu <= '1';
      elsif vapauta = '1' then
        varattu <= '0';
      end if;
    end if;
  end process varaus;

  varattu <= '0' when vapauta = '1';     -- toinen ajuri
  -- @loppu ajurit

  testi : process
  begin
    pyynto <= '1';
    clk <= '1'; wait for 5 ns;
    clk <= '0'; wait for 5 ns;
    assert varattu = '1'
      report "varattu = " & to_string(varattu) severity failure;
    pyynto <= '0';
    vapauta <= '1';
    clk <= '1'; wait for 5 ns;
    clk <= '0'; wait for 5 ns;
    assert varattu = '0'
      report "varattu = " & to_string(varattu) severity failure;
    wait;
  end process testi;
end architecture sim;
