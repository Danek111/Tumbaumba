from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255)
    fio = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(validators=[MinLengthValidator(3)], max_length=20, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'fio']

    def __str__(self):
        return self.email


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.IntegerField()


class Cart(models.Model):
    products = models.ManyToManyField("Product")
    user = models.ForeignKey("User", on_delete=models.CASCADE)


class Order(models.Model):
    products = models.ManyToManyField("Product")
    order_price = models.IntegerField(default=0)
    user = models.ForeignKey("User", on_delete=models.CASCADE)


