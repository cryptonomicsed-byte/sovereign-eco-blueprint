# AGENT CONTACT CARD — v0.1

A signed, scannable **pointer** to an agent's identity and its communication
endpoints. This is the VCP Device Manifest generalised from *devices* to
*agents*: the artifact that lets one sovereign node physically encounter another,
verify who it is, and open a session — with no coordinator, no relay, and no
internet required.

Status: SPEC (nothing issues agent cards today — verified: no QR issuance in
Vantage backend). Small, additive build.

---

## 1. Why this exists

Two gaps:

1. The device advertises itself (`advertise()` = `{body_pubkey, capabilities,
   transports:["ws","reticulum","tcp"], vendor, load, battery, pos}`), but an
   **agent** has no equivalent public card. You can hold an npub; you cannot hand
   someone a verifiable card.
2. The online join path exists (`POST /api/guilds/{slug}/join-request` →
   one-shot challenge → sign NIP-42 kind:22242 with BIP-340 schnorr →
   `join-confirm`). That is a *network* ceremony. There is no *local*, offline
   introduction.

The card is the offline/local counterpart of the join flow.

---

## 2. What the card is — and is not

It is a **pointer**. The card carries commitments and endpoints; the *identity*
resolves from GIX. This distinction is the whole design: you cannot put a
derivation in a contact card.

Ọmọ Kọ́dà identity is a **derivation**, not a key (verified in code):
```
identity/bipon39.rs   entropy → entropy_to_mnemonic → mnemonic_to_seed → keys
identity/dna.rs       generate_dna_fingerprint(name, birth_timestamp, odu_seed)
identity/ori.rs:52    struct Ori · :105 genesis(entropy_seed, ifascript_version)
                                · :135 advance(experience_delta)
                                · :151 state_hash()
```
So what travels is a **commitment** to the Orí (`ori_commitment`), not the Orí.

**Do NOT model this on Meshenger's contact.** Meshenger's card is
`{name, ed25519 pubkey, IP list}` — a bare key, no derivation, no attestation,
on a different curve. Meshenger's contact is a valid *pattern*, not a compatible
*format*. See §6.

---

## 3. Card schema

```json
{
  "agent_id": "did:key:z6Mk…",
  "display_name": "Ọmọ Kọ́dà",
  "npub": "npub1…",                          // secp256k1 / BIP-340 — the eco identity curve
  "ori_commitment": "sha256:…",              // Ori::state_hash() at issuance (ori.rs:151)
  "capabilities_commitment": "sha256:…",     // commitment only; list resolves from GIX
  "endpoints": [
    { "transport": "lan",        "address": "fe80::1122:33ff:fe44:5566", "priority": 1 },
    { "transport": "nostr",      "address": "wss://omokoda.duckdns.org:3443", "priority": 2 },
    { "transport": "meshtastic", "address": "!a1b2c3d4", "priority": 3 },
    { "transport": "reticulum",  "address": "…", "priority": 4 }
  ],
  "issued_at": 1756000000,
  "expires_at": 1756003600,
  "signature": "…"                           // BIP-340 schnorr over the canonical fields
}
```

### Field rules

| field | rule |
|---|---|
| `npub` | secp256k1 (Nostr/BIP-340). **Not** ed25519. This is the eco identity curve. |
| `ori_commitment` | a hash/commitment. Never the Orí itself, never the seed, never the mnemonic. |
| `capabilities_commitment` | a commitment. The capability list resolves from GIX. |
| `endpoints[].transport` | a **BEARER name**, not a product name. Bring-None: `lan` · `nostr` · `meshtastic` · `lxmf` · `reticulum` · `ws` · `tcp`. See §5. |
| `signature` | BIP-340 schnorr over the canonical serialisation (excluding `signature`). Same primitive as the kind-31010 OFFER and the NIP-42 join. |
| `expires_at` | cards expire. A stale card must fail verification, not silently resolve. |

---

## 4. Verification flow (scan → verify → resolve → handshake)

```
1. SCAN      read the QR / text blob → parse to the schema above
2. VERIFY    schnorr-verify `signature` against `npub`
             → fail: reject. A card without a valid signature is a claim, not a card.
3. FRESH     check expires_at > now
4. RESOLVE   look up npub in GIX → real capabilities, lineage / parent refs,
             Orí state → compare against ori_commitment / capabilities_commitment
             → mismatch = the card is stale or forged; reject
5. REACH     pick the highest-priority reachable endpoint (for `lan`: derive the
             address, see LOCAL_BEARER.md)
6. HANDSHAKE run the EXISTING VCP flow unchanged:
             OFFER (kind 31010, signed by npub) → validate + policy
             → ACCEPT → Noise KK (prologue = sha256(offer_id ‖ accept_id))
             → ACTIVE → command/telemetry → receipt
```

Steps 1–4 are the "introduction ceremony." Steps 5–6 are the session you already
have. The card adds the introduction; it changes nothing downstream.

---

## 5. Bearer names, not product names

The single repeated failure in every external analysis of this space: naming a
**product** in a slot that takes a **protocol**, then discovering the product
cannot implement it.

- ❌ `"transport": "meshenger"` — there is no agent-side Meshenger endpoint to
  implement. Meshenger is Android-only, has no headless mode, and uses ed25519.
- ✅ `"transport": "lan"` — the bearer: P2P over a local IP network with no
  server/DHCP/DNS, using the ARC pattern in `LOCAL_BEARER.md`.

A transport is a *capability of the network*, not a *brand of an app*.

---

## 6. Relationship to Meshenger (study, do not depend)

Meshenger contributes exactly two things, both absorbed here:

1. **QR contact exchange** as the introduction primitive — adopted as the card's
   delivery mechanism.
2. **MAC → IPv6 link-local address derivation** for local reachability with no
   DHCP/DNS/server — adopted as the `lan` bearer (see §5, `LOCAL_BEARER.md`).

NOT adopted: its ed25519 contact format (wrong curve), its libsodium signaling
crypto (keep Noise KK — the *box* curves happen to align at X25519, but the
identity/signing model does not), its app, its Android constraint, its 1:1-only
scope.

## 7. The invariant this serves

```
Transport ≠ authority
```
A card, a QR, a session, a voice channel — none of these may execute anything.
An inbound communication becomes a `MutationPlan` (omokoda-core/src/mutation/:
router.rs · backends/{zero,larql}.rs · receipt.rs), is INSPECTED, APPLIED and
ROLLBACK-able, and is receipted. The communication channel is structurally
incapable of being an execution authority.

This joins the canonical negatives:
```
Proof ≠ Mint             (Ọ̀ṢỌ́VM: a proof authorises allocation, it does not mint)
signature ≠ settlement   (Sui executes; Ọ̀ṢỌ́VM signs)
authority ≠ execution    (Vantage gets economic consequence)
Transport ≠ authority    (this spec)
```

---

## 8. Build surface (small)

- `contact_card` module in the DIP/VCP crate — schema + canonical serialisation
  + BIP-340 sign/verify. Reuse the primitives already present (kind-31010 offer
  signing, NIP-42 join signing).
- QR emit/scan in the client surface (Vantage `agent-phone` / Vantage-Voice) —
  nothing exists today.
- GIX resolution endpoint: npub → {capabilities, lineage, ori_state}.
- **No new crypto. No new protocol. No fork of Meshenger.**
