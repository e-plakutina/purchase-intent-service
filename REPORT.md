# Отчет о выполнении проекта

## pytest

![img.png](img.png)

## SELECT из логов

![img_1.png](img_1.png)

## get pods

![img_2.png](img_2.png)

## ответ predict через port-forward

![img_3.png](img_3.png)

![img_4.png](img_4.png)

## скрин k9s

![img_5.png](img_5.png)

## журнал проблем

### проблема 1 - в запросе параметр приходит как bool, а модель обучалась на int (0/1)
![img_6.png](img_6.png)

РЕШЕНИЕ: Починилось путем добавления в predict (в app.py) cast bool -> int
