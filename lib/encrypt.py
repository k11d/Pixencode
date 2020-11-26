import itertools as it

def _cifer_decifer(plainstream, keystream):
    ks = it.cycle(keystream)
    for p in plainstream:
        k = next(ks)
        try:
            yield p ^ k
        except:
            try:
                yield ord(chr(int(p))) ^ k
            except:
                yield ord(p) ^ k

def cifer(message, password):
    return "".join(map(chr, _cifer_decifer(map(ord, message), map(ord, password))))

def decifer(cifered, password):
    return "".join(map(chr, _cifer_decifer(cifered, map(ord, password))))


if __name__ == '__main__':

    Message = "My super secret message. Please do not record this message anywhere."
    Password = "password1234"
    print()

    c = cifer(Message, Password)
    print(c)
    d = decifer(c, Password)
    print(d)

