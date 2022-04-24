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
图片处理模块，目前提供水印功能
"""
import os  # noqa
import math  # noqa

from django.conf import settings  # noqa
from PIL import Image  # noqa
from PIL import ImageDraw  # noqa
from PIL import ImageFont  # noqa


def produce_watermark(text):
    """
    将文字内容生成图片

    @param {String} text 文字内容
    @return {Image} 图片对象
    """
    image_w = 720
    image_h = 537
    k = 24

    text_image_w = int(image_w * 1.5)  # 确定写文字图片的尺寸，如前所述，要比照片大，这里取1.5倍
    text_image_h = int(image_h * 1.5)
    blank = Image.new("RGBA", (text_image_w, text_image_h), (255, 255, 255, 0))  # 创建用于添加文字的空白图像
    d = ImageDraw.Draw(blank)  # 创建draw对象
    d.ink = 0 + 0 * 256 + 0 * 256 * 256  # 黑色
    # 创建Font对象，k之为字号
    font = ImageFont.truetype(os.path.join(settings.PROJECT_ROOT, "static/font/arial.ttf"), k)
    text_w, text_h = font.getsize(text)  # 获取文字尺寸
    d.text([(text_image_w - text_w) / 2, (text_image_h - text_h) / 2], text, font=font, fill=(180, 180, 190, 110))
    # 旋转文字
    text_rotate = blank.rotate(30)
    # text_rotate.show()
    r_len = math.sqrt((text_w / 2) ** 2 + (text_h / 2) ** 2)
    ori_angle = math.atan(text_h / text_w)
    crop_w = r_len * math.cos(ori_angle + math.pi / 6) * 2  # 被截取区域的宽高
    crop_h = r_len * math.sin(ori_angle + math.pi / 6) * 2
    box = [
        int((text_image_w - crop_w) / 2 - 1) - 40,
        int((text_image_h - crop_h) / 2 - 1) - 40,
        int((text_image_w + crop_w) / 2 + 40),
        int((text_image_h + crop_h) / 2 + 40),
    ]
    text_im = text_rotate.crop(box)  # 截取文字图片
    # text_im.show()
    crop_w, crop_h = text_im.size

    # 旋转后的文字图片粘贴在一个新的blank图像上
    text_blank = Image.new("RGBA", (image_w, image_h), (255, 255, 255, 0))
    for i in range(4):
        for j in range(4):
            paste_box = (int(crop_w * j), int(crop_h * i))
            text_blank.paste(text_im, paste_box)
    text_blank = text_blank.resize((image_w, image_h), Image.ANTIALIAS)
    return text_blank
