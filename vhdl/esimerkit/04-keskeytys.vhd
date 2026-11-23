-- @alku ohjain
-- Keskeytysohjaimen prioriteettikooderi: valitsee sallituista
-- pyynnöistä sen, jonka indeksi on pienin (korkein prioriteetti).
library ieee;
use ieee.std_logic_1164.all;

entity keskeytykset is
  generic (N : positive := 8);
  port (
    pyynnot  : in  std_logic_vector(N - 1 downto 0);
    maski    : in  std_logic_vector(N - 1 downto 0);  -- 1 = sallittu
    voimassa : out std_logic;
    numero   : out natural range 0 to N - 1   -- synteesi: 3 bittiä
  );
end entity keskeytykset;

architecture rtl of keskeytykset is
  signal aktiiviset : std_logic_vector(N - 1 downto 0);
begin
  -- Rinnakkainen sijoitus: kuvaa logiikan suoraan.
  aktiiviset <= pyynnot and maski;

  -- Prosessi: oletussijoitukset ensin, sitten ehdot. Silmukka
  -- käydään alhaalta ylös, joten pienin indeksi jää voimaan.
  kooderi : process (all)
  begin
    voimassa <= '0';
    numero   <= 0;
    for i in N - 1 downto 0 loop
      if aktiiviset(i) = '1' then
        voimassa <= '1';
        numero   <= i;
      end if;
    end loop;
  end process kooderi;
end architecture rtl;
-- @loppu ohjain

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal pyynnot, maski : std_logic_vector(7 downto 0) := x"00";
  signal voimassa : std_logic;
  signal numero   : natural range 0 to 7;
begin
  dut : entity work.keskeytykset
    port map (pyynnot => pyynnot, maski => maski,
              voimassa => voimassa, numero => numero);

  testi : process
    variable rivi : line;
    procedure kokeile(p, m : std_logic_vector(7 downto 0)) is
    begin
      pyynnot <= p;
      maski   <= m;
      wait for 1 ns;
      write(rivi, "pyynnöt " & to_string(p) & " maski " & to_string(m)
                  & " -> ");
      if voimassa = '1' then
        write(rivi, "IRQ " & integer'image(numero));
      else
        write(rivi, string'("ei keskeytystä"));
      end if;
      writeline(output, rivi);
    end procedure kokeile;
  begin
    kokeile("00000000", "11111111");
    kokeile("10010000", "11111111");
    kokeile("10010000", "11101111");
    kokeile("00000111", "11111110");
    kokeile("10000000", "01111111");
    wait;
  end process testi;
end architecture sim;
