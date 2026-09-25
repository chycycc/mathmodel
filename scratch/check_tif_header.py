# -*- coding: utf-8 -*-
import struct
from pathlib import Path

DEM_PATH = Path('数模题目/D题/数据/镇龙乡地理空间数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.tif')
data = DEM_PATH.read_bytes()
u16 = lambda off: struct.unpack_from('<H', data, off)[0]
u32 = lambda off: struct.unpack_from('<I', data, off)[0]
ifd = u32(4)
n = u16(ifd)
print('IFD 数量:', n)
TAG_NAMES = {
    256: 'ImageWidth', 257: 'ImageLength', 258: 'BitsPerSample', 259: 'Compression',
    262: 'PhotometricInterpretation', 273: 'StripOffsets', 277: 'SamplesPerPixel',
    278: 'RowsPerStrip', 279: 'StripByteCounts', 282: 'XResolution', 283: 'YResolution',
    284: 'PlanarConfiguration', 296: 'ResolutionUnit', 305: 'Software', 306: 'DateTime',
    317: 'Predictor', 322: 'TileWidth', 323: 'TileLength', 324: 'TileOffsets',
    325: 'TileByteCounts', 339: 'SampleFormat', 33550: 'ModelPixelScale',
    33922: 'ModelTiepoint', 34735: 'GeoKeyDirectory', 34736: 'GeoDoubleParams', 34737: 'GeoAsciiParams'
}
for i in range(n):
    off = ifd + 2 + 12 * i
    t_id = u16(off)
    t_type = u16(off+2)
    t_cnt = u32(off+4)
    t_val = u32(off+8)
    name = TAG_NAMES.get(t_id, 'Unknown')
    print(f"Tag {t_id:5d} ({name:20s}): type={t_type}, count={t_cnt:6d}, val/off={t_val}")
