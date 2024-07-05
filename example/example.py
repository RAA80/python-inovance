#! /usr/bin/env python3

"""Проверка работы всех функций."""

from time import sleep

from inovance.client import Client
from inovance.device import MD520

if __name__ == "__main__":
    client = Client(host="192.168.0.201", device=MD520)
    print(client)

    value = client.get_param(name="U3-17")  # Остальные названия параметров в файле 'device.py'
    print(f"U3-17 = {value}")

    # MD500-EN1 User Guide
    result = client.set_param(name="U3-17", value=1)    # направление: 0 - стоп, 1 - вперед, 2 - назад
    print(f"U3-17 = {result}")

    result = client.set_param(name="U3-16", value=10)   # частота Гц
    print(f"U3-16 = {result}")

    sleep(10)

    result = client.set_param(name="U3-17", value=0)
    print(f"U3-17 = {result}")
