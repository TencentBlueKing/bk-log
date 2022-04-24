# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
"""
AES加密模块
"""
import base64  # noqa
import math  # noqa

from Crypto.Cipher import AES  # noqa
from Crypto import Random  # noqa


class AESCipher(object):
    """
    AES256加解密器
    注意事项：
    - 加密后密文长度大雨明文长度
    - iv默认使用无需设置，设置后会固定iv进行加密
    """

    def __init__(self, key, iv=None, bs=AES.block_size):
        """
        初始化
        :param key: 秘钥，会经过sha256生成实际秘钥
        :param iv: iv向量，默认不填写，使用随机iv
        :param bs: 加密块，默认无需填写
        """
        self.bs = bs
        self.iv = iv
        self.key = self.get_16bytes_from_string(key)

    def encrypt(self, raw):
        """
        加密函数
        :param raw: 明文
        :return: str 密文
        """
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size) if not self.iv else self.iv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        iv = iv if not self.iv else ""
        result = base64.urlsafe_b64encode(iv + cipher.encrypt(raw))
        return result

    def decrypt(self, enc):
        """
        解密函数
        :param enc: 密文
        :return: str 明文
        """
        if isinstance(enc, str):
            enc = enc.encode("utf-8")
        enc = base64.urlsafe_b64decode(enc)
        iv = enc[: AES.block_size] if not self.iv else self.iv
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        if not self.iv:
            return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")
        else:
            return self._unpad(cipher.decrypt(enc)).decode("utf-8")

    def _pad(self, s):
        """
        打包成长度为bs整数倍的字符串
        """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        """
        解包成原文本
        """
        return s[: -ord(s[len(s) - 1 :])]

    @staticmethod
    def predict_length(length):
        """
        计算加密后的长度
        :param length: int
        :return: int
        """
        return int(math.ceil(((length + 1) / 16 * 16 + 16) / 3.0)) * 4

    @staticmethod
    def get_16bytes_from_string(source_str):
        block_size = AES.block_size
        target = source_str
        if len(target) < 1:
            return False
        elif len(target) < block_size:
            target += target * block_size

        return target[:block_size]
