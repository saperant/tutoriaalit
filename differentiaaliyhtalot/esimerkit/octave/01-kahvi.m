% Jäähtyvä kahvi GNU Octavella: ode45 ja tarkka ratkaisu.
1;

# @alku kahvi
T_ymp = 21; T_alku = 90; k = 0.045;
f = @(t, T) -k * (T - T_ymp);
opt = odeset("RelTol", 1e-9, "AbsTol", 1e-9);
[t, T] = ode45(f, [0 10 20 30], T_alku, opt);
for i = 2:numel(t)
  tarkka = T_ymp + (T_alku - T_ymp) * exp(-k * t(i));
  printf("t = %4.1f: ode45 %.4f, tarkka %.4f\n", t(i), T(i), tarkka);
end
printf("60 C kohdalla: t = %.2f min\n", log((T_alku - T_ymp) / (60 - T_ymp)) / k);
# @loppu kahvi
