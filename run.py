from dltnchecker.harvest import OAIChecker
import argparse
from repox.repox import Repox
import yaml


def create_config():
    config = {}
    print("\nYikes!  Looks like you're missing a config, so we can't read data from Repox.\n")
    config['username'] = input("\t1. What's your Repox username?  ")
    config['password'] = input("\t2. What's your Repox password?  ")
    config['repox'] = input("\t3. What's the base URL of your Repox instance?  ")
    print("\n")
    with open('config.yml', 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
    return


def main():
    parser = argparse.ArgumentParser(description="Check and Harvest if OAI records meet our requirements.")
    parser.add_argument(
        "-s",
        "--set",
        dest="oai_set",
        help="Specify your oai endpoint.",
        required=False
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        dest="oai_endpoint",
        help="Specify your oai endpoint.",
        required=True
    )
    parser.add_argument(
        "-m",
        "--metadata_format",
        dest="metadata_format",
        help="Specify your metadata formant",
        required=True
    )
    parser.add_argument(
        '-H',
        '--harvest_records',
        dest='harvest_records',
        help="Specify whether to harvest files or not. Defaults to True",
        required=False,
        default="True"
    )
    parser.add_argument(
        '-p',
        '--harvest_provider',
        dest='provider',
        help="Harvest all sets from provider",
        required=False
    )

    args = parser.parse_args()
    harvest_records = True
    oai_set = ""
    if args.harvest_records.lower() == "false":
        harvest_records = False
    if args.oai_set:
        oai_set = args.oai_set
    if args.provider:
        try:
            settings = yaml.safe_load(open('config.yml', 'r'))
        except FileNotFoundError:
            create_config()
            settings = yaml.safe_load(open('config.yml', 'r'))
        sets = Repox(
            settings['repox'], settings['username'], settings['password']
        ).get_list_of_sets_from_provider(
            args.provider
        )
        for dataset in sets:
            request = OAIChecker(args.oai_endpoint, dataset, args.metadata_format, harvest_records)
            request.list_records()
            print(f'{dataset} currently has {request.bad_records} bad records.')
    else:
        request = OAIChecker(args.oai_endpoint, oai_set, args.metadata_format, harvest_records)
        request.list_records()
        print(f'This set currently has {request.bad_records} bad records.')
    return


if __name__ == "__main__":
    main()
