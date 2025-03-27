#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# 定义参数
# =========
import argparse
from pathlib import Path
parser = argparse.ArgumentParser()

# 必选参数
parser.add_argument('encrypted_password', help='加密后的密码')

# 可选参数
# parser.add_argument('-s', dest='split_dir', help='拆分后的文件放到哪里，默认与源文件同目录')

args = parser.parse_args()


# 业务逻辑
# =========

import sys
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(WORKSPACE, 'code', 'backend'))

from lib.password_tools import aes

print(aes.decrypt(args.encrypted_password))
