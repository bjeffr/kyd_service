from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


# Create your models here.
class User(AbstractUser):
    username = models.CharField(primary_key=True, max_length=42, validators=[MinLengthValidator(42)])
    contract = models.CharField(max_length=42, validators=[MinLengthValidator(42)])
    birth_date = models.DateField()
    mobile_number = models.CharField(max_length=20)
    REQUIRED_FIELDS = ['contract', 'birth_date', 'mobile_number']


class Address(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    street = models.CharField(max_length=150)
    postal_code = models.CharField(max_length=12)
    city = models.CharField(max_length=150)
    country = models.CharField(max_length=3, validators=[MinLengthValidator(3)])
    REQUIRED_FIELDS = ['street', 'postal_code', 'city', 'country']


class Device(models.Model):
    id = models.CharField(primary_key=True, max_length=10, validators=[MinLengthValidator(10)])
    name = models.CharField(blank=True, max_length=255)
    model = models.CharField(max_length=128)
    key = models.CharField(max_length=64, validators=[MinLengthValidator(64)])
    helper = models.TextField()
    account = models.CharField(blank=True, max_length=42)
    contract = models.CharField(blank=True, max_length=42)
    REQUIRED_FIELDS = ['model', 'key', 'helper']
