% Задача 6. 0 = пакет не ставим, иначе номер версии
% foo: 1 = 1.0.0, 2 = 1.1.0
var 0..2: foo;
% left, right: 1 = 1.0.0
var 0..1: left;
var 0..1: right;
% shared: 1 = 1.0.0, 2 = 2.0.0
var 0..2: shared;
% target: 1 = 1.0.0, 2 = 2.0.0
var 0..2: target;

% root 1.0.0 зависит от foo ^1.0.0 и target ^2.0.0
constraint foo >= 1;
constraint target = 2;
% foo 1.1.0 зависит от left ^1.0.0 и right ^1.0.0
constraint foo = 2 -> (left = 1 /\ right = 1);
% left 1.0.0 зависит от shared >=1.0.0
constraint left = 1 -> shared >= 1;
% right 1.0.0 зависит от shared <2.0.0
constraint right = 1 -> shared = 1;
% shared 1.0.0 зависит от target ^1.0.0
constraint shared = 1 -> target = 1;

% версии посвежее, лишнего не ставим
solve maximize 10 * foo - left - right - shared;

output ["foo = \(foo), left = \(left), right = \(right), ",
        "shared = \(shared), target = \(target)\n"];
