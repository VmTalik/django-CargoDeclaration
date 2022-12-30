from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class AdvUser(AbstractUser):
    """Класс - модель пользователя User с дополнительными данными о пользователе"""
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Активация пройдена?')
    send_messages = models.BooleanField(default=True, verbose_name='Высылать оповещения?')
    job_title = models.CharField(default='', max_length=25, verbose_name='Должность')
    phone_numberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(default='', validators=[phone_numberRegex], max_length=16, unique=True,
                                    verbose_name='Номер телефона')

    def delete(self, *args, **kwargs):
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Cargo(models.Model):
    cargo_type = models.CharField(max_length=45, verbose_name='Тип груза')

    class Meta:
        verbose_name_plural = 'Типы грузов'
        verbose_name = 'Тип груза'


class Status(models.Model):
    status = models.CharField(max_length=45, verbose_name='Статус декларации')

    class Meta:
        verbose_name_plural = 'Статусы декларации'
        verbose_name = 'Статус декларации'


class DeclarationLog(models.Model):
    formation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания декларации')
    responsible = models.CharField(max_length=150, verbose_name='Представитель')
    address_responsible = models.TextField(verbose_name='Адрес представителя')
    customs_value = models.DecimalField(max_digits=50, decimal_places=2, verbose_name='Таможенная стоимость')
    cargo_amount = models.IntegerField(verbose_name='Количество груза')
    net_weight = models.DecimalField(max_digits=50, decimal_places=2, verbose_name='Вес нетто')
    gross_weight = models.DecimalField(max_digits=50, decimal_places=2, verbose_name='Вес брутто')
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL, default=1, verbose_name='Статус')
    user_id = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    cargo_id = models.ForeignKey(Cargo, null=True, on_delete=models.SET_NULL, verbose_name='Вид груза')

    class Meta:
        verbose_name_plural = 'Декларации'
        verbose_name = 'Декларация'


class CargoReceiver(models.Model):
    receiver_name = models.CharField(max_length=65, verbose_name='Имя получателя')
    receiver_country = models.CharField(max_length=60, verbose_name='Страна получателя')
    receiver_locality = models.CharField(max_length=70, verbose_name='Населенный пункт получателя')
    receiver_postal_code = models.CharField(max_length=45, verbose_name='Почтовый индекс получателя')
    receiver_PSRN = models.IntegerField(verbose_name='ОГРН получателя')
    id = models.OneToOneField(DeclarationLog, on_delete=models.CASCADE, primary_key=True, auto_created=True, default=1)

    class Meta:
        verbose_name_plural = 'Получатели груза'
        verbose_name = 'Получатель груза'


class Consignor(models.Model):
    consignor_name = models.CharField(max_length=65, verbose_name='Имя отправителя')
    sending_country = models.CharField(max_length=60, verbose_name='Страна отправителя')
    sender_locality = models.CharField(max_length=70, verbose_name='Населенный пункт отправителя')
    sender_postal_code = models.CharField(max_length=45, verbose_name='Почтовый индекс отправителя')
    sender_PSRN = models.IntegerField(verbose_name='ОГРН отправителя')
    id = models.OneToOneField(DeclarationLog, on_delete=models.CASCADE, primary_key=True, auto_created=True, default=1)

    class Meta:
        verbose_name_plural = 'Отправители груза'
        verbose_name = 'Отправитель груза'


class Orientation(models.Model):
    validity_period = models.DateField(verbose_name='Срок действия')
    scope_orientation = models.TextField(verbose_name='Область действия(территориальная)')
    description_risk_area = models.TextField(verbose_name='Описание области риска')
    risk_indicators = models.CharField(max_length=130, verbose_name='Показатели индикаторов риска')

    class Meta:
        verbose_name_plural = 'Ориентировки'
        verbose_name = 'Ориентировки'


class Summary(models.Model):
    reg_number = models.IntegerField(verbose_name='Регистрационный номер')
    check_date = models.DateTimeField(verbose_name='Дата проверки')
    comment = models.TextField(verbose_name='Комментарий')
    address = models.TextField(verbose_name='Адрес', default='Ленинградский таможенный пост')
    decision = models.TextField(verbose_name='Решение инспектора')
    executor = models.CharField(max_length=150, verbose_name='ФИО инспектора')
    id = models.OneToOneField(DeclarationLog, on_delete=models.CASCADE, primary_key=True)
    orientation_id = models.ForeignKey(Orientation, null=True, on_delete=models.SET_NULL)

    status_id = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL)


class DeclarationLogArchive(models.Model):
    archive_date = models.DateTimeField(verbose_name='Дата ухода в архив')
    id = models.OneToOneField(Summary, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name_plural = 'Даты ухода в архив'
        verbose_name = 'Дата ухода в архив'
