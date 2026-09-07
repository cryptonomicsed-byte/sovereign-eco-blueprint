#!/usr/bin/env python3
"""
First-boot birth for the Portable Sovereign Agent Device.
Arch Linux ARM, runs as systemd oneshot (first-boot.service).

Zero-network, zero-build: pure-python secp256k1 + BIP-340 schnorr
(inline, verified against official test vector 0 in the SEER stack).
Prefers `nak` / `bipon39` / `ifa` binaries when present.

Pipeline (artifact 3):
  entropy -> seed -> nsec -> npub  (NIP-06-style: seed IS the key; the
  mnemonic path via bipon39 CLI is a wordlist encoding of the same seed)
  -> IP Root genesis -> engrams -> kind 31000 birth + 31001 binding
  -> outbox or direct relay publish -> birthed marker -> listen profile
"""
import hashlib, hmac, json, os, secrets, shutil, subprocess, sys, time

STATE = "/var/lib/sovereign"
HOME = "/var/lib/sovereign/home"
RELAYS = ["wss://omokoda.duckdns.org:3443", "wss://relay.damus.io"]

# ----------------------------------------------------------------------
# secp256k1 + BIP-340 (inline, zero-dep). Same math as SEER nostr_layer.
# ----------------------------------------------------------------------
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def _inv(a, m):
    return pow(a, m - 2, m)

def _point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1; x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if p1 == p2:
        lam = (3 * x1 * x1) * _inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)

def _point_mul(k, point=(GX, GY)):
    r = None
    while k:
        if k & 1: r = _point_add(r, point)
        point = _point_add(point, point)
        k >>= 1
    return r

def pubkey_xonly(seckey_int):
    pt = _point_mul(seckey_int)
    return pt[0].to_bytes(32, "big")          # x-only, even-y assumed

def _tagged_hash(tag, msg):
    th = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(th + th + msg).digest()

def schnorr_sign(msg, seckey_int, aux):
    """BIP-340 exact reference construction (deterministic w.r.t. aux).
    Matches official test vector 0 when seckey=3, aux=0x00..00."""
    d0 = seckey_int
    if d0 == 0 or d0 >= N:
        raise ValueError("invalid seckey")
    Pn = _point_mul(d0)
    d = d0 if Pn[1] % 2 == 0 else N - d0
    px = Pn[0].to_bytes(32, "big")
    # t = bytes(d) XOR hash_BIP0340/aux(aux)
    t = bytes(a ^ b for a, b in zip(d.to_bytes(32, "big"),
                                    _tagged_hash("BIP0340/aux", aux)))
    rand = int.from_bytes(t, "big")
    k0 = int.from_bytes(_tagged_hash("BIP0340/nonce",
                                     rand.to_bytes(32, "big") + px + msg),
                        "big") % N
    if k0 == 0:
        raise ValueError("bad nonce")
    R = _point_mul(k0)
    k = k0 if R[1] % 2 == 0 else N - k0      # even-y normalization
    rx = R[0].to_bytes(32, "big")
    e = int.from_bytes(_tagged_hash("BIP0340/challenge", rx + px + msg),
                       "big") % N
    sig = rx + ((k + e * d) % N).to_bytes(32, "big")
    return sig

def event_id(pubkey_hex, created_at, kind, tags, content):
    ser = json.dumps([0, pubkey_hex, created_at, kind, tags, content],
                     separators=(",", ":"))
    return hashlib.sha256(ser.encode()).hexdigest()

# ----------------------------------------------------------------------
def log(msg):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(f"{STATE}/birth.log", "a") as f: f.write(line + "\n")

def device_id():
    parts = []
    for p in ("/sys/class/dmi/id/product_uuid",
              "/sys/firmware/devicetree/base/serial-number",
              "/etc/machine-id"):
        try:
            with open(p, "rb") as f: parts.append(f.read().strip())
        except Exception: pass
    try:
        for line in open("/sys/class/net/eth0/address"):
            parts.append(line.strip().encode())
    except Exception: pass
    return hashlib.sha256(b"|".join(parts) or secrets.token_bytes(16)).hexdigest()

def collect_entropy():
    pools = [os.urandom(64)]
    try:
        with open("/dev/hwrng", "rb") as f: pools.append(f.read(64))
    except Exception: pass
    cast = None
    if shutil.which("ifa"):
        try:
            cast = subprocess.run(["ifa", "cast", "--json"], capture_output=True,
                                  timeout=10).stdout[:512]
            pools.append(cast)
        except Exception: pass
    seed = hashlib.sha512(b"".join(pools)).digest()
    log(f"entropy: urandom + hwrng:{len(pools)>1} + ifa:{bool(cast)} -> sha512")
    return seed[:32], cast

def bipon39_mnemonic(seed_hex):
    if not shutil.which("bipon39"):
        log("bipon39 not present; skipping mnemonic (seed hex is the backup)")
        return None
    try:
        out = subprocess.run(["bipon39", "generate", "--seed", seed_hex],
                             capture_output=True, timeout=15).stdout.decode()
        return out.strip()
    except Exception as e:
        log(f"bipon39 failed: {e}")
        return None

