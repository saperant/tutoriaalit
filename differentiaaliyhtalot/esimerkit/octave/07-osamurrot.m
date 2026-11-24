% Siirtofunktio ja osamurrot Octavella: roots ja residue.
1;

# @alku osamurrot
% Y(s) = (s^2 + 3 s + 4) / (s (s + 1) (s + 2))
b = [1 3 4];
a = conv([1 0], conv([1 1], [1 2]));
[r, p] = residue(b, a);
[p, i] = sort(p);
r = r(i);
for j = 1:numel(p)
  printf("%+g / (s - (%g))\n", r(j), p(j));
end
% Navat RLC-alipäästölle s^2 + 2000 s + 1e8:
n = roots([1 2000 1e8]);
printf("navat: %.1f %+.1fj ja %.1f %+.1fj\n", real(n(1)), imag(n(1)), ...
       real(n(2)), imag(n(2)));
# @loppu osamurrot
