from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Saloon(models.Model):
    title = models.CharField("Название салона", max_length=20)
    city = models.CharField("Город", max_length=20)
    address = models.CharField("Адрес", max_length=50)
    phonenumber = PhoneNumberField(
        'Номер телефона салона', max_length=20,
        blank=True, null=True, db_index=True
    )
    time_open = models.TimeField("Время открытия")
    time_close = models.TimeField("Время закрытия")

    class Meta:
        verbose_name = 'Салон'
        verbose_name_plural = 'Салоны'

    def __str__(self):
        return f"{self.title} - {self.address}"


class Master(models.Model):
    name = models.CharField('Имя мастера', max_length=15, blank=False)
    saloon = models.ForeignKey(
        Saloon, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='masters', verbose_name='В каком салоне')
    time_create = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.name


class Category(models.Model):
    CATEGORY_CHOICES = (
        ("Парикмахерские услуги", "Парикмахерские услуги"),
        ("Маникюр", "Маникюр"),
        ("Макияж", "Макияж"),
    )
    title = models.CharField(
        'Категория услуг', max_length=30, blank=False,
        choices=CATEGORY_CHOICES
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Service(models.Model):
    SERVICE_CHOICES = (
        ('Мужская стрижка', 'Мужская стрижка'),
        ('Женская стрижка', 'Женская стрижка'),
        ('Европейский маникюр', 'Европейский маникюр'),
        ('Аппаратный маникюр', 'Аппаратный маникюр'),
        ('Макияж стандарт', 'Макияж стандарт'),
        ('Свадебный макияж', 'Свадебный макияж')
    )
    title = models.CharField(
        'Наименование услуги', max_length=30, blank=False,
        choices=SERVICE_CHOICES
    )
    price = models.DecimalField(
        'Цена услуги', decimal_places=0, max_digits=5
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=False,
        related_name='masters', verbose_name='Из какой категории')
    masters = models.ManyToManyField(
        Master, related_name='services', verbose_name='Какой мастер'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.title


class Client(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        null=True, blank=True, related_name='clients'
    )
    tg_id = models.IntegerField('Telegram ID', unique=True)  # Добавлено поле для хранения tg_id
    name = models.CharField('Имя клиента', max_length=30)
    phonenumber = PhoneNumberField(
        'Номер телефона клиента', max_length=20,
        db_index=True
    )
    time_create = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name


class Appointment(models.Model):
    TIME_CHOICES = (
        ("10:00", "10:00"), ("10:30", "10:30"),
        ("11:00", "11:00"), ("11:30", "11:30"),
        ("12:00", "12:00"), ("12:30", "12:30"),
        ("13:00", "13:00"), ("13:30", "13:30"),
        ("14:00", "14:00"), ("14:30", "14:30"),
        ("15:00", "15:00"), ("15:30", "15:30"),
        ("16:00", "16:00"), ("16:30", "16:30"),
        ("17:00", "17:00"), ("17:30", "17:30"),
        ("18:00", "18:00"), ("18:30", "18:30"),
        ("19:00", "19:00"), ("19:30", "19:30"),
        ("20:00", "20:00"), ("20:30", "20:30")
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='appointments', verbose_name='Кто клиент'
    )
    master = models.ForeignKey(
        Master, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='appointments', verbose_name='К какому мастеру'
    )
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='appointments', verbose_name='Какая услуга'
    )
    appointment_date = models.DateField(
        'Дата визита', null=True,
    )
    appointment_time = models.CharField(
        'Время визита',  max_length=30,  db_index=True,
        choices=TIME_CHOICES
    )
    time_create = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись на услугу'
        verbose_name_plural = 'Записи на услуги'

    def __str__(self):
        return f"{self.appointment_time} - {self.client}"


class Feedback(models.Model):
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE,
        verbose_name='Посещение',
        related_name='feedbacks'
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Клиент'
    )
    feedback_text = models.TextField('Текст обратной связи')

    def __str__(self):
        return self.feedback_text

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Отзывы'
