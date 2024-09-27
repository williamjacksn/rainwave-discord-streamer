class StationSettings:
    discord_token: str
    audio_source: str
    audio_channel: int
    sid: int

    def __init__(self, discord_token: str, audio_source: str, audio_channel: int, sid: int):
        self.discord_token = discord_token
        self.audio_source = audio_source
        self.audio_channel = audio_channel
        self.sid = sid
