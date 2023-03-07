import hashlib
m = hashlib.sha256()
m.update(b"123")
m.digest()
m.hexdigest()
print(m.hexdigest())