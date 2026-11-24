# Ajastinlohkon ajoitusrajoitteet (SDC). SDC on Tcl:aa: synteesi-,
# sijoittelu- ja ajoitusanalyysityokalut lukevat saman tiedoston.

# @alku sdc
create_clock -name clk -period 10.0 [get_ports clk]
set_clock_uncertainty 0.2 [get_clocks clk]

# APB-vaylan signaalit tulevat samasta kellotoimialueesta.
set_input_delay 3.0 -clock clk [get_ports s_apb_*]
set_output_delay 3.0 -clock clk [get_ports {s_apb_prdata* s_apb_pready}]

# Synkroninen nollaus: ei ajoitusvaatimusta kellon suhteen.
set_false_path -from [get_ports rst]
# @loppu sdc
