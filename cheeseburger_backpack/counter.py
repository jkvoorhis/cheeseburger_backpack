import datetime
import os
from collections import Counter

from slacker import Slacker

class Slack_Counter(object):
    def __init__(self, api_token=None):
        if not api_token:
            raise Exception('No Slack API token found.')
        self.slack_client = Slacker(api_token)
        self.channel_map = {}
        self.channel_histories = [] # List(Dict(channel_id, List(message_text)))
        self.word_list = []

    def _set_word_list(self, file_name='./cheeseburger_backpack/default_list/default_words.txt'):
        """"""
        print('loading word list')
        with open(file_name) as file:
            word_list = []
            for line in file:
                word_list.append(line.rstrip('\n'))

        self.word_list = word_list
        print word_list

    def _build_channel_map(self):
        resp = self.slack_client.channels.list(exclude_archived=1)
        channel_list = resp.body['channels']

        # # TODO put in way to get channels by name?
        # for channel in channel_list[:20]:
        #     self.channel_map[channel['id']] = channel['name']

        self.channel_map['C025Q1VPV'] = 'inane'

    def _set_channel_histories(self, weeks=None):
        oldest_timestamp = 0 # slack API's default value. gets entire history.
        now = datetime.datetime.utcnow()
        now_timestamp = (now - datetime.datetime(1970, 1, 1)).total_seconds()

        if weeks:
            oldest_dt = now - datetime.timedelta(weeks=weeks)
            oldest_timestamp = (
                oldest_dt - datetime.datetime(1970, 1, 1)
            ).total_seconds()

        for channel_id in self.channel_map.iterkeys():
            print('getting history for {0}\n'.format(self.channel_map[channel_id]))

            messages_text = []

            def get_history(oldest=oldest_timestamp, newest=now_timestamp):
                print 'getting history for old:{0}, new:{1}'.format(oldest, newest)
                resp = self.slack_client.channels.history(
                    channel_id,
                    oldest=oldest,
                    latest=newest
                )
                history = resp.body['messages']
                has_more = bool(resp.body['has_more'])
                for message in history:
                    messages_text.append(message['text'])

                if has_more:
                    get_history(newest=history[-1]['ts'])

            get_history()

            self.channel_histories.append(
                {channel_id: messages_text}
            )

    def count_words(self, weeks):
        if not self.channel_map:
            self._build_channel_map()
        if not self.channel_histories: # List(Dict(channel_id, List(message_text)))
            self._set_channel_histories(weeks)
        if not self.word_list:
            self._set_word_list()

        channel_results = {}
        channel_aggregate = {}
        master_counter = Counter()

        print('counting word usage')
        for channel_dict in self.channel_histories:
            for chan_id, messages in channel_dict.iteritems():
                cnt = Counter()
                # print(messages)
                message_blob = ' '.join(messages)
                message_list = message_blob.split()
                for word in message_list:
                    if word in self.word_list:
                        cnt[word] += 1
                channel_results[chan_id] = cnt

        print('aggregating counts')
        for chan_id, name in self.channel_map.iteritems():
            channel_aggregate[name] = sum(channel_results[chan_id].values())

        for counter in channel_results.itervalues():
            master_counter += counter

        return {
            'channel_aggregate': channel_aggregate,
            'word_aggregate': dict(master_counter)
        }
