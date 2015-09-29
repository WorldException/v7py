# v7py
## Модули python для работы с 1С 7.7 напрямую (windows/linux)
Для генерации запросов используется 1Cv7.md и 1Cv7.dba (параметры подключения)
Чтение конфигурации идет напрямую без OLE, что позволяет использовать эту библиотеку на linux

### Возможности:
+ Обновление метаданных из сетевой папки
+ Разбор метаданных в структуру
+ Возможность выполнять прямые запросы с метаподстановками
+ Чтение 1Cv7.DBA
- Генерация моделей SqlAlchemy (в разработке)
+ Доступны справочники, документы, строки документов, регистры, журнал, перечисления

Библиотека используется в рабочем проекте и дорабатывается при наличии времени.

$ - Означает что надо искать метаданные для подстановки
\# - означает таблица строк документа или реквизит табличной части
case t.#Статус $Перечисление.СтатусыЗаказа.case Статус позволяет получить строковое представление перечисления

## Пример использования


    from v7 import db_work
    
    q = db_work.db.query(u"""
        select top 10
          d.НаСайт НаСайт,
          ж.НомерДок НомерДок,
          ж.ДатаДок ДатаДок,
          case t.#Статус $Перечисление.СтатусыЗаказа.case Статус,
          h.Наименование Характеристика,
          t.#КоличествоВБазе ВБазе,
          t.#КоличествоНаСайте НаСайте,
          t.#ОжидаемаяДата Ожидаем
        from $Документ.Уведомление d
        join $Документ.#Уведомление t on d.Код=t.iddoc
        join $Справочник.ХарактеристикиНоменклатуры h on t.#ХарактеристикаТовара = h.id
        join $Журнал ж on ж.IDDOC = d.Код
        where ж.ДатаДок between %(start)s and %(end)s
        and ж.ВидДокумента = d.ВидДокумента
        """)
    q.set_param('start', start_date)
    q.set_param('end', end_date, True)
    
    print unicode(q)  # вывод преобразованного SQL запроса
    items = q()  # выполнение запроса
    for i in items:
        print i[1]
        

    
Скоро добавлю еще код для запуска 1С в Celery с обработчиками в классах 1С++

=======

Евгений Стоянов 
quick.es@gmail.com 
skype:quick.2008
