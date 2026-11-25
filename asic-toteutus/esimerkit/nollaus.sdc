# Asynkronisesti nollautuva laskuri 400 MHz:n kellolla.
# @alku nollaus
create_clock -name clk -period 2.50 [get_ports clk]
set_clock_uncertainty 0.05 [get_clocks clk]
# Ulkoinen nollaus on asynkroninen: sen alkamista ei ajoiteta.
set_false_path -from [get_ports nollaa_n]
# @loppu nollaus
