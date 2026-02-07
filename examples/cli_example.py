import argparse
import asyncio
import logging
import sys

from pyintesishome import IntesisHome, IntesisHomeLocal
from pyintesishome.const import (
    DEVICE_AIRCONWITHME,
    DEVICE_ANYWAIR,
    DEVICE_INTESISHOME,
    DEVICE_INTESISHOME_LOCAL,
)

_LOGGER = logging.getLogger("pyintesishome")


async def main(loop):
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description="Commands: mode fan temp zone")
    parser.add_argument(
        "--user",
        type=str,
        dest="user",
        help="username for user.intesishome.com",
        metavar="USER",
        default=None,
    )
    parser.add_argument(
        "--password",
        type=str,
        dest="password",
        help="password for user.intesishome.com",
        metavar="PASSWORD",
        default=None,
    )
    parser.add_argument(
        "--device",
        type=str,
        dest="device",
        help="Select API to connect to",
        choices=[
            DEVICE_INTESISHOME,
            DEVICE_AIRCONWITHME,
            DEVICE_ANYWAIR,
            DEVICE_INTESISHOME_LOCAL,
        ],
        default=DEVICE_INTESISHOME,
    )
    parser.add_argument(
        "--host",
        type=str,
        dest="host",
        help="Host IP or name when using device intesishome_local",
        metavar="HOST",
        default=None,
    )
    parser.add_argument(
        "cmd",
        nargs="*",
        help="Command to run (mode, fan, temp, zone)",
    )
    args = parser.parse_args()

    if (not args.user) or (not args.password):
        parser.print_help(sys.stderr)
        sys.exit(0)

    if args.device == DEVICE_INTESISHOME_LOCAL:
        controller = IntesisHomeLocal(
            args.host,
            args.user,
            args.password,
            loop=loop,
            device_type=args.device,
        )
    else:
        controller = IntesisHome(
            args.user,
            args.password,
            loop=loop,
            device_type=args.device,
        )
    await controller.connect()
    
    if args.cmd:
        cmd = args.cmd[0]
        dev_id = list(controller.get_devices().keys())[0]
        
        if cmd == "mode" and len(args.cmd) > 1:
            await controller.set_mode(dev_id, args.cmd[1])
        elif cmd == "fan" and len(args.cmd) > 1:
            await controller.set_fan_speed(dev_id, args.cmd[1])
        elif cmd == "temp" and len(args.cmd) > 1:
            await controller.set_temperature(dev_id, float(args.cmd[1]))
        elif cmd == "zone" and len(args.cmd) > 2:
            # Usage: zone <zone_num> <status>
            await controller.set_zone_status(dev_id, int(args.cmd[1]), args.cmd[2])
            
        # Wait a bit for update
        await asyncio.sleep(2)

    print(repr(controller.get_devices()))
    await controller.stop()


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(loop))
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
