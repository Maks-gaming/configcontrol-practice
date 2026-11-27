"""Парсер и транслятор учебного конфигурационного языка."""

from dataclasses import dataclass
from string import ascii_letters
import xml.etree.ElementTree as ET

import pyparsing as pp


BINARY_OPERANDS = 2
RESULT_SIZE = 1


class LanguageError(ValueError):
    """Ошибка синтаксиса или вычисления конфигурации."""


@dataclass
class Definition:
    """Объявление константы."""

    name: str
    value: object


@dataclass
class Expression:
    """Постфиксное константное выражение."""

    items: list


def build_parser():
    """Создает грамматику языка средствами pyparsing."""
    number = pp.Regex(r"[+-]?\d+")
    number.set_parse_action(lambda tokens: int(tokens[0]))
    text = pp.QuotedString('"', esc_char="\\", unquote_results=True)
    name = pp.Word(ascii_letters)
    value = pp.Forward()
    expression = pp.Forward()

    array = pp.Suppress("[") + pp.Group(value[...]) + pp.Suppress("]")
    array.set_parse_action(lambda tokens: [list(tokens[0])])

    operator = (
        pp.Literal("mod()")
        | pp.Literal("abs()")
        | pp.Literal("+")
        | pp.Literal("-")
    )
    expression_item = expression | number | operator | name
    expression <<= (
        pp.Suppress("#(")
        + pp.Group(expression_item[1, ...])
        + pp.Suppress(")")
    )
    expression.set_parse_action(
        lambda tokens: Expression(list(tokens[0]))
    )

    value <<= number | text | array | expression
    definition = (
        pp.Suppress("(")
        + pp.Suppress("def")
        + name
        + value
        + pp.Suppress(")")
    )
    definition.set_parse_action(
        lambda tokens: Definition(tokens[0], tokens[1])
    )
    return (definition | value)[...]


def require_number(value, operation):
    """Проверяет, что операнд арифметической операции является числом."""
    if type(value) is not int:
        raise LanguageError(
            f"Операция {operation} принимает только числа: {value!r}"
        )


def apply_binary(operation, left, right):
    """Выполняет бинарную операцию постфиксного выражения."""
    require_number(left, operation)
    require_number(right, operation)
    if operation == "+":
        return left + right
    if operation == "-":
        return left - right
    try:
        return left % right
    except ZeroDivisionError as error:
        raise LanguageError("Деление на ноль в mod()") from error


def take_operands(stack, operation, count):
    """Извлекает нужное число операндов из стека выражения."""
    if len(stack) < count:
        raise LanguageError(f"Недостаточно операндов для {operation}")
    operands = stack[-count:]
    del stack[-count:]
    return operands


def evaluate_expression(expression, constants):
    """Вычисляет постфиксное выражение на стеке."""
    stack = []
    for item in expression.items:
        if isinstance(item, Expression):
            stack.append(evaluate_expression(item, constants))
        elif type(item) is int:
            stack.append(item)
        elif item in ("+", "-", "mod()"):
            left, right = take_operands(stack, item, BINARY_OPERANDS)
            stack.append(apply_binary(item, left, right))
        elif item == "abs()":
            operand, = take_operands(stack, item, RESULT_SIZE)
            require_number(operand, item)
            stack.append(abs(operand))
        elif item in constants:
            stack.append(constants[item])
        else:
            raise LanguageError(f"Неизвестная константа: {item}")
    if len(stack) != RESULT_SIZE:
        raise LanguageError("Выражение должно оставить одно значение")
    return stack[0]


def evaluate_value(value, constants):
    """Вычисляет выражения внутри значения и вложенных массивов."""
    if isinstance(value, Expression):
        return evaluate_expression(value, constants)
    if isinstance(value, list):
        return [evaluate_value(item, constants) for item in value]
    return value


def add_xml_value(parent, tag, value, name=None):
    """Добавляет значение в XML с явным указанием его типа."""
    attributes = {}
    if name is not None:
        attributes["name"] = name
    if type(value) is int:
        element = ET.SubElement(parent, tag, attributes)
        element.set("type", "number")
        element.text = str(value)
    elif isinstance(value, str):
        element = ET.SubElement(parent, tag, attributes)
        element.set("type", "string")
        element.text = value
    else:
        element = ET.SubElement(parent, tag, attributes)
        element.set("type", "array")
        for item in value:
            add_xml_value(element, "item", item)


def translate(text):
    """Преобразует текст учебного языка в XML."""
    try:
        statements = build_parser().parse_string(text, parse_all=True)
    except pp.ParseException as error:
        message = (
            f"Синтаксическая ошибка в строке {error.lineno}, "
            f"столбце {error.col}: {error.msg}"
        )
        raise LanguageError(message) from error

    root = ET.Element("config")
    constants = {}
    for statement in statements:
        if isinstance(statement, Definition):
            if statement.name in constants:
                raise LanguageError(
                    f"Константа уже объявлена: {statement.name}"
                )
            value = evaluate_value(statement.value, constants)
            constants[statement.name] = value
            add_xml_value(root, "constant", value, statement.name)
        else:
            value = evaluate_value(statement, constants)
            add_xml_value(root, "value", value)
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"
