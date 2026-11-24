"""Redis Streamsin kuluttajaryhmä vaihe vaiheelta: mitä tapahtuu, kun
kuluttaja kaatuu ennen kuittausta."""

from __future__ import annotations

import redis

from testiapu import kontit
from varasto import tapahtumat


def odottaa(r: redis.Redis) -> int:
    return int(r.xpending(tapahtumat.VIRTA, tapahtumat.RYHMA)["pending"])


# @alku vaiheet
def main() -> None:
    with kontit.redis_kontti() as kontti:
        r = redis.Redis(host=kontti.get_container_host_ip(),
                        port=int(kontti.get_exposed_port(6379)))
        tapahtumat.luo_ryhma(r)
        for tunnus in (101, 102):
            tapahtumat.julkaise(r, tunnus, "ABC-1", 1)
        print("virrassa:", r.xlen(tapahtumat.VIRTA))

        def kaatuu(_: dict[str, str]) -> None:
            raise RuntimeError("kaatui")

        try:
            tapahtumat.kasittele(r, "A", kaatuu, kerralla=1)
        except RuntimeError:
            print("A luki viestin ja kaatui; odottaa kuittausta:",
                  odottaa(r))

        def tulosta(v: dict[str, str]) -> None:
            print("  B käsitteli", v["tunnus"])

        print("B lukee uudet:")
        tapahtumat.kasittele(r, "B", tulosta)
        print("odottaa kuittausta:", odottaa(r))
        print("B ottaa A:n viestin haltuun:")
        tapahtumat.ota_hylatyt(r, "B", tulosta, vanhempi_kuin_ms=0)
        print("odottaa kuittausta:", odottaa(r))
        r.close()
# @loppu vaiheet


if __name__ == "__main__":
    main()
