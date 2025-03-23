#!/usr/bin/env python3

# -*- coding: UTF-8 -*-
import random
import string

def get_random_aes_key(length=16):
    """生成随机 aes 密钥"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

if __name__ == '__main__':
    print(get_random_aes_key())
