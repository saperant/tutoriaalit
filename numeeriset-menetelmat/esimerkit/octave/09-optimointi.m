% Optimointi Octavella: fminbnd, fminsearch ja fminunc.
[x, fx] = fminbnd(@(x) -x * (1 - 2*x)^2, 0, 0.5);
printf("fminbnd: x = %.3f, tilavuus %.4f\n", x, -fx);

rosen = @(v) (1 - v(1))^2 + 100 * (v(2) - v(1)^2)^2;
optiot = optimset("TolX", 1e-10, "TolFun", 1e-12, "MaxFunEvals", 5000);
v = fminsearch(rosen, [-1.2, 1], optiot);   % Nelder-Mead, ei derivaattoja
printf("fminsearch: (%.4f, %.4f)\n", v(1), v(2));
v2 = fminunc(rosen, [-1.2, 1]);             % kvasi-Newton
printf("fminunc:    (%.4f, %.4f)\n", v2(1), v2(2));
