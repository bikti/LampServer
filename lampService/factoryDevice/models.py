from django.db import models

# Create your models here.
from django.db import models

class Device(models.Model):
    deviceName = models.CharField(max_length=200)
    deviceModel = models.CharField(max_length=100)