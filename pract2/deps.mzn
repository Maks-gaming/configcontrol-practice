% Задача 7: зависимости пакетов в общей форме.
% Пакет 1 - корень (root). Версии каждого пакета перечислены по возрастанию,
% поэтому версия = её номер в списке, 0 = пакет не ставим.

int: n;                                  % число пакетов
array[1..n] of string: names;            % имена пакетов
int: maxv;                               % наибольшее число версий у пакета
array[1..n, 1..maxv] of string: vers;    % названия версий ("" если версии нет)
array[1..n] of int: nv;                  % сколько версий у каждого пакета

% зависимость k: пакет from_p версии from_v требует пакет to_p версии от lo до hi
int: m;
array[1..m] of int: from_p;
array[1..m] of int: from_v;
array[1..m] of int: to_p;
array[1..m] of int: lo;
array[1..m] of int: hi;

% выбранная версия каждого пакета
array[1..n] of var 0..maxv: sel;

constraint forall(p in 1..n)(sel[p] <= nv[p]);
constraint sel[1] = 1;

% если пакет с нужной версией выбран, его зависимость тоже выполнена
constraint forall(k in 1..m)(
    sel[from_p[k]] = from_v[k] -> (sel[to_p[k]] >= lo[k] /\ sel[to_p[k]] <= hi[k])
);

% лишних пакетов не ставим: каждый (кроме root) кому-то нужен
constraint forall(p in 2..n)(
    sel[p] > 0 -> exists(k in 1..m)(to_p[k] = p /\ sel[from_p[k]] = from_v[k])
);

% берём версии посвежее
solve maximize sum(sel);

output [ if fix(sel[p]) > 0 then names[p] ++ " " ++ vers[p, fix(sel[p])] ++ "\n" else "" endif
       | p in 1..n ];