def build_event(kind, pubkey, seckey, tags, content, created):
    ev = {"id": None, "pubkey": pubkey, "created_at": created, "kind": kind,
          "tags": tags, "content": json.dumps(content, separators=(",", ":"))}
    ev["id"] = event_id(pubkey, created, kind, tags, ev["content"])
    ev["sig"] = schnorr_sign(bytes.fromhex(ev["id"]),
                             int.from_bytes(bytes.fromhex(seckey), "big"),
                             os.urandom(32)).hex()
    return ev

def try_publish(ev):
    """Direct relay publish if websockets is importable; else outbox."""
    try:
        import websockets, asyncio
    except ImportError:
        with open(f"{STATE}/outbox/{ev['id']}.json", "w") as f:
            json.dump(ev, f)
        return "outbox (websockets missing)"
    async def _pub():
        async with websockets.connect(RELAYS[0]) as ws:
            await ws.send(json.dumps(["EVENT", ev]))
            r = json.loads(await asyncio.wait_for(ws.recv(), 10))
            return r
    try:
        r = asyncio.run(_pub())
        return f"relay {RELAYS[0]} -> {r}"
    except Exception as e:
        with open(f"{STATE}/outbox/{ev['id']}.json", "w") as f:
            json.dump(ev, f)
        return f"outbox ({e})"

def main():
    os.makedirs(f"{STATE}/outbox", exist_ok=True)
    os.makedirs(f"{STATE}/home/.sovereign/state", exist_ok=True)
    created = int(time.time())

    # 1-2. entropy -> seed -> keypair
    seed, cast = collect_entropy()
    nsec = seed.hex()
    seckey_int = int.from_bytes(seed, "big")
    pub = pubkey_xonly(seckey_int).hex()
    log(f"npub hex: {pub}")
    log(f"nsec (RECORD ONCE, then destroy this log line): {nsec}")

    # 3. mnemonic (optional, bipon39 CLI)
    mnem = bipon39_mnemonic(nsec)
    mnem_fp = hashlib.sha256((mnem or nsec).encode()).hexdigest()[:16] if mnem else None

    # 4. IfáScript metadata
    odu = None
    if cast:
        try:
            odu = json.loads(cast)
        except Exception:
            odu = {"raw": cast.decode(errors="replace")[:200]}

    # 5. IP Root genesis
    dev = device_id()
    ip_root = hashlib.sha256(f"{pub}|{dev}|{created}".encode()).hexdigest()
    log(f"device_id: {dev}")
    log(f"ip_root : {ip_root}")

    # 6. Engrams
    state_dir = f"{STATE}/home/.sovereign/state"
    birth_engram = {
        "ns": "mem/agent/birth", "npub": pub, "device_id": dev,
        "ip_root_id": ip_root, "birth_receipt_id": None,
        "created_at": created, "owner_binding": None,
        "soul": odu or {}, "mnemonic_fp": mnem_fp,
    }
    ident_engram = {
        "ns": "mem/agent/identity", "npub": pub,
        "key_derivation": "nip06", "wordlist": "bipon39" if mnem else "raw-hex",
        "bunker": "unix-socket", "device_id": dev,
    }
    with open(f"{state_dir}/birth.json", "w") as f: json.dump(birth_engram, f, indent=2)
    with open(f"{state_dir}/identity.json", "w") as f: json.dump(ident_engram, f, indent=2)
    with open(f"{state_dir}/ip-root.json", "w") as f:
        json.dump({"ip_root_id": ip_root, "npub": pub, "created_at": created}, f, indent=2)

    # 7. Publish kind 31000 birth + 31001 binding
    birth = build_event(31000, pub, nsec,
        [["d", ip_root], ["t", "agent/birth"], ["t", "ip/root"],
         ["device", dev], ["bipon39-fp", mnem_fp or ""],
         ["odu", (odu or {}).get("primary_odu", "") or ""],
         ["created", str(created)]],
        {"npub": pub, "ip_root_id": ip_root, "device_id": dev,
         "created_at": created, "soul": odu or {},
         "image": {"distro": "arch", "version": "2026.08"}},
        created)
    binding = build_event(31001, pub, nsec,
        [["d", dev], ["t", "device/binding"], ["agent", pub],
         ["hw", "pi5"], ["fp", dev], ["created", str(created)]],
        {"device_id": dev, "board": "pi5", "binding_type": "primary"},
        created)
    birth_engram["birth_receipt_id"] = birth["id"]
    with open(f"{state_dir}/birth.json", "w") as f: json.dump(birth_engram, f, indent=2)

    log(f"birth 31000 publish: {try_publish(birth)}")
    log(f"binding 31001 publish: {try_publish(binding)}")

    # 8. marker + drop to listen profile
    with open("/var/lib/sovereign/birthed", "w") as f:
        f.write(json.dumps({"npub": pub, "ip_root_id": ip_root, "at": created}))
    subprocess.run(["systemctl", "start", "sovereign-profile@listen"], capture_output=True)
    log("birth complete -> listen profile. agent starting.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
