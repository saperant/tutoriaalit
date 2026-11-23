-- Väyläpyynnön kättely. Tilatyyppiin on lisätty uusi tila TAUKO,
-- mutta case-lauseen haaraa ei ole kirjoitettu. VHDL vaatii, että
-- case kattaa kaikki arvot, joten kääntäjä löytää unohtuneen haaran.
library ieee;
use ieee.std_logic_1164.all;

entity kattelu is
  port (
    clk, nollaa : in  std_logic;
    tarve       : in  std_logic;      -- siirrettävää on
    myonto      : in  std_logic;      -- väylä myönnetty
    pyynto      : out std_logic;
    siirto      : out std_logic
  );
end entity kattelu;

architecture rtl of kattelu is
  -- @alku tilat
  type tila_t is (
    VAPAA,
    PYYDETTY,
    SIIRTO_KAYNNISSA,
    TAUKO,                       -- @virhe: lisätty, ei käsitelty
    VALMIS
  );
  signal tila : tila_t := VAPAA;
  -- @loppu tilat
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if nollaa = '1' then
        tila <= VAPAA;
      else
        case tila is
          when VAPAA =>
            if tarve = '1' then
              tila <= PYYDETTY;
            end if;
          when PYYDETTY =>
            if myonto = '1' then
              tila <= SIIRTO_KAYNNISSA;
            end if;
          when SIIRTO_KAYNNISSA =>
            if tarve = '0' then
              tila <= VALMIS;
            end if;
          when VALMIS =>
            tila <= VAPAA;
        end case;
      end if;
    end if;
  end process;

  -- Mooren lähdöt riippuvat vain tilasta.
  pyynto <= '1' when tila = PYYDETTY else '0';
  siirto <= '1' when tila = SIIRTO_KAYNNISSA else '0';
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk    : std_logic := '0';
  signal ajossa : boolean := true;
  signal nollaa : std_logic := '1';
  signal tarve, myonto, pyynto, siirto : std_logic := '0';
begin
  clk <= not clk after 5 ns when ajossa;

  dut : entity work.kattelu
    port map (clk => clk, nollaa => nollaa, tarve => tarve,
              myonto => myonto, pyynto => pyynto, siirto => siirto);

  testi : process
    variable rivi : line;
  begin
    wait until rising_edge(clk);
    nollaa <= '0';
    for jakso in 1 to 6 loop
      myonto <= '1' when jakso = 3 else '0';
      tarve  <= '1' when jakso < 5 else '0';
      wait until rising_edge(clk);
      wait for 1 ns;
      write(rivi, "jakso " & integer'image(jakso) & ": pyyntö="
                  & to_string(pyynto) & " siirto=" & to_string(siirto));
      writeline(output, rivi);
    end loop;
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
