-- @alku paketti
library ieee;
use ieee.numeric_std.all;

package pwm_pkg is
  -- VHDL-2008: taulukon alkio saa olla rajoittamaton. Leveys
  -- kiinnitetään vasta signaalin esittelyssä.
  type suhteet_t is array (natural range <>) of unsigned;
end package pwm_pkg;
-- @loppu paketti

-- @alku pwm
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.pwm_pkg.all;

-- Monikanavainen PWM: yhteinen laskuri, kanavakohtainen vertailija.
-- Kanavien määrä ja tarkkuus tulevat porttien leveyksistä.
entity pwm is
  port (
    clk     : in  std_logic;
    nollaa  : in  std_logic;
    suhteet : in  suhteet_t;                  -- pulssisuhde / kanava
    lahdot  : out std_logic_vector            -- yksi bitti / kanava
  );
end entity pwm;

architecture rtl of pwm is
  constant LEVEYS : positive := suhteet'element'length;
  signal laskuri  : unsigned(LEVEYS - 1 downto 0);
begin
  assert suhteet'length = lahdot'length
    report "kanavien määrä ei täsmää" severity failure;

  -- @alku laskenta
  laskenta : process (clk)
  begin
    if rising_edge(clk) then
      if nollaa = '1' then
        laskuri <= (others => '0');
      else
        laskuri <= laskuri + 1;
      end if;
    end if;
  end process laskenta;
  -- @loppu laskenta

  kanavat : for k in suhteet'range generate
    vertailu : process (clk)
    begin
      if rising_edge(clk) then
        if nollaa = '1' then
          lahdot(k) <= '0';
        elsif laskuri < suhteet(k) then
          lahdot(k) <= '1';
        else
          lahdot(k) <= '0';
        end if;
      end if;
    end process vertailu;
  end generate kanavat;
end architecture rtl;
-- @loppu pwm

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use work.pwm_pkg.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;
  signal nollaa  : std_logic := '1';
  signal suhteet : suhteet_t(0 to 3)(3 downto 0) :=
    (x"0", x"4", x"8", x"F");
  signal lahdot  : std_logic_vector(0 to 3);
begin
  clk <= not clk after 5 ns when ajossa;

  dut : entity work.pwm
    port map (clk => clk, nollaa => nollaa, suhteet => suhteet,
              lahdot => lahdot);

  -- Lasketaan jokaisen kanavan ykkösjaksot yhden PWM-jakson ajalta.
  testi : process
    type laskurit_t is array (0 to 3) of natural;
    variable ykkoset : laskurit_t := (others => 0);
    variable rivi    : line;
  begin
    wait until rising_edge(clk);
    nollaa <= '0';
    wait until rising_edge(clk);
    for jakso in 1 to 16 loop
      wait until rising_edge(clk);
      for k in 0 to 3 loop
        if lahdot(k) = '1' then
          ykkoset(k) := ykkoset(k) + 1;
        end if;
      end loop;
    end loop;
    for k in 0 to 3 loop
      write(rivi, "kanava " & integer'image(k) & ": suhde "
                  & integer'image(to_integer(suhteet(k))) & "/16, päällä "
                  & integer'image(ykkoset(k)) & "/16");
      writeline(output, rivi);
      assert ykkoset(k) = to_integer(suhteet(k)) severity failure;
    end loop;
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
