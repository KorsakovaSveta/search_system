from django.db import models

# Create your models here.
class Documents(models.Model):
    doc_id = models.AutoField(primary_key=True)
    link = models.URLField()

class Keywords(models.Model):
    #keyword_id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=500, unique=True)
    doc_id = models.ForeignKey(Documents, on_delete=models.CASCADE)
    weight = models.FloatField()