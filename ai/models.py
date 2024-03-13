from django.db import models

# Create your models here.
class StatementInfo(models.Model):
    owner = models.CharField(max_length=100)
    portfolio_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.owner
    
class Holding(models.Model):
    owner = models.ForeignKey(StatementInfo, on_delete=models.CASCADE, related_name='holdings')

    name = models.CharField(max_length=100)
    price = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name