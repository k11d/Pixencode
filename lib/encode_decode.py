#!/usr/bin/env python3

from PIL import Image
from .encrypt import cifer, decifer
import itertools as it
import math
import numpy as np
import os, sys


def to_binary(s):
    def g():
        for c in s:
            sb = bin(ord(c))[2:]
            while len(sb) < 8:
                sb = '0' + sb
            yield sb
    if type(s) == int or type(s) == np.uint8:
        sb = bin(s)[2:]
        while len(sb) < 8:
            sb = '0' + sb
        return sb
    else:
        return g()

def from_binary(bys):
    if type(bys) == str:
        bys = [bys[n-8:n] for n in range(8, len(bys), 8)]
    for c in bys:
        yield chr(int(c, 2))


class EImage:

    HEADER_LEN = 128

    def __init__(self, fp):
        self.fp = fp
        self.img = Image.open(fp)
        self.iar = np.array(self.img)
        self.h,self.w = self.iar.shape[:2]
        self.bits_available = self.h * self.w * 3

    def encode_bits(self, bits):
        while len(bits) % 8 != 0:
            bits = '0' + bits
        blen = len(bits)
        header = to_binary(blen)
        while len(header) < self.HEADER_LEN:
            header = '0' + header
        if blen + len(header) > self.bits_available:
            raise RuntimeError("Not enough space to encode the message")


        def stream_data():
            for b in it.chain(list(header), list(bits)):
                yield b

        bstream = stream_data()
        done = False
        for row_id in range(self.h):
            if done:
                break
            for col_id in range(self.w):
                try:
                    b = next(bstream)
                    pr = to_binary(self.iar[row_id, col_id, 0])
                    pr = pr[:-1] + b
                    self.iar[row_id, col_id, 0] = int(pr, 2)

                    b = next(bstream)
                    pg = to_binary(self.iar[row_id, col_id, 1])
                    pg = pg[:-1] + b
                    self.iar[row_id, col_id, 1] = int(pg, 2)

                    b = next(bstream)
                    pb = to_binary(self.iar[row_id, col_id, 2])
                    pb = pb[:-1] + b
                    self.iar[row_id, col_id, 2] = int(pb, 2)
                except StopIteration:
                    done = True
                    break

    def decode_header(self):
        header = ""
        done = False
        for row_id in range(self.h):
            if done:
                break
            for col_id in range(self.w):
                header += to_binary(self.iar[row_id, col_id, 0])[-1]
                header += to_binary(self.iar[row_id, col_id, 1])[-1]
                header += to_binary(self.iar[row_id, col_id, 2])[-1]
                if len(header) >= self.HEADER_LEN:
                    done = True
                    break
        header = header[:self.HEADER_LEN]
        message_length = 0
        try:
            message_length = int(header, 2)
        except:
            print('Invalid header')
        else:
            if math.log(message_length, 10) > 10:
                raise RuntimeError('Invalid header')
        return message_length

    def extract_message_bits(self, count):
        bits = ""
        for row_id in range(self.h):
            for col_id in range(self.w):
                bits += to_binary(self.iar[row_id, col_id, 0])[-1]
                bits += to_binary(self.iar[row_id, col_id, 1])[-1]
                bits += to_binary(self.iar[row_id, col_id, 2])[-1]
            if len(bits) > count + self.HEADER_LEN:
                break
        return bits[self.HEADER_LEN:count+self.HEADER_LEN+1]

def encode_message_in_image(image_path, message):
    ei = EImage(image_path)
    bmess = "".join(to_binary(message))
    ei.encode_bits("".join(bmess))
    dest_image = os.path.join(os.path.dirname(image_path), 'output_' + os.path.basename(image_path))
    Image.fromarray(ei.iar).save(dest_image)
    return dest_image

def decode_message_from_image(image_path):
    ei = EImage(image_path)
    try:
        mlen = ei.decode_header()
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    data = ei.extract_message_bits(mlen)
    s = "".join(from_binary(data))
    return s


if __name__ == '__main__':
    image = sys.argv[1]
    text = " ".join(sys.argv[2:])
    dest = encode_message_in_image(image, text)
    print(decode_message_from_image(dest), end='\n')

