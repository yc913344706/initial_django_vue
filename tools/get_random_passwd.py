#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：deploy-compose
@File    ：get_random_passwd.py.py
@Author  ：于川
@Date    ：2022/8/17 18:10
'''

# how to use:
# - ./tools/get_random_passwd.py 8
# - ./tools/get_random_passwd.py 18

import sys
import random


def get_random_password(passwd_length, type_num=4):
    pwd = ""
    pass_dict = {
        0: "0123456789",
        1: "abcdefghijklmnopqrstuvwxyz",
        2: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        3: "!@#$%^*()_+-="
    }
    # https://stackoverflow.com/questions/70426576/get-random-number-from-set-deprecation
    # random_users = random.sample((users), num_of_user)
    # random_users = random.choices(list(users),k=num_of_user)
    # target_types = random.sample(pass_dict.keys(), type_num)
    target_types = random.choices(list(pass_dict.keys()), k=type_num)

    for i in target_types:
        pwd += random.choice(pass_dict[i])

    for i in range(0, passwd_length - len(pwd)):
        pwd += random.choice(''.join(pass_dict.values()))
    # https://help.aliyun.com/document_detail/207872.html

    # pwd = ''.join(random.choice(chars + special_chars) for i in range(passwd_length))
    return ''.join(random.sample(pwd, len(pwd)))


if __name__ == "__main__":
    print(get_random_password(int(sys.argv[1])))
