"""Export the Eversweet fountain's drinking history from the Petkit cloud.

Run it yourself (it asks for your Petkit e-mail and password; nothing is stored):

    uv run --with pypetkitapi==1.31.1 python tools/petkit_fountain_history.py

It writes fountain_history.json next to this script: the raw daily work records the
Petkit app keeps for the fountain, plus a list of drinking sessions parsed from them.
The file contains no credentials. Send it back so it can be imported into Home
Assistant's statistics.
"""
from __future__ import annotations

import asyncio
import getpass
import json
import sys
from datetime import date, datetime, timedelta
from http import HTTPMethod
from pathlib import Path

import aiohttp
from pypetkitapi.client import PetKitClient

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90
OUT = Path(__file__).with_name("fountain_history.json")


def sessions_from(records: list) -> list[dict]:
    """Pull (start, in, out) drinking sessions out of the work records, defensively."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            t_in, t_out = node.get("timeIn"), node.get("timeOut")
            if isinstance(t_in, (int, float)) and isinstance(t_out, (int, float)) and t_out >= t_in > 0:
                found.append({"start": int(t_in), "end": int(t_out), "duration": int(t_out - t_in),
                              "event_type": node.get("eventType"), "source": "timeIn/timeOut"})
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(records)
    unique = {(s["start"], s["end"]): s for s in found}
    return sorted(unique.values(), key=lambda s: s["start"])


async def main() -> None:
    print("Petkit login (used once, not stored).")
    username = input("E-mail: ").strip()
    password = getpass.getpass("Password: ")
    country = (input("Country code [AE]: ").strip() or "AE").upper()

    async with aiohttp.ClientSession() as session:
        client = PetKitClient(username=username, password=password, region=country,
                              timezone="Asia/Dubai", session=session)
        await client.get_devices_data()
        fountains = [(dev_id, ent) for dev_id, ent in client.petkit_entities.items()
                     if getattr(getattr(ent, "device_nfo", None), "device_type", "") in ("ctw3", "ctw2", "w5", "w4")]
        if not fountains:
            print("No fountain found on this account.")
            return
        dev_id, fountain = fountains[0]
        device_type = fountain.device_nfo.device_type
        print(f"Fountain: {fountain.name} ({device_type}, id {dev_id})")

        days = []
        for offset in range(DAYS):
            day = date.today() - timedelta(days=offset)
            try:
                resp = await client.req.request(
                    method=HTTPMethod.POST,
                    url=f"{device_type}/getWorkRecord",
                    params={"day": int(day.strftime("%Y%m%d")), "deviceId": dev_id, "userId": fountain.user_id},
                    headers=await client.get_session_id(),
                )
            except Exception as err:  # keep going: one bad day must not lose the rest
                resp = {"error": repr(err)}
            days.append({"day": day.isoformat(), "response": resp})
            print(f"  {day}: {'error' if isinstance(resp, dict) and 'error' in resp else 'ok'}", end="\r")
        print()

    sessions = sessions_from([d["response"] for d in days])
    OUT.write_text(json.dumps({
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "fountain": {"name": fountain.name, "type": device_type},
        "sessions": sessions,
        "days": days,
    }, indent=1, ensure_ascii=False))
    print(f"{len(sessions)} drinking sessions over {DAYS} days -> {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
