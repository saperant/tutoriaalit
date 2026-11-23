-- @alku viive
-- Viivelinja, jonka alkiotyyppi on geneerinen (VHDL-2008). Samaa
-- entiteettiä voi käyttää bittivektoreille, kokonaisluvuille ja
-- tietueille. N = 0 tuottaa suoran johdon.
library ieee;
use ieee.std_logic_1164.all;

entity viive is
  generic (
    type alkio_t;                       -- geneerinen tyyppi
    N    : natural;                     -- viive kellojaksoina
    LEPO : alkio_t                      -- arvo nollauksen jälkeen
  );
  port (
    clk    : in  std_logic;
    nollaa : in  std_logic;
    sisaan : in  alkio_t;
    ulos   : out alkio_t
  );
end entity viive;

architecture rtl of viive is
  type linja_t is array (0 to N - 1) of alkio_t;
begin
  suora : if N = 0 generate
    ulos <= sisaan;
  else generate
    signal linja : linja_t;
  begin
    process (clk)
    begin
      if rising_edge(clk) then
        if nollaa = '1' then
          linja <= (others => LEPO);
        else
          linja <= sisaan & linja(0 to N - 2);
        end if;
      end if;
    end process;
    ulos <= linja(N - 1);
  end generate suora;
end architecture rtl;
-- @loppu viive

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

-- @alku testipenkki
architecture sim of testipenkki is
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;
  signal nollaa  : std_logic := '1';
  signal tavu_s, tavu_u : std_logic_vector(7 downto 0) := x"00";
  signal luku_s, luku_u : integer := 0;
  signal luku_suora     : integer;
begin
  clk <= not clk after 5 ns when ajossa;

  tavut : entity work.viive
    generic map (alkio_t => std_logic_vector(7 downto 0), N => 3,
                 LEPO => x"00")
    port map (clk => clk, nollaa => nollaa, sisaan => tavu_s,
              ulos => tavu_u);

  luvut : entity work.viive
    generic map (alkio_t => integer, N => 1, LEPO => -1)
    port map (clk => clk, nollaa => nollaa, sisaan => luku_s,
              ulos => luku_u);

  suora : entity work.viive
    generic map (alkio_t => integer, N => 0, LEPO => 0)
    port map (clk => clk, nollaa => nollaa, sisaan => luku_s,
              ulos => luku_suora);

  testi : process
    variable rivi : line;
  begin
    wait until rising_edge(clk);
    nollaa <= '0';
    for i in 1 to 5 loop
      tavu_s <= x"A" & std_logic_vector(to_unsigned(i, 4));
      luku_s <= i * 10;
      wait until rising_edge(clk);
      wait for 1 ns;
      write(rivi, "jakso " & integer'image(i) & ": tavu "
                  & to_hstring(tavu_u) & ", luku " & integer'image(luku_u)
                  & ", suora " & integer'image(luku_suora));
      writeline(output, rivi);
    end loop;
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
