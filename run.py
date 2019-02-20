from harvest.harvest import OAIRequest
import argparse


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

    args = parser.parse_args()
    harvest_records = True
    oai_set = ""
    if args.harvest_records.lower() == "false":
        harvest_records = False
    if args.oai_set:
        oai_set = args.oai_set
    request = OAIRequest(args.oai_endpoint, oai_set, args.metadata_format, harvest_records)
    request.list_records()
    print(f'This set currently has {request.bad_records} bad records.')
    return


if __name__ == "__main__":
    main()
