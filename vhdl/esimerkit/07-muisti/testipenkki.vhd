library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant JAKSO : time := 10 ns;
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;

  signal ram_kirj           : std_logic := '0';
  signal ram_kos, ram_los   : natural range 0 to 15 := 0;
  signal ram_kdata, ram_ldata : std_logic_vector(7 downto 0) := x"00";
  signal rom_osoite         : natural range 0 to 15 := 0;
  signal rom_arvo           : unsigned(7 downto 0);

  signal nollaa        : std_logic := '1';
  signal kirjoita, lue : std_logic := '0';
  signal taynna, tyhja : std_logic;
  signal k_data, l_data : std_logic_vector(7 downto 0) := x"00";
begin
  clk <= not clk after JAKSO / 2 when ajossa;

  u_ram : entity work.ram
    generic map (LEVEYS => 8, SANOJA => 16)
    port map (clk => clk, kirjoita => ram_kirj, k_osoite => ram_kos,
              k_data => ram_kdata, l_osoite => ram_los,
              l_data => ram_ldata);
  u_rom : entity work.nelio_rom
    port map (clk => clk, osoite => rom_osoite, arvo => rom_arvo);
  u_fifo : entity work.fifo
    generic map (LEVEYS => 8, OSOITEBIT => 3)
    port map (clk => clk, nollaa => nollaa, kirjoita => kirjoita,
              k_data => k_data, taynna => taynna, lue => lue,
              l_data => l_data, tyhja => tyhja);

  testi : process
    variable rivi        : line;
    variable arpa        : unsigned(15 downto 0) := x"1D0F";
    variable kirjoitettu : natural := 0;
    variable luettu      : natural := 0;
    variable taysi_n     : natural := 0;
    variable tyhja_n     : natural := 0;
  begin
    -- RAM: kirjoitus, luku jakson viiveellä ja sama osoite yhtä aikaa.
    ram_kirj <= '1'; ram_kos <= 2; ram_kdata <= x"B2";
    wait until rising_edge(clk);
    ram_kirj <= '0'; ram_los <= 2;
    wait until rising_edge(clk);
    ram_kirj <= '1'; ram_kdata <= x"C3";      -- sama osoite 2
    wait until rising_edge(clk);
    ram_kirj <= '0';
    wait for 1 ns;
    write(rivi, "ram: sama osoite samalla reunalla -> vanha " &
                to_hstring(ram_ldata));
    wait until rising_edge(clk);
    wait for 1 ns;
    write(rivi, ", seuraavalla " & to_hstring(ram_ldata));
    writeline(output, rivi);
    assert ram_ldata = x"C3" report "RAM väärin" severity failure;

    -- ROM: kaikki 16 osoitetta.
    for i in 0 to 15 loop
      rom_osoite <= i;
      wait until rising_edge(clk);
      wait for 1 ns;
      assert rom_arvo = i * i report "ROM väärin" severity failure;
    end loop;
    rom_osoite <= 12;
    wait until rising_edge(clk);
    wait for 1 ns;
    write(rivi, "rom: 12 * 12 = " &
                integer'image(to_integer(rom_arvo)));
    writeline(output, rivi);

    -- FIFO: sanat ovat juoksevia numeroita, joten järjestys, katoaminen
    -- ja kahdentuminen näkyvät suoraan. Tahti vaihtuu kolmessa vaiheessa.
    nollaa <= '0';
    for vaihe in 0 to 2 loop
      for i in 1 to 200 loop
        arpa := arpa(14 downto 0) &
                (arpa(15) xor arpa(13) xor arpa(12) xor arpa(10));
        kirjoita <= '1' when to_integer(arpa(2 downto 0)) < 6 - 2 * vaihe
                    else '0';
        lue      <= '1' when to_integer(arpa(5 downto 3)) < 2 + 2 * vaihe
                    else '0';
        -- @alku fifotesti
        k_data   <= std_logic_vector(to_unsigned(kirjoitettu mod 256, 8));
        wait until falling_edge(clk);         -- signaalit asettuneet
        if taynna = '1' then taysi_n := taysi_n + 1; end if;
        if tyhja = '1' then tyhja_n := tyhja_n + 1; end if;
        if kirjoita = '1' and taynna = '0' then
          kirjoitettu := kirjoitettu + 1;
        end if;
        if lue = '1' and tyhja = '0' then
          assert to_integer(unsigned(l_data)) = luettu mod 256
            report "FIFO: väärä sana" severity failure;
          luettu := luettu + 1;
        end if;
        wait until rising_edge(clk);
        -- @loppu fifotesti
      end loop;
    end loop;
    write(rivi, "fifo: kirjoitettu " & integer'image(kirjoitettu) &
                ", luettu " & integer'image(luettu) &
                ", täynnä " & integer'image(taysi_n) &
                " ja tyhjä " & integer'image(tyhja_n) & " jaksoa");
    writeline(output, rivi);
    assert taysi_n > 0 and tyhja_n > 0
      report "rajatapaus jäi testaamatta" severity failure;
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
