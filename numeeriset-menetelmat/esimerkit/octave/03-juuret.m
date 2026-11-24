% Yhtälöt Octavella: fzero, roots ja fsolve.
1;  % tiedosto on skripti, vaikka siinä määritellään funktio

function F = yhtalot(v)
  F = [v(1)^2 + v(2)^2 - 4; exp(v(1)) - 1 - v(2)];
end

f = @(x) x.^3 - 2*x - 5;
juuri = fzero(f, [2, 3]);             % Brentin menetelmä välille
printf("fzero:  %.11f\n", juuri);

r = roots([1, 0, -2, -5]);            % kumppanimatriisin ominaisarvot
r = r(abs(imag(r)) < 1e-12);
printf("roots:  %.11f (reaalinen juuri)\n", real(r));

optiot = optimset("TolFun", 1e-12, "TolX", 1e-12);
[v, ~, tila] = fsolve(@yhtalot, [1; 1], optiot);
printf("fsolve: (%.8f, %.8f), tila %d\n", v(1), v(2), tila);
