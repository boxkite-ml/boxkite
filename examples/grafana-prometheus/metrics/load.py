from random import gauss
from time import sleep

from requests import Session


def main():
    data = [0.03, 0.0506801187398187, -0.002, -0.01, 0.04, 0.01, 0.08, -0.04, 0.005, -0.1]
    with Session() as s:
        for i in range(60):
            data[0] = gauss(0, 0.05)
            resp = s.post("http://localhost:5000", json=data)
            resp.raise_for_status()
            if i % 10 == 0:
                print(f"response[{i}]: {resp.json()}")
            sleep(0.1)


if __name__ == "__main__":
    main()
