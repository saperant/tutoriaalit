"""Poikkeusryhmät: kaikki validointivirheet kerralla (3.11+)."""


# @alku ryhmat
class KenttaVirhe(ValueError):
    pass


def validoi(lomake: dict[str, str]) -> None:
    virheet: list[Exception] = []
    if "@" not in lomake.get("email", ""):
        virheet.append(KenttaVirhe("email: virheellinen osoite"))
    if not lomake.get("nimi", "").strip():
        virheet.append(KenttaVirhe("nimi: pakollinen"))
    if not lomake.get("ika", "").isdigit():
        virheet.append(TypeError("ika: ei luku"))
    if virheet:
        raise ExceptionGroup("lomake ei kelpaa", virheet)


try:
    validoi({"email": "ada.example.com", "nimi": " ", "ika": "x"})
except* KenttaVirhe as kenttavirheet:
    for kentta in kenttavirheet.exceptions:
        print("kenttä:", kentta)
except* TypeError as tyyppivirheet:
    for tyyppi in tyyppivirheet.exceptions:
        print("tyyppi:", tyyppi)
# @loppu ryhmat
