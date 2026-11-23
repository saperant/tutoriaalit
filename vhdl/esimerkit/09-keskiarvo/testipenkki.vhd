-- @alku alku
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use std.textio.all;
use std.env.finish;
use work.jono_pkg.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant JAKSO     : time := 10 ns;
  constant NAYTTEITA : positive := 500;
  signal clk       : std_logic := '0';
  signal nollaa    : std_logic := '1';
  signal sisaan_kelpo, ulos_kelpo : std_logic := '0';
  signal sisaan, ulos : signed(11 downto 0) := (others => '0');

  shared variable odotetut : jono_t;    -- malli -> tarkistin
  signal tarkistettu : natural := 0;
begin
  clk <= not clk after JAKSO / 2;       -- finish lopettaa simuloinnin

  dut : entity work.keskiarvo
    port map (clk => clk, nollaa => nollaa, sisaan_kelpo => sisaan_kelpo,
              sisaan => sisaan, ulos_kelpo => ulos_kelpo, ulos => ulos);
-- @loppu alku

  -- @alku heratteet
  -- Herätteet ja malli: satunnaiset näytteet, satunnaiset tauot.
  heratteet : process
    variable s1, s2   : positive := 42;   -- toistettava siemen
    variable x        : real;
    variable ikkuna   : integer_vector(0 to 3) := (others => 0);
    variable nayte    : integer;
  begin
    wait for 3 * JAKSO;
    wait until rising_edge(clk);
    nollaa <= '0';
    for i in 1 to NAYTTEITA loop
      uniform(s1, s2, x);
      nayte := integer(floor(x * 4096.0)) - 2048;   -- -2048 .. 2047
      ikkuna := nayte & ikkuna(0 to 2);
      -- Malli: kokonaislukujen jako pyöristää kohti nollaa, laitteisto
      -- alaspäin. Siksi malli käyttää floor-jakoa.
      odotetut.lisaa(integer(floor(real(ikkuna(0) + ikkuna(1)
                                        + ikkuna(2) + ikkuna(3)) / 4.0)));
      sisaan       <= to_signed(nayte, 12);
      sisaan_kelpo <= '1';
      wait until rising_edge(clk);
      uniform(s1, s2, x);
      if x < 0.3 then                     -- 30 %:n todennäköisyydellä
        sisaan_kelpo <= '0';              -- yhden jakson tauko
        wait until rising_edge(clk);
      end if;
    end loop;
    sisaan_kelpo <= '0';
    wait;
  end process heratteet;
  -- @loppu heratteet

  -- @alku tarkistin
  tarkistin : process (clk)
    variable odotettu : integer;
  begin
    if rising_edge(clk) and ulos_kelpo = '1' then
      odotettu := odotetut.ota;
      assert to_integer(ulos) = odotettu
        report "näyte " & integer'image(tarkistettu + 1) & ": saatiin "
               & integer'image(to_integer(ulos)) & ", odotettiin "
               & integer'image(odotettu)
        severity failure;
      tarkistettu <= tarkistettu + 1;
    end if;
  end process tarkistin;

  -- Valvoja: kaikki näytteet tarkistettu tai aikaraja ylittyy.
  valvoja : process
    variable rivi : line;
  begin
    wait until tarkistettu = NAYTTEITA for 20 us;
    assert tarkistettu = NAYTTEITA
      report "aikakatkaisu: tarkistettu vain "
             & integer'image(tarkistettu) severity failure;
    assert odotetut.koko = 0 report "odotettuja jäi" severity failure;
    write(rivi, "OK: " & integer'image(tarkistettu)
                & " näytettä tarkistettu");
    writeline(output, rivi);
    finish;
  end process valvoja;
  -- @loppu tarkistin
end architecture sim;
