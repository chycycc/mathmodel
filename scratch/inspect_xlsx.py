import zipfile, re, os, glob, xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def read_xlsx(p):
 z=zipfile.ZipFile(p)
 ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  root=ET.fromstring(z.read('xl/sharedStrings.xml'))
  for si in root.findall('m:si',NS): ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
 wb=ET.fromstring(z.read('xl/workbook.xml'))
 rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
 relmap={x.attrib['Id']:x.attrib['Target'] for x in rel}
 for sh in wb.find('m:sheets',NS):
  name=sh.attrib['name']; target=relmap[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
  if not target.startswith('xl/'): target='xl/'+target
  root=ET.fromstring(z.read(target)); rows=[]
  for row in root.findall('.//m:sheetData/m:row',NS):
   vals=[]
   for c in row.findall('m:c',NS):
    v=c.find('m:v',NS); val='' if v is None else v.text
    if c.attrib.get('t')=='s' and val!='': val=ss[int(val)]
    vals.append((c.attrib.get('r'),val))
   rows.append(vals)
  print(repr((' SHEET '+name+' rows '+str(len(root.findall('.//m:sheetData/m:row',NS)))+' cols sample '+repr(rows)).encode('unicode_escape').decode('ascii')))
base=r'D:/python project/mathmodel/数模题目/D题/数据/无人机应急物资运输基础数据'
for f in glob.glob(base+'/*.xlsx'):
 print('FILE',os.path.basename(f)); read_xlsx(f)
