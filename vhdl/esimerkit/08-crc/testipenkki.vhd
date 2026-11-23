library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use work.crc_pkg.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;
  signal aloita  : std_logic := '1';
  signal kelpo   : std_logic := '0';
  signal tavu    : tavu_t := x"00";
  signal crc     : tavu_t;
  signal pituus  : unsigned(bitit(64 + 1) - 1 downto 0);
begin
  clk <= not clk after 5 ns when ajossa;

  dut : entity work.crc_laskin
    generic map (MAKSIMI => 64)
    port map (clk => clk, aloita => aloita, kelpo => kelpo, tavu => tavu,
              crc => crc, pituus => pituus);

  -- @alku testi
  testi : process
    variable rivi : line;
    procedure tarkista(viesti : string) is
    begin
      aloita <= '1';
      wait until rising_edge(clk);
      aloita <= '0';
      for i in viesti'range loop
        kelpo <= '1';
        tavu  <= tavu_t(to_unsigned(character'pos(viesti(i)), 8));
        wait until rising_edge(clk);
      end loop;
      kelpo <= '0';
      wait until rising_edge(clk);
      -- Laitteiston tulosta verrataan saman paketin malliin.
      assert crc = crc8(viesti)
        report "CRC poikkeaa mallista" severity failure;
      write(rivi, '"' & viesti & """: CRC " & to_hstring(crc)
                  & ", " & integer'image(to_integer(pituus)) & " tavua");
      writeline(output, rivi);
    end procedure tarkista;
  begin
    tarkista("123456789");                  -- standardin tarkistusarvo
    tarkista("VHDL-2008");
    assert crc8("123456789") = x"F4" severity failure;
    write(rivi, "pituuslaskurin leveys: " & integer'image(pituus'length));
    writeline(output, rivi);
    ajossa <= false;
    wait;
  end process testi;
  -- @loppu testi
end architecture sim;
