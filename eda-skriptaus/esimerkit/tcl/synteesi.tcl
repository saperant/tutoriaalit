# Yosysin Tcl-skripti: laskurin synteesi usealla leveydellä.
#
#   LEVEYDET="4 8 16" RTL=rtl/laskuri.sv TULOS=hakemisto \
#       yosys -q -c tcl/synteesi.tcl
#
# Yosysin komennot eivät palauta Tcl:lle arvoja, joten tulokset
# kirjoitetaan tiedostoihin (tee -o) ja luetaan niistä.
yosys -import

# @alku silmukka
set tulos $::env(TULOS)
file mkdir $tulos
foreach leveys $::env(LEVEYDET) {
    design -reset
    read_verilog -sv $::env(RTL)
    chparam -set LEVEYS $leveys laskuri
    synth -top laskuri -flatten
    abc -g AND,OR,XOR,MUX
    opt_clean
    tee -q -o $tulos/stat_$leveys.json stat -json
    tee -q -o $tulos/ltp_$leveys.txt ltp -noff
    write_blif -impltf $tulos/laskuri_$leveys.blif
    puts "synteesi LEVEYS=$leveys valmis"
}
# @loppu silmukka
