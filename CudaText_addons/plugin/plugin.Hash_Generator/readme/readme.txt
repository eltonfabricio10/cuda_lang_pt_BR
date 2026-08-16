Plugin for CudaText.
Gives dialog, which is similar to PSPad's dialog "Hash generator".

You can calculate hash for a file (choose it from dialog) or for a custom string (string is encoded in ASCII, so Unicode chars not supported).
Also you can paste some known hash string to the bottom input, and it's compared to calculated hash string, by "Verify" button, or after calculating hash value. Label in dialog will show "Verified" or "?".

Currently supported hashes: 

  MD4 (requires OpenSSL lib)
  MD5
  SHA1
  SHA224
  SHA256
  SHA384
  SHA512
  RIPEMD160 (requires OpenSSL lib)
  Whirlpool (requires OpenSSL lib)


Author: Alexey (CudaText)
License: MIT
