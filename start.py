import asyncio
import notch

import settings

from streamwave.streamwave import Streamwave
from streamwave.now_playing import NowPlaying

log = notch.make_log('rainwave-discord-streamer')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

clients: list[Streamwave] = [
    Streamwave(station) for station in settings.stations
]

now_playings = []

try:
    for client in clients:
        now_playing = NowPlaying(
            client,
            client.settings.sid,
            settings.rainwave_api_url,
            settings.rainwave_user_id,
            settings.rainwave_api_key,
        )
        now_playings.append(now_playing)
        loop.create_task(client.start(client.settings.discord_token))
        loop.create_task(now_playing.start())
    loop.run_forever()
except KeyboardInterrupt:
    for client in clients:
        try:
            loop.run_until_complete(client.close())
        except:
            pass
    for now_playing in now_playings:
        try:
            loop.run_until_complete(now_playing.close())
        except:
            pass
finally:
    loop.close()
