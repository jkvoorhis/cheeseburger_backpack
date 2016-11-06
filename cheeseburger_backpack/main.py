import click
import json

from counter import Slack_Counter

@click.command()
@click.option('--api_token', default=None, type=str,
              help='Your Slack API token as a String')
@click.option('--weeks', default=None, type=int,
              help='Weeks of history you would like to pull as int')
@click.option('--json_encode', default=False, type=bool,
              help='Boolean indicating result should be returned as JSON')
def run(api_token, weeks, json_encode):
    """ """
    slack_counter = Slack_Counter(api_token)

    counts = slack_counter.count_words(weeks)

    print json.dumps(counts)

if __name__ == "__main__":
    run()
