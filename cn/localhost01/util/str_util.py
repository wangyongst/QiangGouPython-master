# -*- coding: utf-8 -*-
import chardet
import sys

# 初始化输出编码
print_code_mode = 'utf-8'

if len(sys.argv) == 2:
    print_code_mode = sys.argv[1]

def print_msg(message):
    encoding = chardet.detect(str(message))['encoding']
    if encoding == print_code_mode:
        print message
    else:
        print message.decode(encoding).encode(print_code_mode)
