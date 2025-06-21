#!/usr/bin/env python3
"""
gyatt-shell.py

Interactive BLE shell using Bleak, with colorized output and a default characteristic.

Commands:
  scan [timeout]               – Scan for devices (default timeout=5s)
  connect <MAC or name>        – Connect to a device by address or name
  disconnect                   – Disconnect from current device
  services                     – List services & characteristics
  setchar <char-UUID>          – Set the default characteristic UUID
  unsetchar                    – Clear the default characteristic
  read [char-UUID]             – Read from given char or default if omitted
  write [char-UUID] <hex>      – Write hex to given char or default if omitted
  notify [char-UUID]           – Toggle notifications on given char or default if omitted
  help                         – Show this help
  exit                         – Quit the shell
"""
import asyncio
import sys
from bleak import BleakClient, BleakScanner
from colorama import init, Fore, Style

init(autoreset=True)
PROMPT = Fore.GREEN + "gyatt> " + Style.RESET_ALL

class BleShell:
    def __init__(self):
        self.client: BleakClient | None = None
        self.notify_handles = set()
        self.current_uuid: str | None = None

    def info(self, msg):    print(Fore.CYAN + msg + Style.RESET_ALL)
    def success(self, msg): print(Fore.GREEN + msg + Style.RESET_ALL)
    def error(self, msg):   print(Fore.RED + msg + Style.RESET_ALL)

    def resolve(self, token: str | None) -> str | None:
        """Use token if provided, otherwise use current_uuid."""
        return token or self.current_uuid

    async def scan(self, timeout: float = 5.0):
        self.info(f"Scanning for {timeout}s…")
        devices = await BleakScanner.discover(timeout=timeout)
        for d in devices:
            print(f"{Fore.YELLOW}{d.address}{Style.RESET_ALL}  {d.name or 'Unknown'}")
        self.success("Scan complete.\n")

    async def connect(self, identifier: str):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.info(f"Connecting to {identifier}…")
        try:
            self.client = BleakClient(identifier, adapter="hci0")
            await self.client.connect()
        except Exception:
            # fallback by name
            devices = await BleakScanner.discover(timeout=5.0)
            addr = next((d.address for d in devices if d.name and identifier in d.name), None)
            if not addr:
                self.error("Device not found.\n"); return
            self.client = BleakClient(addr, adapter="hci0")
            await self.client.connect()
        if self.client.is_connected:
            self.success("Connected.\n")
        else:
            self.error("Failed to connect.\n")

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.success("Disconnected.\n")
        self.client = None
        self.notify_handles.clear()

    async def services(self):
        if not self.client or not self.client.is_connected:
            self.error("Not connected.\n"); return
        svcs = await self.client.get_services()
        for svc in svcs:
            print(Fore.MAGENTA + f"[Service] {svc.uuid}" + Style.RESET_ALL)
            for ch in svc.characteristics:
                props = ",".join(ch.properties)
                print(f"  └─ {Fore.MAGENTA}[Char]{Style.RESET_ALL} {ch.uuid} ({props})")
        print()

    async def setchar(self, uuid: str):
        self.current_uuid = uuid
        self.success(f"Default characteristic set to {uuid}\n")

    async def unsetchar(self):
        self.current_uuid = None
        self.success("Default characteristic cleared\n")

    async def read(self, uuid: str | None):
        uuid = self.resolve(uuid)
        if not uuid:
            self.error("No characteristic specified or default set.\n"); return
        if not self.client or not self.client.is_connected:
            self.error("Not connected.\n"); return
        val = await self.client.read_gatt_char(uuid)
        self.success(f"Read {uuid}: {val.hex()}\n")

    async def write(self, uuid: str | None, data_hex: str | None):
        data = None
        # if only one arg, treat it as data and use default uuid
        if data_hex is None:
            # uuid argument was actually data
            data_hex = uuid
            uuid = None
        uuid = self.resolve(uuid)
        if not uuid or not data_hex:
            self.error("Usage: write [char-UUID] <hex>\n"); return
        if not self.client or not self.client.is_connected:
            self.error("Not connected.\n"); return
        await self.client.write_gatt_char(uuid, bytes.fromhex(data_hex))
        self.success(f"Wrote {data_hex} to {uuid}\n")

    def _notif_cb(self, sender, data):
        print(Fore.YELLOW + f"[Notification] {sender}: {bytes(data).hex()}" + Style.RESET_ALL)

    async def notify(self, uuid: str | None):
        uuid = self.resolve(uuid)
        if not uuid:
            self.error("No characteristic specified or default set.\n"); return
        if not self.client or not self.client.is_connected:
            self.error("Not connected.\n"); return
        if uuid in self.notify_handles:
            await self.client.stop_notify(uuid)
            self.notify_handles.remove(uuid)
            self.success(f"Stopped notifications on {uuid}\n")
        else:
            await self.client.start_notify(uuid, self._notif_cb)
            self.notify_handles.add(uuid)
            self.success(f"Started notifications on {uuid}\n")

    async def repl(self):
        self.info("Welcome to Gyatt BLE shell. Type `help` for commands.\n")
        loop = asyncio.get_event_loop()
        while True:
            try:
                line = await loop.run_in_executor(None, input, PROMPT)
            except (EOFError, KeyboardInterrupt):
                print(); break
            parts = line.strip().split()
            if not parts:
                continue
            cmd, *args = parts
            try:
                if cmd == 'scan':
                    await self.scan(float(args[0]) if args else 5.0)
                elif cmd == 'connect' and args:
                    await self.connect(args[0])
                elif cmd == 'disconnect':
                    await self.disconnect()
                elif cmd == 'services':
                    await self.services()
                elif cmd == 'setchar' and args:
                    await self.setchar(args[0])
                elif cmd == 'unsetchar':
                    await self.unsetchar()
                elif cmd == 'read':
                    await self.read(args[0] if args else None)
                elif cmd == 'write':
                    # args can be [uuid, data] or [data] if default
                    if len(args)==1:
                        await self.write(None, args[0])
                    else:
                        await self.write(args[0], args[1])
                elif cmd == 'notify':
                    await self.notify(args[0] if args else None)
                elif cmd in ('help','?'):
                    print(__doc__)
                elif cmd in ('exit','quit'):
                    self.info("Goodbye!"); break
                else:
                    self.error("Unknown command. Type `help`.\n")
            except Exception as e:
                self.error(f"Error: {e}\n")

        if self.client and self.client.is_connected:
            await self.client.disconnect()

async def main():
    shell = BleShell()
    await shell.repl()

if __name__ == '__main__':
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit(0)

