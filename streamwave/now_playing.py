import json
import logging
import websockets.asyncio.client

from discord import Activity, ActivityType

log = logging.getLogger(__name__)

MAX_LENGTH = 127


class NowPlaying:
    def __init__(
        self, client, sid, rainwave_api_url, rainwave_user_id, rainwave_api_key
    ):
        self.ws = None
        self.client = client
        self.sid = sid
        self.rainwave_api_url = rainwave_api_url
        self.rainwave_user_id = rainwave_user_id
        self.rainwave_api_key = rainwave_api_key

    @staticmethod
    def format_song(rw_event):
        prefix = ''
        if rw_event['type'] == 'OneUp':
            prefix = f'\U0001F31F PH: {rw_event['name']} \U0001F3B5 '
        elif rw_event['type'] == 'PVPElection':
            prefix = '\U0001F94A PVP \U0001F3B5 '

        song = rw_event['songs'][0]
        album = song['albums'][0]['name']
        title = song['title']
        artist = ', '.join(artist['name'] for artist in song['artists'])

        result = f'{prefix}{album} \U0001F4C2 {title} \U0001F58C {artist}'
        return result[:MAX_LENGTH]

    # Function to be run in its own thread so that each bot can update its own status to the currently playing song, album, and artist
    async def start(self):
        log.debug(f'Connecting to Rainwave API for sid {self.sid}')
        async for ws in websockets.asyncio.client.connect(f'{self.rainwave_api_url}{self.sid}'):
            try:
                self.ws = ws
                log.debug('Authorizing with Rainwave API')
                await ws.send(
                    json.dumps(
                        {
                            'action': 'auth',
                            'user_id': self.rainwave_user_id,
                            'key': self.rainwave_api_key,
                        }
                    )
                )

                async for message in ws:
                    data = json.loads(message)
                    if 'sched_current' in data:
                        formatted_song = self.format_song(data['sched_current'])
                        log.debug(f'Updating song [sid {self.sid}]: {formatted_song}')
                        now_play = Activity(type=ActivityType.listening, name=formatted_song,)
                        if self.client.ws:
                            await self.client.change_presence(activity=now_play)
                    if 'wserror' in data:
                        log.error(f'Failed validation to Rainwave API. {message}')
                        raise RuntimeError('Bad user ID/API key')
                    if 'wsok' in data:
                        log.info('Connected to Rainwave API.')
                        await ws.send(
                            json.dumps({'action': 'check_sched_current_id', 'sched_id': 1, })
                        )
                    if 'error' in data:
                        log.error(message)

            except websockets.ConnectionClosed as err:
                log.error(f'Error connecting to Rainwave: {err}')
                continue
            except ConnectionResetError as err:
                log.error(f'Connection reset: {err}')
                continue

    async def close(self):
        if self.ws:
            await self.ws.close()
