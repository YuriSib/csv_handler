Поддерживаемые команды


--file	        |path/to/file.csv	     |   Путь к CSV-файлу (обязательный)

--where 	    |поле(=/>/<)значение     |   Фильтрация по полю

--aggregate	    |поле=(avg/min/max)      |	 Выдает среднее арифм./минимальное/максимальное значение поля

--order_by      |поле=(asc/desc)         |   Сортирует поле по возрастанию или убыванию



Примеры

python script.py --file data.csv

python script.py --file products.csv --where "price<1000"

python script.py --file test.csv --aggregate "rating=avg"

python script.py --file data.csv --order_by "brand=asc"



Архитектура построена по принципу открытой расширяемости:
Все операции (where, aggregate, order_by) реализованы как отдельные функции.
Чтобы добавить новые команды (например, --group_by, --median) — просто:
Напишите новую функцию
Зарегистрируйте её в main и parse_args.
