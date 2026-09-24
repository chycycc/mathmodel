import struct
p=r'D:/python project/mathmodel/数模题目/D题/数据/镇龙乡地理空间数据/镇龙乡及周边地理数据/数字高程模型数据（DEM）/镇龙乡及周边30米DEM.tif'
b=open(p,'rb').read(); off=8; n=struct.unpack_from('<H',b,off)[0]; print(n)
for i in range(n):
 o=off+2+12*i; tid,typ,c,val=struct.unpack_from('<HHII',b,o); print(tid,typ,c,val)
