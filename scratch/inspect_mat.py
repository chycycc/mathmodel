import struct
p=r'D:/python project/mathmodel/数模题目/D题/数据/镇龙乡地理空间数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.mat'
b=open(p,'rb').read(); print(len(b),b[126:128])
o=128
for i in range(10):
 if o+8>len(b):break
 dt,nb=struct.unpack('<II',b[o:o+8]); print('tag',o,dt,nb); o+=8
 if dt in (14,15,16): print('first',b[o:o+64]);
 o+=((nb+7)//8)*8
