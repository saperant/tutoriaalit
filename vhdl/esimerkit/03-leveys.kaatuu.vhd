-- Summain, jonka tulos on bitin leveämpi kuin syötteet. numeric_std:n
-- summa on yhtä leveä kuin leveämpi operandi, joten kantobitti ei
-- synny itsestään, ja leveyksien ero havaitaan vasta simuloinnissa.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity summain is
  port (
    a, b  : in  unsigned(7 downto 0);
    summa : out unsigned(8 downto 0)
  );
end entity summain;

architecture rtl of summain is
begin
  -- @alku summa
  summa <= a + b;                 -- 8 bittiä 9-bittiseen: virhe
  -- Oikein: summa <= resize(a, 9) + b;
  -- @loppu summa
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal a, b  : unsigned(7 downto 0) := x"00";
  signal summa : unsigned(8 downto 0);
begin
  dut : entity work.summain port map (a => a, b => b, summa => summa);

  testi : process
  begin
    a <= x"C8"; b <= x"64";       -- 200 + 100 = 300
    wait for 1 ns;
    assert to_integer(summa) = 300 severity failure;
    wait;
  end process testi;
end architecture sim;
