import os
from tinkoff.invest import Client

TOKEN = os.getenv('TOKEN')


def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query="SiU3")
        for i in r.instruments:
            print(f"\n{i}")


if __name__ == "__main__":
    main()
