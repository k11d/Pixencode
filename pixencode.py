#!/usr/bin/env python3

import numpy as np
from PIL import Image
import itertools as it
import math


def to_binary(x):
    x = str(x)
    try:
        bx = bin(x)[2:]
    except:
        try:
            bx = bin(int(x))[2:]
        except:
            bx = bin(ord(x))[2:]
    while len(bx) < 8:
        bx = '0' + bx
    return bx

def message_to_binary(s):
    mess = []
    for c in s:
        bc = to_binary(c)
        while len(bc) < 8:
            bc = '0' + bc
        # print(bc, "->", chr(int(bc, 2)))
        mess.append(bc)
    return mess

def binary_to_message(bs):
    byt = []
    for n in range(8, len(bs), 8):
        byt.append(bs[n-8:n])
    smess = []
    for e in byt:
        s = int(e,2)
        if s >= 32:
            s = chr(s)
        elif s == 10:
            s = '\n'
        # print(e, '->', s)
        smess.append(str(s))
    return "".join(smess)


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
                print('Invalid header')
            else:
                print(message_length)
        return message_length

    def extract_message_bits(self, count):
        bits = ""
        for row_id in range(self.h):
            for col_id in range(self.w):
                bits += to_binary(self.iar[row_id, col_id, 0])[-1]
                bits += to_binary(self.iar[row_id, col_id, 1])[-1]
                bits += to_binary(self.iar[row_id, col_id, 2])[-1]
            if len(bits) >= count + self.HEADER_LEN:
                break
        return bits[self.HEADER_LEN:count+self.HEADER_LEN]


def encode_message_in_image(image_path, message, dest_image='output.png'):
    ei = EImage(image_path)
    bmess = message_to_binary(message)
    ei.encode_bits("".join(bmess))
    Image.fromarray(ei.iar).save(dest_image)

def decode_message_from_image(image_path):
    ei = EImage(image_path)
    mlen = ei.decode_header()
    data = ei.extract_message_bits(mlen)
    return(binary_to_message(data))


if __name__ == '__main__':
    text = '''
# euromillion.py

import random
from math import log

def lottery():
    nums = set()
    while len(nums) < 5:
        nums.add(random.randint(1, 50))
    star_nums = set()
    while len(star_nums) < 2:
        star_nums.add(random.randint(1, 12))
    return nums, star_nums

def check(t,c,p,pc):
    correct_nums = 0
    for n in t:
        if n in p:
            correct_nums += 1
    correct_stars = 0
    for n in c:
        if n in pc:
            correct_stars += 1
    return correct_nums, correct_stars

def human_readable(ival):
    return str(ival)

analysis = {
    -1:
        0,
    0:
        {0:0, 1:0, 2:0, 3:0, 4:0, 5:0},
    1:
        {0:0, 1:0, 2:0, 3:0, 4:0, 5:0},
    2:
        {0:0, 1:0, 2:0, 3:0, 4:0, 5:0},
}
t,c,play,playc = None, None, None, None
count = 0

while t is None or t != play or c != playc:
    analysis[-1] += 1
    t,c = lottery()
    play,playc = lottery()
    res_n , res_c = check(t,c,play,playc)
    analysis[res_c][res_n] += 1
    print(analysis, end='\r')
print()
print("JACKPOT!!!!!!")'''

    encode_message_in_image('lena.png', text, "output.png")
    print(decode_message_from_image('output.png'))

