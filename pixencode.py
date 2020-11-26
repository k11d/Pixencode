#!/usr/bin/env python3

import sys
from lib.codec import encode_message_in_image

image = sys.argv[1]
text = " ".join(sys.argv[2:])
encode_message_in_image(image, text)


