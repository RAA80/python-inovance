#! /usr/bin/env python3

"""Реализация класса клиента для управления приводом переменного тока."""

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.pdu import ModbusResponse


class InovanceError(Exception):
    pass


class Client:
    """Класс клиента для управления приводом переменного тока."""

    def __init__(self, host: str, device: dict) -> None:
        """Инициализация класса клиента с указанными параметрами."""

        self.socket = ModbusTcpClient(host=host, retry_on_empty=True)
        self.socket.connect()

        self.device = device

    def __del__(self) -> None:
        """Закрытие соединения с устройством при удалении объекта."""

        if self.socket:
            self.socket.close()

    def __repr__(self) -> str:
        """Строковое представление объекта."""

        return f"{type(self).__name__}(socket={self.socket})"

    @staticmethod
    def _check_error(retcode: ModbusResponse) -> bool:
        """Проверка возвращаемого значения на ошибку."""

        if retcode.isError():
            raise InovanceError(retcode)
        return True

    def _check_name(self, name: str) -> dict:
        """Проверка названия параметра."""

        name = name.upper()
        if name not in self.device:
            msg = f"Unknown parameter '{name}'"
            raise InovanceError(msg)

        return self.device[name]

    def get_param(self, name: str) -> float:
        """Чтение данных из устройства."""

        dev = self._check_name(name)

        result = self.socket.read_holding_registers(address=dev["address"])
        self._check_error(result)

        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big)
        value = {"U16": decoder.decode_16bit_uint,
                 "I16": decoder.decode_16bit_int,
                }[dev["type"]]()
        return value if dev["divider"] == 1 else value / dev["divider"]

    def set_param(self, name: str, value: float) -> bool:
        """Запись данных в устройство."""

        dev = self._check_name(name)

        if value is None or value < dev["min"] or value > dev["max"]:
            msg = f"An '{name}' value of '{value}' is out of range"
            raise InovanceError(msg)

        value *= dev["divider"]

        builder = BinaryPayloadBuilder(None, Endian.Big)
        {"U16": builder.add_16bit_uint,
         "I16": builder.add_16bit_int,
        }[dev["type"]](int(value))

        result = self.socket.write_registers(address=dev["address"],
                                             values=builder.build(),
                                             skip_encode=True)
        return self._check_error(result)


__all__ = ["Client"]
