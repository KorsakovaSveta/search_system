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
    
from django.db import models

class Translation(models.Model):
    source_text = models.TextField()
    translated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class WordDictionary(models.Model):
    source_word = models.CharField(max_length=100)
    translated_word = models.CharField(max_length=100)
    pos_tag = models.CharField(max_length=50)  # Part of speech
    frequency = models.IntegerField(default=1)
    grammar_info = models.TextField()

    class Meta:
        unique_together = ('source_word', 'translated_word')

        
class Word(models.Model):
    english_word = models.CharField(unique=True)
    russian_translation = models.CharField()
    pos_tag = models.CharField(max_length=50)  # Части речи (например, NOUN, VERB и т.д.)
    
    class Meta:
        indexes = [
            models.Index(fields=['english_word']),
        ]