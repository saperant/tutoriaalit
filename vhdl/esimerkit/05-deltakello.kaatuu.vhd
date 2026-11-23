-- Kahden kiikun viivelinja, jonka toinen kiikku käyttää kellon
-- "kopiota". Sijoitus clk_b <= clk viivästää kelloa yhden
-- deltasyklin, jolloin ensimmäisen kiikun uusi arvo ehtii toisen
-- kiikun syötteeksi ennen kuin sen kello nousee. Simulaatiossa
-- data ohittaa yhden vaiheen; laitteistossa viivelinja toimisi.
library ieee;
use ieee.std_logic_1164.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk    : std_logic := '0';
  signal ajossa : boolean := true;
  signal d, q1, q2 : std_logic := '0';
  -- @alku virhe
  signal clk_b : std_logic;
begin
  clk_b <= clk;                 -- "vain uudelleennimeäminen": +1 delta

  vaihe1 : process (clk)
  begin
    if rising_edge(clk) then
      q1 <= d;
    end if;
  end process;

  vaihe2 : process (clk_b)
  begin
    if rising_edge(clk_b) then
      q2 <= q1;                 -- q1 on jo päivittynyt
    end if;
  end process;
  -- @loppu virhe

  clk <= not clk after 5 ns when ajossa;

  testi : process
  begin
    d <= '1';
    wait until rising_edge(clk);
    wait for 1 ns;
    assert q1 = '1' severity failure;
    assert q2 = '0' report "q2 muuttui samalla reunalla kuin q1"
      severity failure;
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
