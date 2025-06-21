# GYATT — Interactive BLE Shell

![GYATT Icon PNG](gyatt.png "GYATT Level 10")

**GYATT** (pronounced “gee-yat”) is a Python3-based interactive shell for exploring and interacting with Bluetooth Low Energy (BLE) devices via the [Bleak](https://github.com/hbldh/bleak) library. It supports scanning, connecting, listing services, reading/writing characteristics, and toggling notifications—all with colorized output.

---

## Requirements

- Python 3.7+  
- [`bleak`](https://pypi.org/project/bleak/)  
- [`colorama`](https://pypi.org/project/colorama/)  
- A Linux host with a working BLE adapter (`hci0`) and proper permissions (run as root or via `sudo`).

Install dependencies with:

```bash
pip3 install bleak colorama
```

---

## Installation

1. Save `gyatt.py` to your machine.  
2. Make it executable:
   ```bash
   chmod +x gyatt.py
   ```
3. Run it with Python 3:
   ```bash
   sudo ./gyatt.py
   ```

---

## Quick Start

Launch GYATT:

```bash
sudo ./gyatt.py
```

You will see a prompt:

```
gyatt> 
```

Type `help` to display the built-in documentation and command list.

---

## Commands

| Command                         | Description                                                                         |
|---------------------------------|-------------------------------------------------------------------------------------|
| `scan [timeout]`                | Discover nearby BLE devices (default `timeout=5.0` seconds).                       |
| `connect <MAC or name>`         | Connect by device MAC address (e.g. `AA:BB:CC:DD:EE:FF`) or by matching name.      |
| `disconnect`                    | Disconnect from the current device.                                                |
| `services`                      | List all GATT services and characteristics.                                        |
| `setchar <char-UUID>`           | Set a “default” characteristic UUID for subsequent read/write/notify commands.     |
| `unsetchar`                     | Clear the default characteristic.                                                  |
| `read [char-UUID]`              | Read from the given characteristic UUID, or the default if omitted.                |
| `write [char-UUID] <hex>`       | Write raw hex data to the given or default characteristic.                         |
| `notify [char-UUID]`            | Toggle notifications on the given or default characteristic.                       |
| `help` or `?`                   | Show this help documentation.                                                      |
| `exit` or `quit`                | Quit GYATT.                                                                        |

---

## Examples

1. **Scan for devices**  
   ```bash
   gyatt> scan
   ```

2. **Connect to a device by MAC**  
   ```bash
   gyatt> connect 9C:F1:D4:40:08:13
   ```

3. **List services & characteristics**  
   ```bash
   gyatt> services
   ```
   ```
   [Service] 00001801-0000-1000-8000-00805f9b34fb
     └─ [Char] 00002a05-0000-1000-8000-00805f9b34fb (indicate)
   [Service] 00005001-84af-12c1-4cc4-6b8f83431727
     └─ [Char] 00005002-84af-12c1-4cc4-6b8f83431727 (read,write,notify,indicate)
   ```

4. **Set a default characteristic**  
   ```bash
   gyatt> setchar 00005002-84af-12c1-4cc4-6b8f83431727
   ```

5. **Read from the default characteristic**  
   ```bash
   gyatt> read
   ```
   ```
   Read 00005002-84af-12c1-4cc4-6b8f83431727: 0a0b0c
   ```

6. **Write to the default characteristic**  
   ```bash
   gyatt> write a1b2c3
   ```
   ```
   Wrote a1b2c3 to 00005002-84af-12c1-4cc4-6b8f83431727
   ```

7. **Toggle notifications**  
   ```bash
   gyatt> notify
   ```
   ```
   Started notifications on 00005002-84af-12c1-4cc4-6b8f83431727
   [Notification] 00005002-84af-12c1-4cc4-6b8f83431727: deadbeef
   ```

8. **Disconnect and exit**  
   ```bash
   gyatt> disconnect
   gyatt> exit
   ```

---

## Tips

- If connecting by device name, ensure your name substring is unique.  
- Use `setchar` to avoid typing the full UUID every time.  
- BLE permissions on Linux may require running as `root` or adding your user to the `bluetooth` group.
