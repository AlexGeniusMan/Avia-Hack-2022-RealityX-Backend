from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given data
        """

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=email
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **kwargs):
        """
        Creates and saves a superUser with the given data
        """
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager()
    username = models.CharField('Username', blank=True, max_length=100)
    email = models.EmailField('Email', blank=False, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='User',
                             related_name='sessions', null=False)


class Metric(models.Model):
    name = models.CharField('Name', max_length=1000, blank=False)

    def __str__(self):
        return f"{self.name}"


class Prediction(models.Model):
    flight_phase = models.CharField('Flight phase', max_length=1000, blank=False)
    flight_datetime = models.DateTimeField('Flight datetime', blank=False)
    engine_id = models.CharField('Engine ID', max_length=1000, blank=False)
    session = models.ForeignKey(Session, on_delete=models.PROTECT, verbose_name='Session',
                                related_name='predictions', null=False)


class MetricValue(models.Model):
    value = models.FloatField('Value', null=True)
    metric_name = models.ForeignKey(Metric, on_delete=models.PROTECT, verbose_name='Metric name',
                                    related_name='metric_values', null=False)
    prediction = models.ForeignKey(Prediction, on_delete=models.PROTECT, verbose_name='Prediction',
                                   related_name='metric_values', null=False)
