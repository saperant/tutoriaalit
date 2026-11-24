% Jäykkä yhtälö Octavella: ode45 vastaan ode23s.
1;

# @alku jaykka
f = @(t, y) -1000 * (y - cos(t));
% ode23s on matalan kertaluvun jäykkä ratkaisija: se on edullisin, kun
% toleranssi on maltillinen. Refine 1 palauttaa vain todelliset askeleet.
opt = odeset("RelTol", 1e-3, "AbsTol", 1e-6, "Refine", 1);
[t45, y45] = ode45(f, [0 10], 0, opt);
[t15, y15] = ode23s(f, [0 10], 0, opt);
printf("ode45:  %5d askelta, y(10) = %.4f\n", numel(t45) - 1, y45(end));
printf("ode23s: %5d askelta, y(10) = %.4f\n", numel(t15) - 1, y15(end));
# @loppu jaykka
