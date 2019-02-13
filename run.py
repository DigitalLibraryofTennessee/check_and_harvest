from harvest.harvest import OAIRequest
import argparse


def main():
    parser = argparse.ArgumentParser(description="Download good OAI records only.")
    parser.add_argument(
        "-s",
        "--set",
        dest="oai_set",
        help="Specify your oai endpoint.",
        required=True
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

    args = parser.parse_args()
    request = OAIRequest(args.oai_endpoint, args.oai_set, args.metadata_format)
    request.list_records()
    print(f'This set currently has {request.bad_records} bad records.')
    return


if __name__ == "__main__":
    main()
