% Differentiaaliyhtälöt Octavella: ode45 (Dormand-Prince) ja ode15s.
f = @(t, y) -2 * t * y;
optiot = odeset("RelTol", 1e-8, "AbsTol", 1e-10);
[t, y] = ode45(f, [0 2], 1, optiot);
printf("ode45: virhe hetkellä 2 alle 1e-7: %d\n", ...
       abs(y(end) - exp(-4)) < 1e-7);

% Jäykkä van der Pol: ode15s on implisiittinen (BDF-tyyppinen).
mu = 100;
vdp = @(t, y) [y(2); mu * (1 - y(1)^2) * y(2) - y(1)];
[t1, y1] = ode45(vdp, [0 200], [2; 0]);
[t2, y2] = ode15s(vdp, [0 200], [2; 0]);
printf("ode45:llä yli viisi kertaa ode15s:n askeleet: %d\n", ...
       numel(t1) > 5 * numel(t2));
printf("y(200): ode45 %.2f, ode15s %.2f\n", y1(end, 1), y2(end, 1));
