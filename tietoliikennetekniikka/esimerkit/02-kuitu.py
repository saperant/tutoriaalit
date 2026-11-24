"""Valokuituyhteyden vaimennus- ja dispersiobudjetti."""

# @alku budjetti
LAHETYSTEHO_DBM = -3.0       # lähetin
HERKKYYS_DBM = -20.0         # vastaanottimen herkkyys
VARA_DB = 3.0                # vanheneminen, korjausjatkokset
VAIMENNUS_DB_KM = 0.35       # yksimuotokuitu, 1310 nm
LIITIN_DB = 0.5              # kaksi liitintä
JATKOS_DB = 0.1              # hitsausjatkos 2 km:n välein

kaytettavissa = LAHETYSTEHO_DBM - HERKKYYS_DBM - VARA_DB
print(f"käytettävissä {kaytettavissa:.1f} dB")
for km in (10, 20, 30, 40):
    jatkokset = km // 2
    hukka = km * VAIMENNUS_DB_KM + 2 * LIITIN_DB + jatkokset * JATKOS_DB
    tila = "ok" if hukka <= kaytettavissa else "EI RIITÄ"
    print(f"{km:>3} km: vaimennus {hukka:5.2f} dB  {tila}")
# @loppu budjetti

# @alku dispersio
# Kromaattinen dispersio levittää pulssia: Δt = D · L · Δλ.
D_PS_NM_KM = 17.0            # yksimuotokuitu, 1550 nm
SPEKTRI_NM = 0.1             # lähettimen spektrin leveys
for km in (10, 40, 80):
    levenema_ps = D_PS_NM_KM * km * SPEKTRI_NM
    # Nyrkkisääntö: levenemä saa olla korkeintaan noin neljännes
    # bittiajasta (NRZ).
    raja_gbit = 1 / (4 * levenema_ps * 1e-12) / 1e9
    print(f"{km:>3} km: levenemä {levenema_ps:5.0f} ps,"
          f" yläraja noin {raja_gbit:5.1f} Gbit/s")
# @loppu dispersio
