import datetime

from slacker import Slacker

class Counter(object):
    def __init__(self, api_token=None):
        if not api_token:
            raise Exception('No Slack API token found.')
        self.slack_client = Slacker(api_token)
        self.channel_map = {}
        self.channel_histories = [] # List(Dict(channel_id, List(message_text)))

    def build_channel_map(self):
        resp = self.slack_client.channels.list(exclude_archived=1)
        channel_list = resp.body['channels']

        for channel in channel_list:
            self.channel_map[channel['id']] = channel['name']

    def set_channel_histories(self, weeks=None):
        oldest_timestamp = 0 # slack API's default value. gets entire history.
        if weeks:
            now =  datetime.datetime.utcnow()
            oldest_dt = now - datetime.timedelta(weeks=4)
            oldest_timestamp = (
                oldest_dt - datetime(1970, 1, 1)
            ).total_seconds()

        for channel_id in self.channel_map.iterkeys():
            resp = self.slack_client.channels.history(
                channel_id,
                oldest=oldest_timestamp
            )
            history = resp.body['messages']
            messages_text = [message['text'] for message in history]

            self.channel_histories.append(
                {channel_id: messages_text}
            )
