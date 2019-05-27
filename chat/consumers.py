from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message
class ChatConsumer(AsyncWebsocketConsumer):
	async def fetch_messages(self,data):
		messages=Message.objects.order_by('-time').all()[:10]
		content={
			'messages':self.messages_to_json(messages),
			'command':'messages'
		}
		await self.send_message(content)
	async def new_message(self,data):
		author=data['from']
		author_user=User.objects.filter(username=author).first()
		message=Message.objects.create(
			user=author_user,
			content=data['message']
			)
		content={
			'command':'new_message',
			'message':self.message_to_json(message)
		}
		await self.send_chat_message(content)
	def messages_to_json(self,messages):
		result=[]
		for m in messages:
			result.append(self.message_to_json(m))
		result.reverse()
		return result
	def message_to_json(self,message):
		return {
			'author':message.user.username,
			'content':message.content,
			'time':str(message.time),
		}
	commands={
		'fetch_messages':fetch_messages,
		'new_message': new_message,
	}
	async def connect(self):
		self.room_name=self.scope['url_route']['kwargs']['room_name']
		self.room_group_name=f'chat_{self.room_name}'

		await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)
		await self.accept()
	async def disconnect(self,close_code):
		await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)
	async def receive(self,text_data):
		data=json.loads(text_data)
		await self.commands[data['command']](self,data)

	async def send_chat_message(self,message):
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type':'chat_message',
				'message':message
			}
			)
	async def send_message(self,message):
		await self.send(text_data=json.dumps(message))
	async def chat_message(self,event):
		message=event['message']
		await self.send(text_data=json.dumps(message)) 