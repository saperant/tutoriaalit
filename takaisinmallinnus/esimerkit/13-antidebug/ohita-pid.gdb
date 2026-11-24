# Ohittaa ensimmäisen tarkistuksen: jaljittajan_pid palauttaa 0.
# @alku ohita-pid
python
class Nolla(gdb.FinishBreakpoint):
    def stop(self):
        print(f"> jaljittajan_pid palautti jäljittäjän pid:n "
              f"(> 0: {int(gdb.parse_and_eval('$rax')) > 0}), asetetaan 0")
        gdb.execute("set $rax = 0")
        return False


class Pid(gdb.Breakpoint):
    def stop(self):
        Nolla(gdb.newest_frame(), internal=True)
        return False


Pid("jaljittajan_pid")
end
run > ohjelma.txt
# @loppu ohita-pid
