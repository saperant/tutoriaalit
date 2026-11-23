"""asyncio: tuhansia samanaikaisia odotuksia yhdessä säikeessä."""

import asyncio


# @alku asyncio
async def hae(osoite: str, rajoitin: asyncio.Semaphore) -> tuple[str, int]:
    async with rajoitin:                 # enintään N pyyntöä kerralla
        await asyncio.sleep(0.05)        # verkon odotus
        if osoite.endswith("/7"):
            raise ConnectionError(f"{osoite}: yhteys katkesi")
        return osoite, 200


async def main() -> None:
    rajoitin = asyncio.Semaphore(10)
    osoitteet = [f"https://palvelu.example/{n}" for n in range(100)]
    tehtavat = [hae(o, rajoitin) for o in osoitteet]
    tulokset = await asyncio.gather(*tehtavat, return_exceptions=True)
    onnistuneet = [t for t in tulokset if not isinstance(t, BaseException)]
    virheet = [t for t in tulokset if isinstance(t, BaseException)]
    print(f"{len(onnistuneet)} onnistui, {len(virheet)} epäonnistui")
    print(virheet[0])

    try:
        async with asyncio.timeout(0.01):
            await hae("https://hidas.example/1", rajoitin)
    except TimeoutError:
        print("aikakatkaisu")


asyncio.run(main())
# @loppu asyncio
