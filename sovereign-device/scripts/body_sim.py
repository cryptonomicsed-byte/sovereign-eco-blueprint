#!/usr/bin/env python3
"""
body_sim.py — simulated drone/robot body for the Sovereign Device
embodiment protocol (artifact 5 reference pairing flow).

JSON-RPC 2.0 over WebSocket on 127.0.0.1:18877
HTTP stub (advertise/status) on 127.0.0.1:18878

Run:  python3 body_sim.py
Test: curl http://127.0.0.1:18878/advertise
"""
import asyncio, json, sys, time, uuid

try:
    import websockets
except ImportError:
    print("pip install websockets", file=sys.stderr); sys.exit(1)

WS_PORT = 18877
HTTP_PORT = 18878
BODY_PUBKEY = "b0d1" + "a" * 60          # placeholder body key
AGENT_NPUB = None                        # set on offer

GEOFENCE = {"lat": (23.0, 23.3), "lon": (-82.5, -82.2)}
MAX_SPEED = 5.0
TTL = 3600

class State:
    DISCOVERY, OFFERED, ACCEPTED, KEYED, ACTIVE, TERMINATED = range(6)

class Body:
    def __init__(self):
        self.state = State.DISCOVERY
        self.session_id = None
        self.offer = None
        self.pose = {"lat": 23.1136, "lon": -82.3666, "alt": 0.0, "yaw": 0}
        self.battery = 95.0
        self.seq = 0
        self.start_ts = None
        self.samples = []

    def advertise(self):
        return {"body_pubkey": BODY_PUBKEY,
                "capabilities": ["camera", "gps", "motors"],
                "transports": ["ws"],
                "vendor": {"type": "sim", "version": "1.0"},
                "load": 0.1, "battery": round(self.battery, 1),
                "pos": self.pose if self.state != State.DISCOVERY else None}

    def handle_offer(self, ev):
        if self.state not in (State.DISCOVERY, State.TERMINATED):
            return {"accepted": False, "error": "busy"}
        # validate signature is skipped in sim (real runtime checks it)
        self.offer = ev
        self.state = State.OFFERED
        self.session_id = "s-" + uuid.uuid4().hex[:8]
        return {"accepted": True, "session_id": self.session_id,
                "body_session_pubkey": "bb01" + "b" * 60}

    def handle_command(self, sid, cmd):
        if self.state != State.ACTIVE or sid != self.session_id:
            return {"ok": False, "error": "not-active"}
        op = cmd.get("op")
        if op == "goto":
            lat, lon, alt = cmd["target"]
            if not (GEOFENCE["lat"][0] <= lat <= GEOFENCE["lat"][1] and
                    GEOFENCE["lon"][0] <= lon <= GEOFENCE["lon"][1]):
                return {"ok": False, "error": "geofence-violation"}
            self.pose = {"lat": lat, "lon": lon, "alt": alt,
                         "yaw": self.pose["yaw"]}
            return {"ok": True, "ack_ts": int(time.time())}
        if op == "set_velocity":
            v = abs(cmd.get("vx", 0)) + abs(cmd.get("vy", 0)) + abs(cmd.get("vz", 0))
            if v > MAX_SPEED:
                return {"ok": False, "error": "speed-violation"}
            return {"ok": True, "ack_ts": int(time.time())}
        if op == "sense":
            sid2 = f"sp-{len(self.samples)+1:04d}"
            self.samples.append(sid2)
            return {"ok": True, "sample_id": sid2}
        if op == "hover":
            return {"ok": True, "ack_ts": int(time.time())}
        if op == "stop":
            self.state = State.TERMINATED
            return {"ok": True}
        return {"ok": False, "error": "unsupported-op"}

    def end_session(self, sid):
        if sid != self.session_id:
            return {"error": "unknown-session"}
        summary = json.dumps({"samples": self.samples,
                              "pose": self.pose}, sort_keys=True)
        import hashlib
        h = hashlib.sha256(summary.encode()).hexdigest()
        self.state = State.TERMINATED
        return {"final_summary_hash": h, "receipts": list(self.samples)}

body = Body()

async def telemetry_loop():
    while True:
        await asyncio.sleep(1)
        if body.state == State.ACTIVE:
            body.battery = max(0, body.battery - 0.05)
            body.seq += 1
            print(json.dumps({"jsonrpc": "2.0", "method": "telemetry",
                              "params": {"session_id": body.session_id,
                                         "ts": int(time.time()),
                                         "pose": body.pose,
                                         "battery": round(body.battery, 1),
                                         "status": "ok",
                                         "sensors": {"camera": True, "gps": True}}}),
                  flush=True)

async def ws_handler(ws):
    global AGENT_NPUB
    async for raw in ws:
        try:
            req = json.loads(raw)
        except Exception:
            continue
        method = req.get("method"); params = req.get("params", {})
        rid = req.get("id")
        result = None; error = None
        if method == "offer":
            AGENT_NPUB = params.get("offer_event", {}).get("pubkey")
            result = body.handle_offer(params.get("offer_event"))
            if result.get("accepted"):
                body.state = State.ACCEPTED
                print(f"[sim] OFFERED->ACCEPTED session={body.session_id}", flush=True)
        elif method == "command":
            result = body.handle_command(params.get("session_id"), params.get("cmd"))
        elif method == "heartbeat":
            result = {"battery": round(body.battery, 1), "link": "ws", "seq": body.seq}
        elif method == "end_session":
            result = body.end_session(params.get("session_id"))
            print("[sim] TERMINATED -> DISCOVERY", flush=True)
            body.state = State.DISCOVERY
        else:
            error = {"code": -32601, "message": f"unknown method {method}"}
        out = {"jsonrpc": "2.0"}
        if rid is not None:
            out["id"] = rid
        if error: out["error"] = error
        else: out["result"] = result
        await ws.send(json.dumps(out))
        # sim key-agreement placeholder
        if method == "offer" and result.get("accepted"):
            print("[sim] NOISE-KK placeholder: prologue=offer_id|accept_id "
                  "(real handshake in Rust body runtime)", flush=True)
            body.state = State.KEYED
            print(f"[sim] KEYED -> ACTIVE session={body.session_id}", flush=True)
            body.state = State.ACTIVE

async def http_stub(reader, writer):
    data = await reader.read(4096)
    path = data.decode(errors="ignore").split(" ")[1] if data else "/"
    if path == "/advertise":
        resp = json.dumps({"jsonrpc": "2.0", "result": body.advertise()})
    else:
        resp = json.dumps({"state": body.state, "session_id": body.session_id,
                           "battery": round(body.battery, 1), "pose": body.pose})
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                 b"Content-Length: " + str(len(resp)).encode() + b"\r\n\r\n" + resp.encode())
    await writer.drain(); writer.close()

async def main():
    print(f"body_sim: WS on 127.0.0.1:{WS_PORT}, HTTP on 127.0.0.1:{HTTP_PORT}", flush=True)
    print("body_pubkey:", BODY_PUBKEY, flush=True)
    asyncio.create_task(telemetry_loop())
    await asyncio.gather(
        websockets.serve(ws_handler, "127.0.0.1", WS_PORT),
        asyncio.start_server(http_stub, "127.0.0.1", HTTP_PORT),
    )
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
