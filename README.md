# I. Запуск контейнера.

## 1. Уапоковка образа
`docker build -t cbr-hw-dockerization .`

## 2. Запук контейнера
`docker run -t -i -p 5000:5000 cbr-hw-dockerization`

# II. Замечание по работе проекта.
Иногда сайт Росстата не отвечает и проект выдает ошибку (отсутствие ответа от сервера). В таких случаях нужно запустить проект ещё раз, если сайт не лежит, то код отработает.

# III. Состав проекта:
1. requirements.txt - файл со списком необходимых пакетов и версий для проекта
2. func.py - файл со вспомогательными функциями загрузки и обработки данных
3. plot.py - файл с функцией прогноза и построение графика ИПЦ
4. app.py - файл со скриптом запуска сайта через flask
5. Dockerfile - файл с командой запуска докера
6. templates/ipc_fcs.html - файл с HTML кодом web страницы
7. static/images/plot.png - сохраненный файл после отработки app.py
8. research/ipc_research.py - файл с небольшим исследованием данных
9. 
