-- @alku kooderi
-- Kvadratuurikooderin (kiertoanturin) dekooderi. Kanavat A ja B
-- tulevat piirin ulkopuolelta, joten ne tahdistetaan kahdella
-- kiikulla ennen käyttöä. Jokainen tilamuutos siirtää asentoa yhdellä
-- askeleella; suunta riippuu siitä, kumpi kanava muuttui.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity kvadratuuri is
  port (
    clk    : in  std_logic;
    nollaa : in  std_logic;                 -- synkroninen nollaus
    a, b   : in  std_logic;
    asento : out signed(15 downto 0)
  );
end entity kvadratuuri;

architecture rtl of kvadratuuri is
  signal a_tahd, b_tahd : std_logic_vector(1 downto 0);
  signal ab_ed          : std_logic_vector(1 downto 0);
  signal laskuri        : signed(15 downto 0);
begin
  process (clk)
    variable ab : std_logic_vector(1 downto 0);
  begin
    if rising_edge(clk) then
      -- Tahdistus: kaksi kiikkua peräkkäin (ks. RTL-suunnittelu, CDC).
      a_tahd <= a_tahd(0) & a;
      b_tahd <= b_tahd(0) & b;

      ab    := a_tahd(1) & b_tahd(1);
      ab_ed <= ab;

      if nollaa = '1' then
        laskuri <= (others => '0');
      else
        -- Gray-järjestys 00 -> 10 -> 11 -> 01 -> 00 on myötäpäivään.
        case std_logic_vector'(ab_ed & ab) is
          when "0010" | "1011" | "1101" | "0100" =>
            laskuri <= laskuri + 1;
          when "0001" | "0111" | "1110" | "1000" =>
            laskuri <= laskuri - 1;
          when others =>
            null;                           -- ei muutosta tai virhe
        end case;
      end if;
    end if;
  end process;

  asento <= laskuri;
end architecture rtl;
-- @loppu kooderi

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

-- @alku testipenkki
architecture sim of testipenkki is
  constant JAKSO : time := 10 ns;
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;
  signal nollaa  : std_logic := '1';
  signal a, b    : std_logic := '0';
  signal asento  : signed(15 downto 0);
begin
  -- Kello pysähtyy, kun ajossa = false; simulaatio loppuu itsestään.
  clk <= not clk after JAKSO / 2 when ajossa;

  dut : entity work.kvadratuuri
    port map (clk => clk, nollaa => nollaa, a => a, b => b,
              asento => asento);

  testi : process
    variable rivi : line;
    -- Yksi askel: kanavien tila muuttuu, sitten odotetaan 4 jaksoa.
    procedure askel(uusi_a, uusi_b : std_logic) is
    begin
      a <= uusi_a;
      b <= uusi_b;
      wait for 4 * JAKSO;
    end procedure askel;
    procedure tulosta(otsikko : string) is
    begin
      write(rivi, otsikko & ": " & integer'image(to_integer(asento)));
      writeline(output, rivi);
    end procedure tulosta;
  begin
    wait for 3 * JAKSO;
    nollaa <= '0';
    for kierros in 1 to 3 loop              -- 3 täyttä jaksoa eteen
      askel('1', '0'); askel('1', '1'); askel('0', '1'); askel('0', '0');
    end loop;
    tulosta("eteen 12 askelta");
    askel('0', '1'); askel('1', '1');       -- 2 askelta taakse
    tulosta("taakse 2 askelta");
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
