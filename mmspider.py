#coding=utf-8
__author__ = 'Daemon'

import urllib2,re,os,datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from pyquery import PyQuery as pq
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Spider:
    def __init__(self):
        self.page=1
        self.dirName='MM_data'
        self.browser = webdriver.PhantomJS() # Get local session of firefox
        self.browser.get("https://mm.taobao.com/search_tstar_model.htm?spm=719.1001036.1998606017.2.BxJmWq") # Load page
        self.page_total=0;
        self.page_current=1;
        #assert "淘女郎-美人库" in browser.title
 
        time.sleep(0.2) # Let the page load, will be added to the API

        self.getContent();

    def getContent(self):
        page_total= self.browser.find_element_by_class_name("page-total").text[1:-1]
        print(page_total)
        self.page_total=int(page_total)
        for i in range(1, self.page_total):
            time.sleep(4)
            self.LoadPageContent()
            self.browser.find_element_by_class_name("page-next").click() # Find the query box

#获取页面内容提取
    def LoadPageContent(self):
        #记录开始时间
        begin_time=datetime.datetime.now()
        lis = self.browser.find_elements_by_xpath('//*[@id="J_GirlsList"]/li')

        for item in lis:
            try:
                url = item.find_element_by_xpath('./a').get_attribute('href')
                temp1_img_url = item.find_element_by_xpath('./a/div/div[1]/img').get_attribute('src')
                temp2_img_url = 'https:'+item.find_element_by_xpath('./a/div/div[1]/img').get_attribute('data-ks-lazyload')
                img_url=''
                if len(temp1_img_url) > len(temp2_img_url):
                    img_url=temp1_img_url
                else:
                    img_url=temp2_img_url
                name = item.find_element_by_xpath('./a/div/div[2]/span[1]').text
                area = item.find_element_by_xpath('./a/div/div[2]/span[2]').text
                body_data = item.find_element_by_xpath('./a/div/div[3]/span[1]').text
                hot_index = item.find_element_by_xpath('./a/div/div[3]/span[2]').text[1:]
                print(url)
                print(name)
                print(area)
                print(body_data)
                print(hot_index)
                print(img_url)
                dir=self.dirName+'/'+name
                self.mkdir(dir)
                self.saveIcon(img_url,dir,name)
                end_time=datetime.datetime.now()
                brief=name+' '+area+' '+body_data+' '+hot_index
            except Exception,e:
                continue
        #保存个人信息 以及耗时
            try:self.saveBrief(brief,dir,name,end_time-begin_time)
            except Exception,e:
                print u'保存个人信息失败 %s'%e.message

    def getDetailPage(self,url,name,begin_time):
        
        self.driver.get(url)
        base_msg=self.driver.find_elements_by_xpath('//div[@class="mm-p-info mm-p-base-info"]/ul/li')
        brief=''
        for item in base_msg:
            print item.text
            brief+=item.text+'\n'
            #保存个人信息
        icon_url=self.driver.find_element_by_xpath('//div[@class="mm-p-model-info-left-top"]//img')
        icon_url=icon_url.get_attribute('src')

        dir=self.dirName+'/'+name
        self.mkdir(dir)


    #保存头像
        try:
            self.saveIcon(icon_url,dir,name)
        except Exception,e:
            print u'保存头像失败 %s'%e.message

    #开始跳转相册列表
        images_url=self.driver.find_element_by_xpath('//ul[@class="mm-p-menu"]//a')
        images_url=images_url.get_attribute('href')
        try:
            self.getAllImage(images_url,name)
        except Exception,e:
            print u'获取所有相册异常 %s'%e.message

        end_time=datetime.datetime.now()
        #保存个人信息 以及耗时
        try:self.saveBrief(brief,dir,name,end_time-begin_time)
        except Exception,e:
            print u'保存个人信息失败 %s'%e.message


#获取所有图片
    def getAllImage(self,images_url,name):
        self.driver.get(images_url)
    #只获取第一个相册
        photos=self.driver.find_element_by_xpath('//div[@class="mm-photo-cell-middle"]//h4/a')
        photos_url=photos.get_attribute('href')

        #进入相册页面获取相册内容
        self.driver.get(photos_url)
        images_all=self.driver.find_elements_by_xpath('//div[@id="mm-photoimg-area"]/a/img')

        self.saveImgs(images_all,name)


    def saveImgs(self,images,name):
        index=1
        print u'%s 的相册有%s张照片, 尝试全部下载....'%(name,len(images))

        for imageUrl in images:
            splitPath = imageUrl.get_attribute('src').split('.')
            fTail = splitPath.pop()
            if len(fTail) > 3:
                fTail = "jpg"
            fileName = self.dirName+'/'+name +'/'+name+ str(index) + "." + fTail
            print u'下载照片地址%s '%fileName

            self.saveImg(imageUrl.get_attribute('src'),fileName)
            index+=1


    def saveIcon(self,url,dir,name):
        print u'头像地址%s %s '%(url,name)

        splitPath=url.split('.')
        fTail=splitPath.pop()
        fileName=dir+'/'+name+'.'+fTail
        print fileName
        self.saveImg(url,fileName)

    #写入图片
    def saveImg(self,imageUrl,fileName):
        print imageUrl
        u=urllib2.urlopen(imageUrl)
        data=u.read()
        f=open(fileName,'wb')
        f.write(data)
        f.close()

    #保存个人信息
    def saveBrief(self,content,dir,name,speed_time):
        speed_time=u'当前MM耗时 '+str(speed_time)
        content=content+'\n'+speed_time

        fileName=dir+'/'+name+'.txt'
        f=open(fileName,'w+')
        print u'正在获取%s的个人信息保存到%s'%(name,fileName)
        f.write(content.encode('utf-8'))

#创建目录
    def mkdir(self,path):
        path=path.strip()
        print u'创建目录%s'%path
        if os.path.exists(path):
            return False
        else:
            os.makedirs(path)
            return True
myspider = Spider()