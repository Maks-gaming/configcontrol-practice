% Счастливый билет: сумма первых трёх цифр = сумма последних трёх
include "alldifferent.mzn";
array[1..6] of var 0..9: d;

constraint all_different(d);
constraint d[1] + d[2] + d[3] = d[4] + d[5] + d[6];

% ищем билет с минимальной суммой трёх цифр
solve minimize d[1] + d[2] + d[3];

output ["Билет: "] ++ [show(d[i]) | i in 1..6] ++ ["\n",
        "Сумма: \(d[1] + d[2] + d[3])\n"];
