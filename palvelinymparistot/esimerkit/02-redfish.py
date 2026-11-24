"""Palvelimen kunto Redfish-rajapinnasta.

BMC (baseboard management controller) tarjoaa Redfish-rajapinnan
HTTPS:n yli, esimerkiksi GET /redfish/v1/Chassis/1/Power ja
/redfish/v1/Chassis/1/Thermal. Tämä tarkistus lukee vastaukset ja
tiivistää ne valvontajärjestelmälle tilaksi OK/WARNING/CRITICAL.
Oikeasti vastaukset haetaan esim. urllib.request-kirjastolla
hallintaverkosta; esimerkissä ne ovat valmiina.
"""

import json
from typing import Any

POWER = """{
  "PowerSupplies": [
    {"Name": "PSU1", "PowerInputWatts": 412,
     "Status": {"State": "Enabled", "Health": "OK"}},
    {"Name": "PSU2", "PowerInputWatts": 0,
     "Status": {"State": "Enabled", "Health": "Critical"}}
  ],
  "Redundancy": [{"Mode": "N+1", "Status": {"Health": "Critical"}}]
}"""

THERMAL = """{
  "Temperatures": [
    {"Name": "CPU1 Temp", "ReadingCelsius": 64,
     "UpperThresholdNonCritical": 85, "UpperThresholdCritical": 95},
    {"Name": "Inlet Temp", "ReadingCelsius": 31,
     "UpperThresholdNonCritical": 30, "UpperThresholdCritical": 40}
  ],
  "Fans": [
    {"Name": "Fan1", "Reading": 7200, "Status": {"Health": "OK"}},
    {"Name": "Fan2", "Reading": 7150, "Status": {"Health": "OK"}}
  ]
}"""

TASOT = {"OK": 0, "WARNING": 1, "CRITICAL": 2}


# @alku tarkistus
def tarkista(power: dict[str, Any], thermal: dict[str, Any]
             ) -> list[tuple[str, str]]:
    havainnot: list[tuple[str, str]] = []
    for psu in power["PowerSupplies"]:
        if psu["Status"]["Health"] != "OK":
            havainnot.append(("CRITICAL", f"{psu['Name']}: "
                              f"{psu['Status']['Health']}"))
    for r in power.get("Redundancy", []):
        if r["Status"]["Health"] != "OK":
            havainnot.append(("CRITICAL",
                              f"virransyötön redundanssi {r['Mode']} "
                              "menetetty"))
    for t in thermal["Temperatures"]:
        arvo = t["ReadingCelsius"]
        if arvo >= t["UpperThresholdCritical"]:
            havainnot.append(("CRITICAL", f"{t['Name']} {arvo} °C"))
        elif arvo >= t["UpperThresholdNonCritical"]:
            havainnot.append(("WARNING", f"{t['Name']} {arvo} °C"))
    for f in thermal["Fans"]:
        if f["Status"]["Health"] != "OK":
            havainnot.append(("WARNING", f"{f['Name']} ei kunnossa"))
    return havainnot
# @loppu tarkistus


def main() -> int:
    havainnot = tarkista(json.loads(POWER), json.loads(THERMAL))
    tila = max((h[0] for h in havainnot), key=TASOT.__getitem__,
               default="OK")
    print(f"{tila}: {len(havainnot)} havaintoa")
    for taso, viesti in havainnot:
        print(f"  {taso:8} {viesti}")
    return TASOT[tila]


if __name__ == "__main__":
    # Valvontajärjestelmä lukisi tilan paluuarvosta (0/1/2); tässä
    # tulostetaan se, jotta esimerkki päättyy onnistuneesti.
    print(f"paluuarvo valvonnalle: {main()}")
