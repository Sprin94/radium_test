# Тестовое задание для компании Радиум

### Задача:
Напишите скрипт, асинхронно, в 3 одновременных задачи, скачивающий содержимое HEAD репозитория https://gitea.radium.group/radium/project-configuration во временную папку.
После выполнения всех асинхронных задач скрипт должен посчитать sha256 хэши от каждого файла.
Код должен проходить без замечаний проверку линтером wemake-python-styleguide. Конфигурация nitpick - https://gitea.radium.group/radium/project-configuration


### Запуск:
Создать виртуальное окружение:
```sh
python -m venv venv
```
------------------------
Активировать виртуальное окружение: <br />
Для Windows
```sh
.\venv\Scripts\activate
```
Для Linux
```linux
source venv/bin/activate
```
------------------------
Установить зависимости:
```sh
pip install -r requirements.txt
```
------------------------
