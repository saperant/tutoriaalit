-- Pikaoppaan mallit: napin värähtelyn vaimennin ja sen testipenkki.
-- @alku entiteetti
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity vaimennin is
  generic (VAKAA : positive := 4);       -- jaksoa ennen hyväksyntää
  port (
    clk, nollaa : in  std_logic;
    nappi       : in  std_logic;         -- asynkroninen tulo
    tila        : out std_logic;         -- vaimennettu taso
    painallus   : out std_logic          -- 1 jakson pulssi
  );
end entity vaimennin;
-- @loppu entiteetti

architecture rtl of vaimennin is
  -- @alku tilakone
  type tila_t is (YLHAALLA, ALAS, ALHAALLA, YLOS);
  signal t : tila_t := YLHAALLA;
  -- @loppu tilakone
  signal tahd    : std_logic_vector(1 downto 0) := "00";
  signal laskuri : natural range 0 to VAKAA - 1 := 0;
  signal valmis  : boolean;
begin
  -- @alku kombinaatio
  ehto : process (all)
  begin
    valmis <= false;                     -- oletus ensin: ei salpaa
    if laskuri = VAKAA - 1 then
      valmis <= true;
    end if;
  end process ehto;
  -- @loppu kombinaatio

  -- @alku rekisteri
  process (clk)
  begin
    if rising_edge(clk) then
      tahd      <= tahd(0) & nappi;      -- 2 kiikun tahdistin
      painallus <= '0';                  -- pulssin oletusarvo
      if nollaa = '1' then               -- synkroninen nollaus
        t       <= YLHAALLA;
        laskuri <= 0;
      else
        case t is
          when YLHAALLA =>
            laskuri <= 0;
            if tahd(1) = '1' then
              t <= ALAS;
            end if;
          when ALAS =>
            if tahd(1) = '0' then
              t <= YLHAALLA;             -- värähtely: alusta
            elsif valmis then
              t         <= ALHAALLA;
              painallus <= '1';
            else
              laskuri <= laskuri + 1;
            end if;
          when ALHAALLA =>
            laskuri <= 0;
            if tahd(1) = '0' then
              t <= YLOS;
            end if;
          when YLOS =>
            if tahd(1) = '1' then
              t <= ALHAALLA;
            elsif valmis then
              t <= YLHAALLA;
            else
              laskuri <= laskuri + 1;
            end if;
        end case;
      end if;
    end if;
  end process;
  -- @loppu rekisteri

  tila <= '1' when t = ALHAALLA or t = YLOS else '0';
end architecture rtl;

-- @alku tb-alku
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant JAKSO : time := 10 ns;
  signal clk     : std_logic := '0';
  signal nollaa  : std_logic := '1';
  signal nappi, tila, painallus : std_logic := '0';
  signal painalluksia : natural := 0;
begin
  clk <= not clk after JAKSO / 2;

  dut : entity work.vaimennin
    generic map (VAKAA => 4)
    port map (clk => clk, nollaa => nollaa, nappi => nappi,
              tila => tila, painallus => painallus);

  laske : process (clk)
  begin
    if rising_edge(clk) and painallus = '1' then
      painalluksia <= painalluksia + 1;
    end if;
  end process laske;
  -- @loppu tb-alku

  -- @alku muunnokset
  muunnokset : process
    variable v : std_logic_vector(7 downto 0);
    variable u : unsigned(7 downto 0);
    variable s : signed(7 downto 0);
    variable l : signed(15 downto 0);
  begin
    v := x"F6";
    u := unsigned(v);                    -- tyyppimuunnos: 246
    s := signed(v);                      -- tyyppimuunnos: -10
    l := resize(s, 16);                  -- etumerkin laajennus: FFF6
    v := std_logic_vector(to_signed(-10, 8));
    assert to_integer(u) = 246 and to_integer(s) = -10
      severity failure;
    assert to_hstring(l) = "FFF6" severity failure;
    u := u + 20;                         -- 266 mod 256 = 10
    assert u = 10 and shift_right(s, 1) = -5 severity failure;
    wait;
  end process muunnokset;
  -- @loppu muunnokset

  -- @alku testi
  testi : process
    variable rivi : line;
  begin
    wait for 2 * JAKSO;
    nollaa <= '0';
    for i in 1 to 3 loop                 -- värähtelevä painallus
      nappi <= '1'; wait for 2 * JAKSO;
      nappi <= '0'; wait for 1 * JAKSO;
    end loop;
    nappi <= '1';
    wait until painallus = '1' for 1 us;
    assert painallus = '1' report "aikakatkaisu" severity failure;
    wait for 20 * JAKSO;
    write(rivi, "tila " & to_string(tila) & ", painalluksia "
                & integer'image(painalluksia));
    writeline(output, rivi);
    std.env.finish;
  end process testi;
end architecture sim;
-- @loppu testi
