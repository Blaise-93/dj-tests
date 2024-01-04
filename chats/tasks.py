from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from chatterbot import ChatBot
import asyncio
from chatterbot.ext.django_chatterbot import settings

channel_layer = get_channel_layer()


@shared_task
async def get_response(channel_name, input_data):
    chatterbot = ChatBot(**settings.CHATTERBOT)
    response = chatterbot.get_response(input_data)
    response_data = response.serialize()

    # remember here is used to give Usewarning issue prior to using async await function
    # instead the previous async_to_sync func.
    await (channel_layer.send)(
        channel_name,
        {
            "type": "chat.message",
            "text": {"msg": response_data["text"], "source": "bot"},
        },
    )

    asyncio.run()


""" 
def some_sync_function():
    # some code
    asyncio.run(some_other_async_function())

"""
