from django.db import models


class TissueExpression(models.Model):
	tissue= models.CharField(max_length=30)
