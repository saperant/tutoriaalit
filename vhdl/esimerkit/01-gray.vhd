-- @alku muunnin
-- Binääriluvun ja Gray-koodin muunnokset. Gray-koodissa peräkkäiset
-- arvot eroavat yhdellä bitillä, joten sitä käytetään esimerkiksi
-- kiertoanturien ja kellotusalueita ylittävien laskurien koodauksena.
library ieee;
use ieee.std_logic_1164.all;

entity gray_muunnin is
  generic (LEVEYS : positive := 4);
  port (
    binaari  : in  std_logic_vector(LEVEYS - 1 downto 0);
    gray     : out std_logic_vector(LEVEYS - 1 downto 0);
    takaisin : out std_logic_vector(LEVEYS - 1 downto 0)
  );
end entity gray_muunnin;

architecture rtl of gray_muunnin is
begin
  -- Binääri -> Gray: jokainen bitti XOR ylemmän naapurinsa kanssa.
  gray <= binaari xor ('0' & binaari(LEVEYS - 1 downto 1));

  -- Gray -> binääri: bitti on kaikkien ylempien Gray-bittien XOR.
  purku : process (all)
    variable b : std_logic_vector(LEVEYS - 1 downto 0);
  begin
    b(LEVEYS - 1) := gray(LEVEYS - 1);
    for i in LEVEYS - 2 downto 0 loop
      b(i) := b(i + 1) xor gray(i);
    end loop;
    takaisin <= b;
  end process purku;
end architecture rtl;
-- @loppu muunnin

-- @alku testipenkki
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant N : positive := 4;
  signal binaari, gray, takaisin : std_logic_vector(N - 1 downto 0);
begin
  dut : entity work.gray_muunnin
    generic map (LEVEYS => N)
    port map (binaari => binaari, gray => gray, takaisin => takaisin);

  testi : process
    variable rivi : line;
    variable edellinen : std_logic_vector(N - 1 downto 0);
    variable erot : natural;
  begin
    for arvo in 0 to 2**N - 1 loop
      binaari <= std_logic_vector(to_unsigned(arvo, N));
      wait for 1 ns;
      assert takaisin = binaari
        report "paluumuunnos väärin arvolla " & integer'image(arvo)
        severity failure;
      if arvo > 0 then
        erot := 0;
        for i in gray'range loop
          if gray(i) /= edellinen(i) then
            erot := erot + 1;
          end if;
        end loop;
        assert erot = 1 report "useampi bitti muuttui" severity failure;
      end if;
      edellinen := gray;
      if arvo < 6 then
        write(rivi, integer'image(arvo) & " -> " & to_string(gray));
        writeline(output, rivi);
      end if;
    end loop;
    write(rivi, string'("kaikki 16 arvoa tarkistettu"));
    writeline(output, rivi);
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
