"""Lua-skripti: tarkistus ja muutos yhtenä atomisena operaationa."""

from nosql.kontit import Ymparisto, aja

# @alku lua
VARAA = """
local saldo = tonumber(redis.call('GET', KEYS[1]) or '0')
local maara = tonumber(ARGV[1])
if saldo < maara then
  return -1
end
redis.call('DECRBY', KEYS[1], maara)
redis.call('HINCRBY', KEYS[2], ARGV[2], maara)
return saldo - maara
"""
# @loppu lua


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()
    # @alku kaytto
    varaa = r.register_script(VARAA)
    r.set("varasto:42", 5)
    for asiakas, maara in [("aino", 2), ("eero", 2), ("ilona", 2)]:
        jaljella = varaa(keys=["varasto:42", "varaukset:42"],
                         args=[maara, asiakas])
        tila = "ok" if jaljella >= 0 else "ei riita"
        print(f"{asiakas} varaa {maara}: {tila}")
    print("varaukset:", sorted(r.hgetall("varaukset:42").items()))
    print("varasto:", r.get("varasto:42"))
    # @loppu kaytto


if __name__ == "__main__":
    aja(ajo)
