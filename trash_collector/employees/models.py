from django.db import models

# Create your models here.

# TODO: Create an Employee model with properties required by the user stories

class Employee(models.Model):
    user = models.ForeignKey('accounts.User', blank=True, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    zip_code = models.IntegerField()

    def __str__(self):
        return self.first_name + " " + self.last_name
