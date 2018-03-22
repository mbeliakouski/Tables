from django.db import models


# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=35)
    address = models.CharField(max_length=100)


class Post(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    posted_by = models.CharField(max_length=50)


class Tax(models.Model):
    name = models.CharField(max_length=50)
    amount = models.FloatField()
    category = models.CharField(max_length=50)
    exp_description = models.CharField(max_length=100)
    pre_tax_amount = models.FloatField()
    tax_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)



