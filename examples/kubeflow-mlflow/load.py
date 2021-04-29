from argparse import ArgumentParser
from random import gauss
from time import sleep

from requests import Session


def main(classification):
    data = (
        [0.03, 0.0506801187398187, -0.002, -0.01, 0.04, 0.01, 0.08, -0.04, 0.005, -0.1]
        if not classification
        else [6.1, 2.8, 4.7, 1.2]
    )
    with Session() as s:
        for i in range(60):
            data[0] = gauss(6, 2) if classification else gauss(0, 0.05)
            resp = s.post("http://ml-server", json=data)
            resp.raise_for_status()
            if i % 10 == 0:
                print(f"response[{i}]: {resp.json()}")
            sleep(0.1)


if __name__ == "__main__":
    parser = ArgumentParser(description="Generate inference workload.")
    parser.add_argument("-c", "--classification", action="store_true")
    args = parser.parse_args()
    main(args.classification)
