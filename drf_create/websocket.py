import os
import tailer
import json
from django.conf import settings
from threading import Thread
import asyncio


async def tail_log(task_id, send):
    log_file_path = os.path.join(settings.DEPLOY_LOG_PATH, f'{task_id}_log')
    if os.path.exists(log_file_path):
        for line in tailer.follow(open(log_file_path)):
            await send({
                'type': 'websocket.send',
                'text': json.dumps(line)
            })
    else:
        await send({
            'type': 'websocket.send',
            'text': json.dumps(f'{log_file_path} not exist')
        })


async def log_consumer(scope, receive, send):

    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept',
                'text': json.dumps("waiting for task log...")
            })

        if event['type'] == 'websocket.receive':
            task_id = json.loads(event['text']).get('task_id', None)

            if not task_id:
                await send({
                    'type': 'websocket.send',
                    'text': json.dumps("task_id为空，请输入task_id")
                })

            t = Thread(target=asyncio.run, args=(tail_log(task_id, send),))
            t.start()

        if event['type'] == 'websocket.disconnect':
            await send({
                'type': 'websocket.close'
            })
            break
