# Samat rajoitteet ja tieto siitä, että kertolasku saa kaksi jaksoa.
source kertoja2.sdc
# @alku monisykli
set_multicycle_path 2 -setup -from [get_cells {a_r* b_r*}] \
    -to [get_cells tulo*]
set_multicycle_path 1 -hold -from [get_cells {a_r* b_r*}] \
    -to [get_cells tulo*]
# Nollaus pidetään päällä useita jaksoja käynnistyksessä.
set_false_path -from [get_ports nollaa]
# @loppu monisykli
