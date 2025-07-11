from tabulate import tabulate
import csv
import argparse
import re
import sys
import os


def get_data_from_csv(filename):
    if not os.path.isfile(filename):
        return "По указанному пути csv документ не найден"

    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)

            table = []
            for row in reader:
                table.append(row)
            return table
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"


def type_definition(row_fields: list, row_values: list):
    """
    Функция для определения, какое из полей какому типу соответствует
    :param row_fields: список полей. Первая строка таблицы
    :param row_values: список значений. Вторая строка таблицы, соответствует значениям row_fields
    :return: словарь, где ключ это название поля, а значение - его тип
    """
    row_types = []
    for cell in row_values:
        try:
            float(cell)
        except ValueError:
            row_types.append(str)
        else:
            row_types.append(float) if '.' in cell else row_types.append(int)
    return dict(zip(row_fields, row_types))


def where(table: list, field, operator, value):
    """
        Функция фильтрации с операторами «больше», «меньше» и «равно»
        :param table: наша таблица в виде вложенного списка
        :param field: имя поля
        :param operator: > < или =
        :param value: значение, по которому будем фильтроваться
        :return: список, где на индексе поля стоит тип его значений
    """
    types_fields = type_definition(table[0], table[1])
    my_field_type = types_fields.get(field)

    if not my_field_type:
        return 'Указанного поля нет в таблице'
    elif operator not in [">", "<", "="]:
        return 'Некорректно указан оператор'
    elif my_field_type is str and operator != "=":
        return 'Нельзя применять операторы сравнения к строковым данным'

    try:
        if my_field_type is int and '.' in value:
            value = float(value)
        else:
            value = my_field_type(value)
    except ValueError:
        return f"Переданное значение не валидно. Не удалось привести его к типу {my_field_type}"

    field_idx = table[0].index(field)
    selected_rows = []

    if operator == '>':
        for row in table[1:]:
            if my_field_type(row[field_idx]) > value:
                selected_rows.append(row)
    elif operator == '<':
        for row in table[1:]:
            if my_field_type(row[field_idx]) < value:
                selected_rows.append(row)
    elif operator == '=':
        for row in table[1:]:
            if my_field_type(row[field_idx]) == value:
                selected_rows.append(row)

    return selected_rows


def aggregate(table: list, field, agg_value):
    """
        Функция фильтрации с операторами «больше», «меньше» и «равно»
        :param table: наша таблица в виде вложенного списка
        :param field: имя поля
        :param agg_value: аргумент агрегации среднего (avg), минимального (min) и максимального (max) значений
        :return: список, где на индексе поля стоит тип его значений
    """
    types_fields = type_definition(table[0], table[1])
    my_field_type = types_fields.get(field)

    if not my_field_type:
        return 'Указанного поля нет в таблице'
    elif my_field_type is str:
        return 'Агрегация доступна только для числовых полей'
    elif agg_value not in ["avg", "min", "max"]:
        return 'Некорректно указан аргумент агрегации'

    field_idx = table[0].index(field)

    field_values = [my_field_type(row[field_idx]) for row in table[1:]]

    aggregations = {
        'avg': lambda vals: sum(vals) / len(vals),
        'min': min,
        'max': max
    }
    result = [[aggregations[agg_value](field_values)]]

    return result


def order_by(table: list, field: str, agg_value: str):
    """
        Функция сортирующая вложенный список по одному из его индексов
        :param table: наша таблица в виде вложенного списка
        :param field: имя поля
        :param agg_value: аргумент сортировки по убыванию (asc) и возрастанию (desc)
        :return: отсортированный список
    """
    types_fields = type_definition(table[0], table[1])
    my_type = types_fields.get(field)

    flag_choice = {
        'asc': True,
        'desc': False
    }
    reverse_flag = flag_choice.get(agg_value)

    if reverse_flag is None:
        return 'Некорректное значение сортировки'

    if my_type:
        field_idx = table[0].index(field)
        sorted_table = sorted(table[1:], key=lambda x: my_type(x[field_idx]), reverse=reverse_flag)
        return sorted_table
    else:
        return 'Указанного поля нет в таблице'


def parse_args():
    """
        Функция распарсит аргументы, принятые консолью
        :return: словарь типа {'file': 'test.csv', 'where': ('brand', '=', 'apple'), 'aggregate': ['rating', 'min']}
    """

    args = sys.argv[1:]

    if args[0] != "--file":
        return "Обязательный аргумент '--file' не указан"
    if '.csv' not in args[1]:
        return "Не передан csv документ для обработки"
    if len(args) == 2:
        return "Не переданы аргументы действия"

    for idx, val in enumerate(args[2:], start=2):
        if idx % 2 != 0:
            if val.count("=") != 1:
                return f"Не корректное значение. {val}"
        else:
            if val not in ["--where", "--aggregate"]:
                return f"Не корректный флаг. {val}"

    parser = argparse.ArgumentParser(description="Обработчик csv файлов")
    parser.add_argument('--file', type=str, required=True, help='Путь к файлу')
    parser.add_argument('--where', type=str, help='Параметры фильтрации')
    parser.add_argument('--aggregate', type=str, help='Параметры агрегации')

    args = parser.parse_args()

    args_dict = vars(args)

    if args_dict['where']:
        where_args = re.match(r'(\w+)\s*([<>=])\s*(.+)', args_dict['where'])
        args_dict['where'] = where_args.groups()
    if args_dict['aggregate']:
        aggregate_args = args_dict['aggregate'].split('=')
        args_dict['aggregate'] = aggregate_args

    return args_dict


def main():
    args_dict = parse_args()

    if args_dict is str:
        return args_dict

    file = args_dict.pop('file')

    data_table = get_data_from_csv(file)
    if data_table is str:
        return data_table

    types_fields = type_definition(data_table[0], data_table[1])

    # список задач на обработку csv.
    tasks = [task for task in ['where', 'order_by', 'aggregate'] if args_dict.get(task)]

    methods = {
        'where': where,
        'order_by': order_by,
        'aggregate': aggregate,
    }

    result = []
    for task in tasks:
        args = args_dict[task]

        if not result:
            result = methods[task](data_table, *args)
        else:
            result = methods[task]([data_table[0]] + result, *args)

    return tabulate(result, headers=list(types_fields.keys()), tablefmt="grid")


if __name__ == "__main__":
    file = "test.csv"
    data_table = get_data_from_csv(file)
    aggregate(data_table, "rating", "avg")

    print(main())
