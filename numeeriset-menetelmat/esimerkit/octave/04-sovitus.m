% Interpolointi ja sovitus Octavella.
ajat = [0 1 2 4];
lampo = [12 15 17 16];
p = polyfit(ajat, lampo, 3);          % 4 pistettä, aste 3: interpolointi
printf("polyval(p, 2.5) = %.3f\n", polyval(p, 2.5));
printf("interp1 linear  = %.3f\n", interp1(ajat, lampo, 2.5));
printf("interp1 spline  = %.3f\n", interp1(ajat, lampo, 2.5, "spline"));

% Sovitus: suora mittauksiin pienimmän neliösumman mielessä.
x = (0:5)';
y = [1.1; 2.9; 5.2; 7.1; 8.8; 11.2];
A = [ones(size(x)), x];
c = A \ y;                            % ylimäärätty: \ ratkaisee PNS:n
printf("suora: y = %.4f + %.4f x\n", c(1), c(2));
