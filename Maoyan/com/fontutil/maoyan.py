# -*- coding: utf-8 -*-
from fontTools.ttLib import TTFont

# 单步获得模板
font = TTFont("TEST.woff")
font.saveXML('temp.xml')
