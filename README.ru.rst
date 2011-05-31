**************
Django-catalog
**************

Это приложение создано для того, чтобы организовывать объекты в древовидной структуре.

============
Установка
============


1. Загрузить
`````````````
В настоящее время стабильного релиза ``Django-catalog`` нет, но вы можете загрузить разрабатываемую версию с репозитория на github ::

    pip install -e git://github.com/redsolution/django-catalog.git@2.0.0#egg=Django-catalog

2. Подключить приложение
`````````````````````````
Чтобы подключить установленный ``Django-catalog`` добавьте в ваш файл настроек проекта ``settings.py`` следующее содержимое ::

    INSTALLED_APPS += [
        'catalog',
        'catalog.contrib.defaults',
    ]

3. Подключить URLs приложения
``````````````````````````````
Добавьте URL приложения ``Django-catalog`` в ``urls.py`` вашего проекта 

Чтобы использовать схему доступа к элементам дерева по ``slug`` ::

    urlpatterns += patterns('',
        (r'^catalog/', include('catalog.urls.by_slug')),
    )

Чтобы использовать схему доступа к элементам дерева по их ``id`` ::

    urlpatterns += patterns('',
        (r'^catalog/', include('catalog.urls.by_id')),
    )

4. Создание моделей
`````````````````````
Для того, чтобы использовать каталог необходимо создать для него модели. Ранее в INSTALLED_APPS мы подключили приложение каталога реализующее базовые модели и методы работы с ними. На данном этапе, чтобы убедиться в работоспособности каталога, нам этого достаточно. Запускаем синхронизации базы данных чтобы создать стандартные модели каталога ::

    python manage.py syncdb

5. Административный интерфейс
```````````````````````````````
Для того, чтобы заполнить каталог категориями и товарами зайдите в административный интерфейс ``Django`` и выберите ``Manage catalog``.

6. Использование шаблонов
``````````````````````````
``Django-catalog`` уже поставляется с готовыми для работы шаблонами, которых должно хватить для начала использования каталога.

================================
7. Использование своих моделей
================================

Если вам не хватает каких-то полей стандартного каталога и вы хотите их добавить, то самое время переопределить базовые модели каталога. Для этого давайте создадим расширенную версию ``Django-catalog`` внутри вашего проекта ::

    python manage.py startapp catalog_extended

и подключим его в файле настроек проекта ``settings.py`` добавив в конец файла ::

    INSTALLED_APPS += ['catalog_extended']

Теперь в ``catalog_extended/models.py`` вы можете создать свои модели наследуемые от базовой модели ``django-catalog``. Вот пример моделей с отсутствующим полем ``description`` для секции и дополнительным полем ``box_size`` для элемента каталога ::

    from catalog.base import CatalogBase
    from django.db import models
    from django.db.models import permalink


    class Common(CatalogBase):
        class Meta:
            abstract = True

        name = models.CharField()
        slug = models.SlugField(max_length=200, unique=True)

        def __unicode__(self):
            return self.name

        @permalink
        def get_absolute_url(self):
            return ('catalog-by-slug', (str(self.__class__.__name__.lower()), str(self.slug)))


    class Section(Common, models.Model):
        leaf = False

    
    class Item(Common, models.Model):
        name = models.CharField(max_length=200)
        description = models.TextField(null=True, blank=True)
        box_size = models.CharField(null=True, blank=True)

        leaf = True


После написания своих моделей необходимо подключить их в файле ``settings.py`` вашего проекта ::

    CATALOG_MODELS = [
        ('catalog_extended', 'Section'),
        ('catalog_extended', 'Item')
    ]

и выполняем синхронизацию проекта ::

    python manage.py syncdb

==============================
Использование своих шаблонов
==============================
