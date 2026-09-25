# -*- coding: utf-8 -*-
import struct
from pathlib import Path

DEM_PATH = Path('数模题目/D题/数据/镇龙乡地理空间数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.tif')
data = DEM_PATH.read_bytes()
u16 = lambda off: struct.unpack_from('<H', data, off)[0]
u32 = lambda off: struct.unpack_from('<I', data, off)[0]
ifd = u32(4)
n = u16(ifd)
tags = {}
for i in range(n):
    off = ifd + 2 + 12 * i
    tags[u16(off)] = {"type": u16(off + 2), "count": u32(off + 4), "value": u32(off + 8), "val_offset": off + 8}

# q3_solver.py 中的错误实现
def values_buggy(tag_id):
    tag = tags[tag_id]
    size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 12: 8}[tag["type"]]
    off = ifd + 2 + 12 * n + 4 if tag["count"] * size <= 4 else tag["value"]
    result = []
    for i in range(tag["count"]):
        pos = off + i * size
        if tag["type"] == 3:
            result.append(struct.unpack_from("<H", data, pos)[0])
        elif tag["type"] == 4:
            result.append(struct.unpack_from("<I", data, pos)[0])
    return result

# 规范正确的 TIFF 实现
def values_correct(tag_id):
    tag = tags[tag_id]
    size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 12: 8}[tag["type"]]
    off = tag["val_offset"] if tag["count"] * size <= 4 else tag["value"]
    result = []
    for i in range(tag["count"]):
        pos = off + i * size
        if tag["type"] == 3:
            result.append(struct.unpack_from("<H", data, pos)[0])
        elif tag["type"] == 4:
            result.append(struct.unpack_from("<I", data, pos)[0])
    return result

print("q3_solver.py buggy 读取结果:")
print("  Width (Tag 256):", values_buggy(256)[0])
print("  Height (Tag 257):", values_buggy(257)[0])
print("  TileWidth (Tag 322):", values_buggy(322)[0])
print("  TileLength (Tag 323):", values_buggy(323)[0])

print("\n规范正确的 TIFF 读取结果:")
print("  Width (Tag 256):", values_correct(256)[0])
print("  Height (Tag 257):", values_correct(257)[0])
print("  TileWidth (Tag 322):", values_correct(322)[0])
print("  TileLength (Tag 323):", values_correct(323)[0])
