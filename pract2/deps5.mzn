% Задача 5: root, menu, dropdown, icons
% 0 = пакет не ставим, иначе номер версии

% menu: 1 = 1.0.0, 2 = 1.1.0, ..., 6 = 1.5.0
var 0..6: menu;
% dropdown: 1 = 1.8.0, 2 = 2.0.0, 3 = 2.1.0, 4 = 2.2.0, 5 = 2.3.0
var 0..5: dropdown;
% icons: 1 = 1.0.0, 2 = 2.0.0
var 0..2: icons;

% root зависит от menu (любая версия) и icons 1.0.0
constraint menu > 0;
constraint icons = 1;

% menu 1.1.0 - 1.5.0 зависят от dropdown 2.0.0 - 2.3.0
constraint menu >= 2 -> dropdown >= 2;
% menu 1.0.0 зависит от dropdown 1.8.0
constraint menu = 1 -> dropdown = 1;
% dropdown 2.0.0 - 2.3.0 зависят от icons 2.0.0
constraint dropdown >= 2 -> icons = 2;

% хотим версии посвежее
solve maximize menu + dropdown;

output ["menu = \(menu), dropdown = \(dropdown), icons = \(icons)\n"];
