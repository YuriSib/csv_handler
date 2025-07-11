import pytest
from script import where, aggregate, parse_args, get_data_from_csv, order_by
from unittest.mock import patch
import sys


table = [
    ['Name', 'Brand', 'Price'],
    ['iPhone 15', 'Apple', '999'],
    ['Galaxy S23', 'Samsung', '899'],
    ['Pixel 8', 'Google', '799']
]


"""Тестирую where"""


@pytest.mark.parametrize("operator,value,expected", [
    ('>', '800', [['iPhone 15', 'Apple', '999'], ['Galaxy S23', 'Samsung', '899']]),
    ('<', '900', [['Galaxy S23', 'Samsung', '899'], ['Pixel 8', 'Google', '799']]),
    ('=', '999', [['iPhone 15', 'Apple', '999']]),
    ('<', '800.5', [['Pixel 8', 'Google', '799']]),
])
def test_where_valid_numeric_filtering(operator, value, expected):
    result = where(table, 'Price', operator, value)
    assert result == expected


@pytest.mark.parametrize("operator,value,response", [
    ('!=', '800', 'Некорректно указан оператор'),
    ('>', '900', 'Нельзя применять операторы сравнения к строковым данным'),
    ('<', 'Google', 'Нельзя применять операторы сравнения к строковым данным'),
    ('<', '900,5', 'Нельзя применять операторы сравнения к строковым данным'),
])
def test_where_incorrect_operator(operator, value, response):
    result = where(table, 'Brand', operator, value)
    assert result == response


def test_where_unknown_field():
    result = where(table, 'Unknown', '=', 'Apple')
    assert result == 'Указанного поля нет в таблице'


def test_where_invalid_type_casting():
    result = where(table, 'Price', '=', 'not_a_number')
    assert result.startswith('Переданное значение не валидно')


"""Тестирую aggregate"""


def test_agg_dnt_exist_field():
    result = aggregate(table, 'Description', 'avg')
    assert result == 'Указанного поля нет в таблице'


def test_agg_invalid_field_type():
    result = aggregate(table, 'Brand', 'avg')
    assert result == 'Агрегация доступна только для числовых полей'


def test_agg_invalid_agg_arg():
    result = aggregate(table, 'Price', 'Avg')
    assert result == 'Некорректно указан аргумент агрегации'


def test_agg_unknown_field():
    result = aggregate(table, 'Unknown', 'Avg')
    assert result == 'Указанного поля нет в таблице'


"""Тестирую parse_args"""


@pytest.fixture
def run_with_args():
    def _run(args_list):
        with patch.object(sys, 'argv', ['script.py'] + args_list):
            return parse_args()
    return _run


@pytest.mark.parametrize("input_,response", [
    (['--where', 'brand=apple', '--aggregate', 'rating=min'], "Обязательный аргумент '--file' не указан"),
    (['--file', 'file_path', '--aggregate', 'rating=min'], "Не передан csv документ для обработки"),
    (['--file', 'file_path.csv'], "Не переданы аргументы действия"),
])
def test_pa_invalid_data(run_with_args, input_, response):
    result = run_with_args(input_)
    assert result == response


@pytest.mark.parametrize("input_,response", [
    (['--file', 'file_path.csv', '--where', 'brand==apple'], "Не корректное значение."),
    (['--file', 'file_path.csv', '--aggregator', 'brand=apple'], "Не корректный флаг."),
])
def test_pa_invalid_data_2(run_with_args, input_, response):
    result = run_with_args(input_)
    assert result.startswith(response)


"""Тестирую order_by"""


@pytest.mark.parametrize("field,agg_value,response", [
    ('Name', 'Asc', 'Некорректное значение сортировки'),
    ('name', 'asc', 'Указанного поля нет в таблице'),
    ('Name', 'desc', [
        ['Galaxy S23', 'Samsung', '899'],
        ['Pixel 8', 'Google', '799'],
        ['iPhone 15', 'Apple', '999'],
    ]),
    ('Price', 'desc', [
            ['Pixel 8', 'Google', '799'],
            ['Galaxy S23', 'Samsung', '899'],
            ['iPhone 15', 'Apple', '999'],
        ]),
])
def test_order_by_invalid_data(field, agg_value, response):
    result = order_by(table, field, agg_value)
    assert result == response


