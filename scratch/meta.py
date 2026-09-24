import struct, os
for p in [r'D:/python project/mathmodel/数模题目/D题/数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.tif',r'D:/python project/mathmodel/数模题目/D题/数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.mat']:
 print(p,os.path.getsize(p),open(p,'rb').read(32))
