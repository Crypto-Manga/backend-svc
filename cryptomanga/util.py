import hmac
import os
from base64 import b64decode
from hashlib import sha256


def is_valid_request(request) -> bool:

    crc = request.headers["X-Twitter-Webhooks-Signature"]
    h = hmac.new(
        bytes(os.environ["twitter_key_secret"], "ascii"),
        request.get_data(),
        digestmod=sha256,
    )

    crc = b64decode(crc[7:])  # strip out the first 7 characters
    return hmac.compare_digest(h.digest(), crc)


def strip_suffix(id: str) -> int:
    return int(id.replace(".json", ""))
