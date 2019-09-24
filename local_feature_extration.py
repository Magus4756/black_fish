#coding:utf-8
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import re
import sys
import csv
import importlib
import time
importlib.reload(sys)
import os

#特征提取函数
def feature_extract(data,includeUrl):
    soup = BeautifulSoup(data, 'html5lib')
    f1_istxt = istxt_extract(soup)
    f2_link = link_extract(soup,includeUrl)
    f3_linknum = linknum_extract(soup)
    f4_innerlinknum = innerlinknum_extract(soup,includeUrl)
    f5_outterlinknum = outterlinknum_extract(soup,includeUrl)
    f6_formnum = formnum_extract(soup)
    f7_getform = getform_extract(soup)
    f8_postform = postform_extract(soup)
    f9_src = src_extract(soup,includeUrl)
    f10_copyright = copyright_extract(soup)
    f11_imgsrc = imgsrc_extract(soup,includeUrl)
    f12_style = style_extract(soup,includeUrl)
    f13_script = script_extract(soup,includeUrl)
    f14_formsrc = formsrc_extract(soup,includeUrl)
    f15_tagtype = tagtype_extract(soup)
    f16_embednum = embednum_extract(soup)
    f17_iframenum = iframenum_extract(soup)
    f18_appletnum = appletnum_extract(soup)
    f19_framenum = framenum_extract(soup)
    f20_imgnum = imgnum_extract(soup)
    f21_inputnum = inputnum_extract(data)
    f22_passwordnum = passwordnum_extract(data)
    f23_submitnum = submitnum_extract(data)
    f24_stylenum = stylenum_extract(data)
    f25_scriptnum = scriptnum_extract(data)
    f26_scriptlen = scriptlen_extract(soup)
    f27_popupwindow = popupwindow_extract(data)
    f28_onclick = onclick_extract(data)
    f29_function = function_extract(data)
    f30_linkjudge = linkjudge_extract(soup)
    f31_hyplink = hyplink_extract(soup)
    f32_formlink = formlink_extract(data,includeUrl)
    f33_redirect = redirect_extract(data)
    f34_csslinknum = csslinknum_extract(soup)
    f35_mail = mail_extract(data)
    f36_divlink = divlink_extract(soup,includeUrl)
    f37_csslink = csslink_extract(soup)
    f38_innercsslink = cssinnerlink_extract(soup,includeUrl)
    feature_vector = [includeUrl,
                      f1_istxt,f2_link,f4_innerlinknum,f5_outterlinknum,
                      f6_formnum,f7_getform,f8_postform,f9_src,f10_copyright,
                      f11_imgsrc,f12_style,f13_script,f14_formsrc,f15_tagtype,
                      f16_embednum,f17_iframenum,f18_appletnum,f19_framenum,f20_imgnum,
                      f21_inputnum,f22_passwordnum,f23_submitnum,f24_stylenum,f25_scriptnum,
                      f26_scriptlen,f27_popupwindow,f28_onclick,f29_function,f30_linkjudge,
                      f31_hyplink,f32_formlink,f33_redirect,f34_csslinknum,f35_mail,
                      f36_divlink,f37_csslink,f38_innercsslink
                      ]
    return feature_vector

#是否含文本-
def istxt_extract(soup):
    for script in soup.find_all("script"):
        script.extract()
    for style in soup.find_all("style"):
        style.extract()
    text = soup.get_text()
    if len(text):
        return 1;
    else:
        return -1;

