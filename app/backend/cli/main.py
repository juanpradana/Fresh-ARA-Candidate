import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--date")
    args = parser.parse_args()
    print(args.command, args.date)


if __name__ == "__main__":
    main()
