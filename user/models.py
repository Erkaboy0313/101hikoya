from django.db import models
from .managers import WriterManager,UserManager,ReaderManager,AdminManager
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    class UserRole(models.TextChoices):
        ADMIN = 'admin'
        READER = 'reader'

    class Gender(models.TextChoices):
        MALE = 'male'
        FEMALE = "female"

    role = models.CharField(max_length=10,default=UserRole.READER,choices=UserRole.choices)
    phone = models.CharField(max_length = 20, blank=True, null=True)
    gender = models.CharField(max_length = 6, choices = Gender.choices, blank=True,null=True)
    birth_date = models.DateField(blank=True, null=True)

    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

class Reader(CustomUser):
    objects = ReaderManager()

    class Meta:
        proxy = True


class Admin(CustomUser):
    objects = AdminManager()

    class Meta:
        proxy = True



class Role(models.Model):
    role = models.CharField(max_length = 30)

    def __str__(self):
        return self.role

# Create your models here.
class Writer(models.Model):
    first_name = models.CharField(max_length = 150)
    last_name = models.CharField(max_length = 150)
    image = models.ImageField(upload_to='Writers/',blank=True,null=True)
    bio = models.TextField(blank=True, null=True)
    title = models.CharField(max_length = 60, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    role = models.ManyToManyField(Role,blank=True)

    objects = models.Manager()
    filter = WriterManager()

    @property
    async def imageURL(self):
        if self.image:
            return self.image.url
        else:
            return ''

    @property
    async def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} | {self.last_name}"

