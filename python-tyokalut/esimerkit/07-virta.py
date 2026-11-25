"""Pitkän ajon tulosteen seuraaminen rivi kerrallaan ja siivous."""

import os
import signal
import subprocess
import sys

# Simulaattorin korvike: kolme lokiriviä, joista viimeinen on virhe,
# ja sen jälkeen ajo jäisi pyörimään minuutiksi.
LAPSI = """
import time
for rivi in ("käännös valmis", "ajo alkaa", "UVM_FATAL: väylä jumissa"):
    print(rivi, flush=True)
time.sleep(60)
"""


# @alku virta
def aja_seuraten(komento: list[str], keskeyta: str) -> int:
    """Tulostaa lapsen rivit sitä mukaa kuin ne syntyvät. Jos rivillä
    on merkkijono `keskeyta`, ajo lopetetaan heti."""
    with subprocess.Popen(
            komento, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, start_new_session=True) as prosessi:
        assert prosessi.stdout is not None
        try:
            for rivi in prosessi.stdout:        # rivi heti, kun se tulee
                print("  |", rivi.rstrip())
                if keskeyta in rivi:
                    break
        finally:                                # myös Ctrl+C:n jälkeen
            if prosessi.poll() is None:
                os.killpg(prosessi.pid, signal.SIGTERM)
        return prosessi.wait()


koodi = aja_seuraten([sys.executable, "-c", LAPSI], keskeyta="UVM_FATAL")
print("paluuarvo", koodi, "eli signaali", signal.Signals(-koodi).name)
# @loppu virta
