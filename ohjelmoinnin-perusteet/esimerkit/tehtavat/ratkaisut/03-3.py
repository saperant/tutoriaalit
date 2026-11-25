"""Malliratkaisu 03-3: Collatzin jono."""

n = int(input())
askelia = 0
while n != 1:
    if n % 2 == 0:
        n = n // 2
    else:
        n = 3 * n + 1
    askelia += 1
print(f"Askelia: {askelia}")
