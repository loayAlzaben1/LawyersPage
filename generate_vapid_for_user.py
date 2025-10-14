import base64
from cryptography.hazmat.primitives.asymmetric import ec


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

# generate a P-256 (secp256r1) keypair
priv = ec.generate_private_key(ec.SECP256R1())
pub = priv.public_key()

# Export public key in uncompressed X9.62 form (0x04 | X | Y)
pub_numbers = pub.public_numbers()
x = pub_numbers.x.to_bytes(32, "big")
y = pub_numbers.y.to_bytes(32, "big")
uncompressed = b"\x04" + x + y

# Private key as 32-byte big-endian integer
priv_numbers = priv.private_numbers().private_value
priv_bytes = priv_numbers.to_bytes(32, "big")

print("VAPID_PUBLIC_KEY=" + b64url(uncompressed))
print("VAPID_PRIVATE_KEY=" + b64url(priv_bytes))
