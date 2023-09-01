from tinkoff.invest import Client

TOKEN = 't.qAA92zgThHLAO6mNv_m9iydwxW1Na-gARgXdbsTnGfoOQmpXRT0YDrwIP4OOR8WCVPgPPJJ6Wh2e2goa_lQb7g'  # noqa: E501


def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query="SiU3")
        for i in r.instruments:
            print(f"\n{i}")


if __name__ == "__main__":
    main()