#链接特征提取函数 指向内部链接的比例
def link_extract(soup,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    internalLinks = []
    link_num = 0
    innerlink_num = 0
    # 找出所有以“/”开头的链接
    for link in soup.find_all("a"):
        if link.attrs.get('href'):
            link_num += 1
    for link in soup.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
        if link.attrs.get('href'):
            if link.attrs.get('href') not in internalLinks:
                if (link.attrs.get('href').startswith("/")):
                    internalLinks.append(includeUrl + link.attrs.get('href'))
                    innerlink_num += 1
                else:
                    internalLinks.append(link.attrs.get('href'))
                    innerlink_num += 1
    try:
        return innerlink_num/link_num
    except ZeroDivisionError:
        return -1

#链接数量
def linknum_extract(soup):
    link_num = 0
    for link in soup.find_all("a"):
        if link.attrs.get('href'):
            link_num += 1
    return link_num

#内部链接数量
def innerlinknum_extract(soup,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    internalLinks = []
    innerlink_num = 0
    # 找出所有以“/”开头的链接
    for link in soup.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
        if link.attrs.get('href') is not None:
            if link.attrs.get('href') not in internalLinks:
                if (link.attrs.get('href').startswith("/")):
                    internalLinks.append(includeUrl + link.attrs.get('href'))
                    innerlink_num += 1
                else:
                    internalLinks.append(link.attrs.get('href'))
                    innerlink_num += 1
    return innerlink_num

#外部链接数量
def outterlinknum_extract(soup,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    internalLinks = []
    link_num = 0
    innerlink_num = 0
    # 找出所有以“/”开头的链接
    for link in soup.find_all("a"):
        if link.attrs.get('href'):
            link_num += 1
    for link in soup.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
        if link.attrs.get('href'):
            if link.attrs.get('href') not in internalLinks:
                if (link.attrs.get('href').startswith("/")):
                    internalLinks.append(includeUrl + link.attrs.get('href'))
                    innerlink_num += 1
                else:
                    internalLinks.append(link.attrs.get('href'))
                    innerlink_num += 1
    return link_num - innerlink_num

#链接综合判定
def linkjudge_extract(soup):
    linkAveNum_black = 12.87328244
    link_num = 0
    for link in soup.find_all("a"):
        if link.attrs.get('href'):
            link_num += 1
    if link_num > linkAveNum_black:
        return 1
    else:
        return -1

#表单数量特征提取函数
def formnum_extract(data):
    rform = re.compile("form", re.I)
    mach = rform.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#表单get方式数量提取函数
def getform_extract(data):
    rget = re.compile("get", re.I)
    mach = rget.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#表单post方式数量提取函数
def postform_extract(data):
    rpost = re.compile("post",re.I)
    mach = rpost.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#资源加载特征提取函数
def src_extract(data,url):
    https = []
    http = []
    r1 = re.compile(r'"https://\S+"')
    r2 = re.compile(r'"http://\S+"')
    if url[4] == 's':
        r1 = re.compile(r'("(https:)?//?[^ \}\(\),]+")')
    else:
        r2 = re.compile(r'"(http:)?//?[^ \}\(\),]+"')
    match = r1.findall(str(data))
    for i in match:
        https.append(i[0])
    match = r2.findall(str(data))
    for i in match:
        http.append(i)
    try:
        return len(https)/(len(https)+len(http))
    except ZeroDivisionError:
        return -1

#版权特征提取函数
def copyright_extract(data):
    rcopy = re.compile("@copyright",re.I)
    mach = rcopy.findall(str(data))
    if mach:
        return 1
    else:
        return -1

#节点种类提取函数
def tagtype_extract(soup):
    list = []
    flag = 0
    num = 0
    for child in soup.descendants:
        for l in list:
            if child.name == l and child.name != None:
                flag = 1
        if flag == 0:
            list.append(child.name)
            num += 1
    return num

#embed标签数量提取函数
def embednum_extract(soup):
    embed_num = 0
    for child in soup.find_all('embed'):
        embed_num += 1
    return embed_num

#iframe标签数量提取函数
def iframenum_extract(soup):
    iframe_num = 0
    for child in soup.find_all('iframe'):
        iframe_num += 1
    return iframe_num

#applet标签数量提取函数
def appletnum_extract(soup):
    applet_num = 0
    for child in soup.find_all('applet'):
        applet_num += 1
    return applet_num

#frame标签数量提取函数
def framenum_extract(soup):
    frame_num = 0
    for child in soup.find_all('frame'):
        frame_num += 1
    return frame_num

#图片安全资源特征
def imgsrc_extract(soup,url):
    https = []
    http = []
    r1 = re.compile(r'"https://\S+"')
    r2 = re.compile(r'"http://\S+"')
    if url[4] == 's':
        r1 = re.compile(r'("(https:)?//?[^ \}\(\),]+")')
    else:
        r2 = re.compile(r'"(http:)?//?[^ \}\(\),]+"')
    img_src = soup.find_all('img')
    match = r1.findall(str(img_src))
    for i in match:
        https.append(i[0])
    match = r2.findall(str(img_src))
    for i in match:
        http.append(i)
    num_img = len(http) + len(https)
    num_secureimg = len(https)
    try:
        return num_secureimg / num_img
    except ZeroDivisionError:
        return -1

#样式安全资源特征
def style_extract(soup,url):
    https = []
    http = []
    r1 = re.compile(r'\(https://\S+\)')
    r2 = re.compile(r'\(http://\S+\)')
    if url[4] == 's':
        r1 = re.compile(r'(\((https:)?//?[^ \}\(\),]+\))')
    else:
        r2 = re.compile(r'\((http:)?//?[^ \}\(\),]+\)')
    style_src = soup.find_all("style")
    match = r1.findall(str(style_src))
    for i in match:
        https.append(i[0])
    match = r2.findall(str(style_src))
    for i in match:
        http.append(i)
    num_style = len(http) + len(https)
    num_securestyle = len(https)
    try:
        return num_securestyle / num_style
    except ZeroDivisionError:
        return -1

#脚本安全资源特征
def script_extract(soup,url):
    https = []
    http = []
    r1 = re.compile(r'"https://\S+"')
    r2 = re.compile(r'"http://\S+"')
    if url[4] == 's':
        r1 = re.compile(r'("(https:)?//?[^ \}\(\),]+")')
    else:
        r2 = re.compile(r'"(http:)?//?[^ \}\(\),]+"')
    script_src = soup.find_all("script")
    match = r1.findall(str(script_src))
    for i in match:
        https.append(i[0])
    match = r2.findall(str(script_src))
    for i in match:
        http.append(i)
    num_script = len(http)+len(https)
    num_securescript = len(https)
    try:
        return num_securescript / num_script
    except ZeroDivisionError:
        return -1

#表单安全资源特征
def formsrc_extract(soup, url):
    https = []
    http = []
    r1 = re.compile(r'"https://\S+"')
    r2 = re.compile(r'"http://\S+"')
    if url[4] == 's':
        r1 = re.compile(r'("(https:)?//?[^ \}\(\),]+")')
    else:
        r2 = re.compile(r'"(http:)?//?[^ \}\(\),]+"')
    form_src = soup.find_all('form')
    match = r1.findall(str(form_src))
    for i in match:
        https.append(i[0])
    match = r2.findall(str(form_src))
    for i in match:
        http.append(i)
    num_formsrc = len(http) + len(https)
    num_secureform = len(https)
    try:
        return num_secureform / num_formsrc
    except ZeroDivisionError:
        return -1

#图片数量
def imgnum_extract(soup):
    imgnum = 0
    for img in soup.find_all("img"):
        imgnum += 1
    return imgnum

#password输入栏数量
def passwordnum_extract(data):
    rpassword = re.compile("password")
    mach = rpassword.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#submit表单数量
def submitnum_extract(data):
    rsubmit = re.compile("submit")
    mach = rsubmit.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#input输入栏数量
def inputnum_extract(data):
    rsinput = re.compile("input")
    mach = rsinput.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#css文件数量
def stylenum_extract(data):
    rstyle = re.compile("style")
    mach = rstyle.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#script文件数量
def scriptnum_extract(data):
    rscript = re.compile("script")
    mach = rscript.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#javascript长度
def scriptlen_extract(soup):
    script = soup.find_all("script")
    return len(str(script))

#是否包含popupwindow
def popupwindow_extract(data):
    rwindow = re.compile("PopupWindow",re.I)
    mach = rwindow.findall(str(data))
    if mach:
        return 1
    else:
        return 0

# 是否包含onclick
def onclick_extract(data):
    rclick = re.compile("onclick",re.I)
    mach = rclick.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#function个数
def function_extract(data):
    rfunction = re.compile("function",re.I)
    mach = rfunction.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#空链接
def hyplink_extract(soup):
    num = 0
    for hyplink in soup.find_all("a"):
        if hyplink.attrs.get('href') is not None and hyplink.attrs.get('href')=="#":
            num += 1
        else:
            num += 0
    return num

#form表单的链接类型
def formlink_extract(data,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    soup = BeautifulSoup(data, 'html5lib')
    for form in soup.find_all('form'):
        if form is not None:
            if form.attrs.get('action') is not None:
                formlink = form.attrs.get('action')
                if re.match('http',formlink) is not None:
                    r = re.compile("^(/|.*" + includeUrl + ")")
                    m = r.findall(formlink)
                    if m:
                        return 1
                    else:
                        return 0
                else:
                    return 2
            else:
                return 3
        else:
            return -1

#重定向提取
def redirect_extract(data):
    redirect = re.compile("redirect|location|http-equiv=\"refresh\"")
    mach = redirect.findall(str(data))
    if mach:
        return len(mach)
    else:
        return 0

#css中的链接数
def csslinknum_extract(soup):
    css = soup.find_all("style")
    rlink = re.compile("url",re.I)
    mach = rlink.findall(str(css))
    if mach:
        return len(mach)
    else:
        return 0

#mail
def mail_extract(data):
    rmail = re.compile("mail\(\)|mailto")
    mach = rmail.findall(str(data))
    if mach is not None:
        return len(mach)
    else:
        return 0

#表单容器中的内部链接比例
def divlink_extract(soup,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    for div in soup.find_all("div", class_=re.compile("post|get|submit|form")):
        if div is not None:
            rlink = re.compile("\"http[^\"]*\"")
            mach = rlink.findall(str(div))
            if len(mach) > 0:
                r = re.compile(includeUrl)
                m = r.findall(str(mach))
                return len(m)/len(mach)
            else:
                return 0
        else:
            return -1

#css内部链接比例
def cssinnerlink_extract(soup,includeUrl):
    includeUrl = urlparse(includeUrl).netloc
    print(includeUrl)
    css = soup.find_all("style")
    if css is not None:
        rlink = re.compile("url\(http[^\)]*\)")
        mach = rlink.findall(str(css))
        print(mach)
        if mach:
            rinclude = re.compile(includeUrl)
            m = rinclude.findall(str(mach))
            print(m)
            if len(m)>0:
                return len(m)/len(mach)
            else:
                return 0
        else:
            return 2
    else:
        return -1



#css可疑URL
def csslink_extract(soup):
    css = soup.find_all("style")
    if css is not None:
        rlink = re.compile("url\([^\)]*\)")
        mach = rlink.findall(str(css))
        if mach:
            rdata = re.compile("data:")
            m1 = rdata.findall(str(mach))
            if m1:
                return 3
            else:
                return 2
        else:
            return 1
    else:
        return -1

#从url提取特征
def get_pagevector(url):
    time1=time.time()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36"
    }
    req = urllib.request.Request(url = url, headers = headers)
    #req.add_header("Connection","keep-alive")
    response = urllib.request.urlopen(req)
    if response is not None:
        data = response.read()
        time2 = time.time()
        try:
            data = data.decode()
        except:
            data = data.decode('gbk','ignore')
        vector = feature_extract(data,url)
        time3=time.time()
        # print("页面请求时间："+str(time2-time1))
        # print("特征提取时间："+str(time3-time2))
        # print(vector)
        return vector

""" feature_vector = [includeUrl,
                      f1_istxt,f2_link,f3_linknum,f4_innerlinknum,f5_outterlinknum,
                      f6_formnum,f7_getform,f8_postform,f9_src,f10_copyright,
                      f11_imgsrc,f12_style,f13_script,f14_formsrc,f15_tagtype,
                      f16_embednum,f17_iframenum,f18_appletnum,f19_framenum,f20_imgnum,
                      f21_inputnum,f22_passwordnum,f23_submitnum,f24_stylenum,f25_scriptnum,
                      f26_scriptlen,f27_popupwindow,f28_onclick,f29_function,f30_linkjudge1,
                       f31_hyplink,f32_formlink,f33_redirect,f34_csslinknum,f35_mail,
                      f36_divlink,f37_csslink,f38_innercsslink
                      ]"""

if __name__ == '__main__':
    print("#####")
    time1=time.time()
    header = ["URL",
          "Is_Txt","Link_Per","Link_Num","InnerLink_Num","OutterLink_Num",
          "Form_Num","GetForm_Num","PostForm_Num","Src_Safe","Copyright",
          "Img_Safe","Style_Safe","Script_Safe","FormSrc_Safe","Tagtype",
          "Embed_Num","Iframe_Num","Applet_Num","Frame_Num","Img_Num",
          "InputBox_Num","Password_Num","Submit_Num","Style_Num","Script_Num",
          "Script_Len","PopupWindow","OnClick","Function","LinkJudge",
          "HypLink","FormLink","Redirect","CSSLink_Num","Mail",
          "DivLink","CSSLink","InnerCSSLink",
          "label"  ]
    feature_writer = open('now/UP.csv','a',newline='')
    fcsv = csv.writer(feature_writer)
    fcsv.writerow(header)
    print("载入数据...")
    filepath="now/UP"
    for file in range(4,2662):
        newDir = os.path.join(filepath,str(file))
        try:
            fopen = open(newDir,'rb')
            url = fopen.readline()
            try:
                url = url.decode()
            except:
                url = url.decode('gbk','ignore')
            data = fopen.read()
            try:
                data = data.decode()
            except:
                data = data.decode('gbk','ignore')
            soup = BeautifulSoup(data, 'html5lib')
            vector = feature_extract(data,url)
            vector.append(0)
            fcsv.writerow(vector)
            print(str(file))
            print(str(vector))
        except:
            continue
        
    print("向量生成完毕")
    feature_writer.close()
    time2=time.time()
    print("耗时："+str(time2-time1))