from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Message(models.Model):
	user=models.ForeignKey(User,related_name='user_messages',on_delete=models.CASCADE)
	content=models.TextField()
	time=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.user} message'
		