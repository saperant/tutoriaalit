# SDC- ja UPF-tiedostojen kuivaharjoitus Tcl-tulkilla. Komennot
# korvataan proseduureilla, jotka tulostavat komennon nimen ja
# valitsimien maaran. Nain tiedoston Tcl-syntaksi ja komentojen nimet
# tarkistetaan ilman kaupallista tyokalua; tuntematon komento kaataa
# tarkistuksen.

set tunnetut {
    create_clock set_clock_uncertainty set_input_delay set_output_delay
    set_false_path get_ports get_clocks
    create_power_domain create_supply_port create_supply_net
    connect_supply_net create_power_switch set_isolation
}

foreach komento $tunnetut {
    proc $komento {args} [format {
        set valitsimet [lsearch -all -inline -glob $args -*]
        if {[string match get_* %1$s]} { return "<%1$s $args>" }
        puts [format "  %%-22s %%d valitsinta" %1$s [llength $valitsimet]]
    } $komento]
}

foreach tiedosto $argv {
    puts "[file tail $tiedosto]:"
    if {[catch {source $tiedosto} virhe]} {
        puts "  VIRHE: $virhe"
        exit 1
    }
}
