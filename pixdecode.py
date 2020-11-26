#!/usr/bin/env python3

import sys
from lib.codec import decode_message_from_image

image = sys.argv[1]
print(decode_message_from_image(image))


