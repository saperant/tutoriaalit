# Laskee porttitason netlistasta solutyypit ja niiden pinta-alan
# lohkoittain. Sanakirja (dict) on arvo, jota voi sisäkkäistää.

# @alku kirjasto
set pinta_ala [dict create \
    NAND2_X1 0.80 NOR2_X1 0.80 INV_X1 0.53 DFF_X1 4.52 MUX2_X1 1.86]
# @loppu kirjasto

# @alku jasennys
set lohkot [dict create]
set tuntemattomat {}
while {[gets stdin rivi] >= 0} {
    # Esim. "  DFF_X1 u_regs/q_reg_3 (.D(n12), .CK(clk), .Q(q[3]));"
    if {![regexp {^\s*(\w+)\s+([\w/\[\]]+)\s*\(} $rivi - solu inst]
        || $solu eq "module"} {
        continue
    }
    if {![dict exists $pinta_ala $solu]} {
        lappend tuntemattomat $solu
        continue
    }
    set lohko [lindex [split $inst /] 0]
    # Sisäkkäinen laskuri: lohkot -> lohko -> solu -> lukumäärä.
    dict update lohkot $lohko solut {
        dict incr solut $solu
    }
}
# @loppu jasennys

# @alku tulostus
dict for {lohko solut} $lohkot {
    set ala 0.0
    dict for {solu n} $solut {
        set ala [expr {$ala + $n * [dict get $pinta_ala $solu]}]
    }
    puts [format "%-8s %8.2f um2" $lohko $ala]
    foreach solu [lsort [dict keys $solut]] {
        puts [format "    %-10s %3d" $solu [dict get $solut $solu]]
    }
}
if {[llength $tuntemattomat]} {
    puts "tuntemattomat solut: [lsort -unique $tuntemattomat]"
}
# @loppu tulostus
