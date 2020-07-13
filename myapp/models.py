from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Country(models.Model):
    cid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300, verbose_name='страна')

    def __str__(self):
        return self.name


class Hot_guest(models.Model):
    VIZA_TYPE = (
        ('sp', 'SP'),
        ('bs', 'BS'),
        ('of', 'OF'),
        ('wp', 'WP'),
        ('pr', 'PR'),
        ('dp', 'DP'),
        ('nn', 'NO NEED')
    )
    M_F = (
        ('female', 'FEMALE'),
        ('male', 'MALE')
    )
    gid = models.AutoField(primary_key=True)
    passportnum = models.CharField(max_length=25, unique=True, verbose_name='№ паспорта')
    surname = models.CharField(max_length=100, verbose_name='фамилия')
    name = models.CharField(max_length=50, verbose_name='имя')
    fk_cid = models.ForeignKey(Country, db_index=True, on_delete=models.CASCADE, verbose_name='страна')
    birthdate = models.DateField(verbose_name='дата рождения')
    gender = models.CharField(max_length=8, choices=M_F, default='female', verbose_name='пол')
    typeofvisa = models.CharField(max_length=10, choices=VIZA_TYPE, default='nn', verbose_name='тип визы')
    company = models.CharField(max_length=50, verbose_name='компания')
    active = models.BooleanField(default=True, verbose_name='active')

    def __str__(self):
        return f'{self.surname} {self.name}'


class Hot_room(models.Model):
    TYPE_CHOICES = (
        ('', ''),
        ('DLT', 'DL Tween'),
        ('DLK', 'DL King'),
        ('EXS', 'EXS'),
        ('JST', 'JST'),
        ('PS', 'PS'),
        ('TRP', 'Triple'),
        ('DIS', 'DISABLE')
    )
    COLOR_CHOICES = (
        ('dff0d8', 'Nut'),
        ('fcf8e3', 'Wood'),
        ('f2dede', 'Pink'),
        ('5cb85c', 'Green'),
        ('ffffff', 'White')
    )
    STATUS_CHOICES = (
        ('repair', 'ремонт'),
        ('free', 'свободный'),
        ('busy', 'занятый'),
        ('dirty', 'грязный')
    )
    rid = models.AutoField(primary_key=True)
    roomnum = models.PositiveSmallIntegerField(unique=True, verbose_name='номер комнаты')
    roomtype = models.CharField(max_length=8, choices=TYPE_CHOICES, default='', verbose_name='тип комнаты')
    floor = models.PositiveSmallIntegerField(verbose_name='этаж')
    orderby = models.PositiveSmallIntegerField(verbose_name='расположение комнат')
    view = models.CharField(max_length=50, verbose_name='обзор')
    colored = models.CharField(max_length=10, choices=COLOR_CHOICES, default='dff0d8', verbose_name='цвет')
    reserved = models.DateField(verbose_name='дата резервирования')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='состояние')
    remark = models.CharField(max_length=300, verbose_name='примечание')

    def __str__(self):
        return "{0}".format(self.roomnum)


class Hot_book(models.Model):
    PAY_METHOD = (
        ('cash', 'CASH'),
        ('visa', 'VISA'),
        ('cl', 'CL'),
        ('poa', 'POA'),
        ('all_cl', 'All Cl')
    )
    CURRENCY = (
        ('usd', 'USD'),
        ('dtm', 'DTM')
    )
    bid = models.AutoField(primary_key=True)
    fk_gid = models.ForeignKey(Hot_guest, db_index=True, on_delete=models.CASCADE, verbose_name='постоялец')
    fk_rid = models.ForeignKey(Hot_room, db_index=True, on_delete=models.CASCADE, verbose_name='номер комнаты')
    arrdate = models.DateTimeField(verbose_name='дата прибытия')
    depdate = models.DateTimeField(verbose_name='дата убытия')
    paymethod = models.PositiveSmallIntegerField(verbose_name='сумма оплаты')
    payrate = models.CharField(max_length=8, choices=PAY_METHOD, default='cash', verbose_name='оплата')
    currency = models.CharField(max_length=4, choices=CURRENCY, default='usd', verbose_name='курс оплаты')
    active = models.BooleanField(default=True, verbose_name='')

    def __str__(self):
        return "{0}".format(self.fk_rid)