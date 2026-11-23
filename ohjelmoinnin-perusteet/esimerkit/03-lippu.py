"""Määrittää konserttilipun hinnan ostajan iän mukaan."""

PERUSHINTA = 25
for ika in [4, 15, 34, 67]:
    if ika < 7:
        hinta = 0
        ryhma = "lapsi, ilmainen"
    elif ika < 18:
        hinta = PERUSHINTA // 2
        ryhma = "nuori"
    elif ika >= 65:
        hinta = PERUSHINTA - 5
        ryhma = "eläkeläinen"
    else:
        hinta = PERUSHINTA
        ryhma = "aikuinen"
    print(f"{ika:>3} v: {hinta:>2} € ({ryhma})")
