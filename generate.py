#! /usr/bin/env python
from lxml import etree as ET
from datetime import datetime
import os
import sys

# --- config ------------------------
sourcefontname = 'source.ttx'

maxlengthofname = 30 # max length of file names of svg images
svgs = ['nyan.svg']

namelist = [
        'Copyright &#169; 2017 Hogehoge',
        'My Emoji Font',
        'Regular',
        'My Emoji Font Version 1.000',
        'My Emoji Font Regular',
        'Version 1.000',
        'MyEmojiFont-Regular',
        '*Trademark*',
        '*Name*',
        '*Designer*',
        '*Description*',
        '*URL*',
]
# -----------------------------------


## 既存フォントのデータを持ってくる
sourcefont = open(sourcefontname, 'r', encoding='utf-8')
sourcefont.readline()#1行目を読み飛ばす
root=ET.fromstring(sourcefont.read())

## OS_2
usMaxContex = root.find('OS_2')
usMaxContex.attrib['value'] = str(maxlengthofname + 2) #usMaxContext（AFKDOの誤植？）。GSUB(リガチャ等)で結合し得る最大の文字数


## name
name = ET.SubElement(root, 'name')
for num in range(12):
    ET.SubElement(name, 'namerecord', attrib={
        'nameID': str(num),
        'platformID': '1',
        'platEncID': '0',
        'langID': '0x0'
        }).text = namelist[num]
    ET.SubElement(name, 'namerecord', attrib={
        'nameID': str(num),
        'platformID': '3',
        'platEncID': '1',
        'langID': '0x409'
        }).text = namelist[num]



### 絵文字を追加する
glyphorder = root.find('GlyphOrder')

#コメントの削除
for c in glyphorder.xpath('//comment()'):
    p = c.getparent()
    p.remove(c)

glyphcount = len(glyphorder)#既存のグリフ数

##gsubが無い場合は考えないことにする
gsub = root.find('GSUB')
dfltlang = gsub.find('ScriptList/ScriptRecord/ScriptTag[@value=\'DFLT\']').getparent().find('Script/DefaultLangSys')
langfcount = 0 # DFLTの中から参照するFeatureの数
for c in dfltlang:
    if c.tag == 'FeatureIndex':
        langfcount+=1
featurecount = 0 # FeatureListの要素数
flist = gsub.find('FeatureList')
for c in flist:
    if c.tag == 'FeatureRecord':
        featurecount+=1
lucount = 0
lulist = gsub.find('LookupList')
for c in lulist:
    if c.tag == 'Lookup':
        lucount+=1
#print(lucount)
ET.SubElement(dfltlang, 'FeatureIndex', attrib={'index': str(langfcount), 'value': str(featurecount)})
frec = ET.SubElement(flist, 'FeatureRecord', attrib={'index': str(featurecount)})
ET.SubElement(frec, 'FeatureTag', attrib={'value': 'liga'})
feature = ET.SubElement(frec, 'Feature')
ET.SubElement(feature, 'LookupListIndex', attrib={'index': '0', 'value': str(lucount)})
lookup = ET.SubElement(lulist, 'Lookup', attrib={'index': str(lucount)})
ET.SubElement(lookup, 'LookupFlag', attrib={'value': '0'})
lsubst = ET.SubElement(lookup, 'LigatureSubst', attrib={'index': '0'})


for i in range(len(svgs)):
    glyphnumber = glyphcount + i;#現在のグリフの番号（id）。0-originであることに注意。
    glyphname, tmp = os.path.splitext(os.path.basename(svgs[i]))
    ET.SubElement(glyphorder, 'GlyphID', attrib={'id': str(glyphnumber), 'name': glyphname})
    hmtx = root.find('hmtx')
    gwidth = int(root.find('OS_2/sTypoAscender').attrib['value']) - int(root.find('OS_2/sTypoDescender').attrib['value']) #文字幅をアセンダ+ディセンダにする
    ET.SubElement(hmtx, 'mtx', attrib={'name': glyphname, 'width': str(gwidth), 'lsb': '0'})
    chars = root.find('CFF/CFFFont/CharStrings')
    nullchar = chars.find('CharString[@name=\'.notdef\']').text
    ET.SubElement(chars, 'CharString', attrib={'name': glyphname}).text=nullchar
    svg = root.find('SVG')
    if svg == None:
        svg = ET.SubElement(root, 'SVG')
    svggl = ET.SubElement(svg, 'svgDoc', attrib={'startGlyphID': str(glyphnumber), 'endGlyphID': str(glyphnumber)})
    rawsvg = open(svgs[i], 'r').read()
    svgelm = ET.fromstring(rawsvg)
    svgelm.attrib["id"] = 'glyph'+str(glyphnumber)
    chinosvg = ET.CDATA(ET.tostring(svgelm))
    svggl.text = chinosvg
    ET.SubElement(svg, 'colorPalettes')
    #gsub
    ligatureset = ET.SubElement(lsubst, 'LigatureSet', attrib={'glyph': 'colon'})
    components = ','.join(list(glyphname)) + ',colon'
    ET.SubElement(ligatureset, 'Ligature', attrib={'components': components, 'glyph': glyphname})
    
    

maxp = root.find('maxp')
maxp.find('numGlyphs').attrib['value'] = str(glyphcount + len(svgs))
hhea = root.find('hhea')
#hhea.find('numberOfHMetrics').attrib['value'] = str(glyphcount + len(svgs))
hhea.find('numberOfHMetrics').attrib['value'] = '1'


###ファイル出力処理
tree = ET.ElementTree(element=root)
tree.write('out.ttx', encoding='utf-8', xml_declaration=True, pretty_print=True)

