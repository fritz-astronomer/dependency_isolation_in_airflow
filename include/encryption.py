
def md5(s):
    import hashlib
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()
