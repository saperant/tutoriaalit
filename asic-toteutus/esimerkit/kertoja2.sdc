# Rajoitteet kertojalle noin 700 MHz:n kellolla.
# @alku perus
create_clock -name clk -period 1.40 [get_ports clk]
set_clock_uncertainty 0.05 [get_clocks clk]
set_input_delay 0.30 -clock clk [all_inputs]
set_output_delay 0.20 -clock clk [all_outputs]
set_input_transition 0.10 [all_inputs]
set_load 0.005 [all_outputs]
# @loppu perus
