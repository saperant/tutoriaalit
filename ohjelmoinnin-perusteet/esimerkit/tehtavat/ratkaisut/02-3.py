"""Malliratkaisu 02-3: Lasku tasan."""

summa_snt = int(input())
maksajia = int(input())
osuus_snt = summa_snt // maksajia
jakamatta = summa_snt % maksajia
eurot = osuus_snt // 100
sentit = osuus_snt % 100
print(f"Osuus: {eurot},{sentit:02d} €, jakamatta: {jakamatta} snt")
