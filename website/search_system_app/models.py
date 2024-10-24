from django.db import models
import json
# Create your models here.
class Documents(models.Model):
    doc_id = models.AutoField(primary_key=True)
    link = models.URLField()
    text = models.TextField()


class Keywords(models.Model):
    #keyword_id = models.AutoField(primary_key=True)
    doc_id = models.ForeignKey(Documents, on_delete=models.CASCADE)
    keywords= models.TextField()

    def set_data(self, data_dict):
        self.keyword = json.dumps(data_dict)

    def get_data(self):
        return json.loads(self.keyword)
    