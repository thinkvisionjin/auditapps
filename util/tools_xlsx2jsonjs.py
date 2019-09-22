import re
import json
from urllib.request import urlopen, quote
import codecs
import sys
import os
import xlrd

class Tools:
   
    @staticmethod
    def excel2json(workBookName,sheetName,fileName,withgeo,addressColumn):
        res = Tools.doJobs(workBookName,sheetName,withgeo,addressColumn)
        f = open(fileName,'w',encoding='utf8')
        print(res,file=f)
        f.close()

    @staticmethod
    def excel2js(workBookName,sheetName,fileName,withgeo,addressColumn):
        res = Tools.doJobs(workBookName,sheetName,withgeo,addressColumn)
        res_str = "var address = " + json.dumps(res,ensure_ascii=False)
        f = open(fileName, 'w', encoding='utf8')
        print(res_str,file=f)
        f.close()

    @staticmethod
    def doJobs(workBookName,sheetName,withgeo=False,addressColumn='地址'):
        workBook = xlrd.open_workbook(workBookName)
        bookSheet = workBook.sheet_by_name(sheetName)
        res = []
        columns = []
        index = 0
        for col in range(bookSheet.ncols):
            columns.append(bookSheet.cell(0, col).value)
        for row in range(bookSheet.nrows)[1:len(range(bookSheet.nrows))]:
            row_data = {}
            for col in range(bookSheet.ncols):
                cel = bookSheet.cell(row, col)
                try:
                    row_data[columns[col]] = str(cel.value)
                except:
                    pass
            if withgeo==True:
                row_data['lat'], row_data['lng'] = Tools.getlnglat(row_data[addressColumn])
            index += 1
            # if index == 200:
            #     return res
            print(str(index)+":"+json.dumps(row_data,ensure_ascii=False))
            res.append(row_data)
        return res
    
    @staticmethod 
    def getlnglat(address):
        lat = 0
        lng = 0
        try:
            """根据传入地名参数获取经纬度"""
            url = 'http://api.map.baidu.com/geocoder/v2/'
            output = 'json'
            ak = 'PcNZP3amKzo7zKNDP7c9MDRC' # 浏览器端密钥
            address = quote(address)
            uri = url + '?' + 'address=' + address  + '&output=' + output + '&ak=' + ak
            req = urlopen(uri)
            res = req.read().decode()
            temp = json.loads(res)
            lat = temp['result']['location']['lat']
            lng = temp['result']['location']['lng']
        except:
            print("Get AError")
        return lat, lng

    @staticmethod
    def jsondump(outfilename, dic):
        """传入保存路径和字典参数，保存数据到对应的文件中"""
        with codecs.open(outfilename, 'w', 'utf-8') as outfile:
            json.dump(dic, outfile, ensure_ascii=False)
            outfile.write('\n')

    @staticmethod     
    def excel2StoryMapJson(workBookName,sheetName,fileName,withgeo,addressColumn):
        res = Tools.doJobs(workBookName,sheetName,withgeo,addressColumn)
        slides =[]
        index = 0
        for row_data in res:
            slide={};
            slide["date"] = row_data["出生年份"] + '-' + row_data["过世年份"]
            if index ==0:
                slide["type"] = "overview"
            slide["location"] = {
                "name":row_data["工作地"],
                "lat":row_data["lat"],
                "lon":row_data["lng"],
                "zoom":10,
                "line":"ture"
            }
            slide["text"] = {
                "headline":row_data["标题"]+":"+row_data["姓名"],
                "text": "<span class='vco-note'>"+row_data["评价"]+"</span>"
            }
            slide["media"] = {
                "url":"img/"+row_data["姓名"]+".png",
                "credit": "人民日报",
                "caption": row_data["荣誉"]
            }
            slides.append(slide)
            index += 1

        storydic = {
            "storymap":{
                "slides":slides
            }
        }
        Tools.jsondump(fileName, storydic)
        return slides

            
if __name__ == '__main__':
    # 从excel生成storymapjson
    Tools.excel2StoryMapJson("data/优秀共产党员.xlsx","Sheet1","data/优秀共产党员2.json",True,"工作地")
    # 从excel生成百度撒点用js 
    Tools.excel2js("data/优秀共产党员.xlsx","Sheet2","data/优秀共产党员.js",True,"工作地")