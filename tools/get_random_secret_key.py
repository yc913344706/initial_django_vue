#!/usr/bin/env python3
# encoding: utf-8

import random
import string


print("".join([random.choice(string.digits + string.ascii_letters) for i in range(50)]))
