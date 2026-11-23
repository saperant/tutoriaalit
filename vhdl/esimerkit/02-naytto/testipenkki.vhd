library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

-- @alku testipenkki
architecture sim of testipenkki is
  signal kymmenet, ykkoset : std_logic_vector(3 downto 0);
  signal vasen, oikea      : std_logic_vector(6 downto 0);
  signal vasen_k, oikea_k  : std_logic_vector(6 downto 0);

  -- Odotetut kuviot numeroille 0–9 samassa bittijärjestyksessä.
  type kuviot_t is array (0 to 9) of std_logic_vector(6 downto 0);
  constant KUVIOT : kuviot_t := (
    "0111111", "0000110", "1011011", "1001111", "1100110",
    "1101101", "1111101", "0000111", "1111111", "1101111");
begin
  -- Arkkitehtuuri valitaan suluissa; ilman sitä käytetään viimeksi
  -- analysoitua.
  dut : entity work.naytto(rakenne)
    port map (kymmenet => kymmenet, ykkoset => ykkoset,
              vasen => vasen, oikea => oikea);

  vanha : entity work.naytto(komponentit)
    port map (kymmenet => kymmenet, ykkoset => ykkoset,
              vasen => vasen_k, oikea => oikea_k);

  testi : process
    variable rivi : line;
  begin
    for luku in 0 to 99 loop
      kymmenet <= std_logic_vector(to_unsigned(luku / 10, 4));
      ykkoset  <= std_logic_vector(to_unsigned(luku mod 10, 4));
      wait for 1 ns;
      assert vasen_k = vasen and oikea_k = oikea
        report "arkkitehtuurit eroavat" severity failure;
      assert oikea = KUVIOT(luku mod 10)
        report "ykköset väärin: " & integer'image(luku) severity failure;
      if luku < 10 then
        assert vasen = "0000000" report "etunolla näkyy" severity failure;
      else
        assert vasen = KUVIOT(luku / 10)
          report "kymmenet väärin" severity failure;
      end if;
    end loop;

    for luku in 7 to 12 loop
      kymmenet <= std_logic_vector(to_unsigned(luku / 10, 4));
      ykkoset  <= std_logic_vector(to_unsigned(luku mod 10, 4));
      wait for 1 ns;
      write(rivi, integer'image(luku) & ": " & to_hstring(vasen)
                  & " " & to_hstring(oikea));
      writeline(output, rivi);
    end loop;

    ykkoset <= "1100";                    -- kelvoton BCD-numero
    wait for 1 ns;
    write(rivi, "kelvoton: " & to_string(oikea));
    writeline(output, rivi);
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
