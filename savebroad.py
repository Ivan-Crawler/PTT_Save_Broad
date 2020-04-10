# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 21:41:48 2020

@author: Ivan
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

import platform

# 判斷是甚麼作業系統
theOS = list(platform.uname())[0]
if theOS == 'Windows':
    theOS = '\\'
    theEncode = 'utf-8-sig'
else:
    theOS = '/'
    theEncode = 'utf-8'
    
class AllBoard:
    def __init__(self):
        self.name = []
        self.theurl = []
        self.board_name = []
        self.board_class = []
        self.board_title = []
        self.theempty = []
        self.count=0
        
    #回存資料
    def save_All_board(self, url,rm_board_name,rm_board_class,rm_board_title,empty):
        self.name.append(rm_board_name[-1])
        self.theurl.append(url)
        self.board_name.append(rm_board_name)
        self.board_class.append(rm_board_class)
        self.board_title.append(rm_board_title)
        self.theempty.append(empty)


    @classmethod
    def htmlCarwler(cls, url):# 爬蟲
        list_req = requests.get(url)
        return BeautifulSoup(list_req.content, "html.parser")

    
    @classmethod
    def checkArticle(cls, soup):#檢查是否有文章
        if len(soup.findAll('input',{'placeholder':'搜尋文章⋯'})) > 0 :
            return True
        else:
            return False
    
    def checkrepeat(self, url):#防止連結回到最上層分類看板，這樣會無限循環
        if url == 'https://www.ptt.cc/cls/1':
            print(self.count)
            print(type(self.count))
            if self.count < 1:#第一次執行
                self.count = self.count +1
                return True
            else:
                return False
        else:
            return True
        
    def PTTcrawler(self, url, rm_board_name=[], rm_board_class=[],rm_board_title=[]):
        classification_Board = self.htmlCarwler(url)
        get_board = classification_Board.findAll('a',{'class':'board'})
        get_board_name = classification_Board.findAll('div',{'class':'board-name'})
        get_board_class = classification_Board.findAll('div',{'class':'board-class'})
        get_board_title = classification_Board.findAll('div',{'class':'board-title'})

        
        #已經到最底，存進資料庫
        if self.checkArticle(classification_Board):
            self.save_All_board(url,rm_board_name,rm_board_class,rm_board_title,0)

            
        #找不到任何文章，空版
        elif len(get_board) == 0 : 
            self.save_All_board(url,rm_board_name,rm_board_class,rm_board_title,1)

            
        #還有分類繼續爬
        else: 
            
            if self.checkrepeat(url): 
                print('繼續往下爬')
                for b,bn,bc,bt in zip(get_board, get_board_name, get_board_class, get_board_title):
                    #加入新的板名與標題
                    rm_board_name.append(bn.text)
                    rm_board_class.append(bc.text)
                    rm_board_title.append(bt.text)
                    #複製一份出來（必須要用copy），原本資料復原回去，才不會造成版名一直堆疊
                    rm_board_name_fornext = rm_board_name.copy()
                    rm_board_class_fornext = rm_board_class.copy()
                    rm_board_title_fornext = rm_board_title.copy()
        
                    #砍掉前一個板的內容
                    del rm_board_name[len(rm_board_name)-1]
                    del rm_board_class[len(rm_board_class)-1]
                    del rm_board_title[len(rm_board_title)-1]
                    
                    #遞回呼叫
                    self.PTTcrawler(url = 'https://www.ptt.cc/' + b['href'],
                                   rm_board_name=rm_board_name_fornext,
                                   rm_board_class =rm_board_class_fornext,
                                   rm_board_title=rm_board_title_fornext,
                                   )
            else:
                print('回到原點')
                
    def save2csv(self, url, rm_board_name=[], rm_board_class=[],rm_board_title=[]):
        self.PTTcrawler(url = url,
               rm_board_name=rm_board_name,
               rm_board_class =rm_board_class,
               rm_board_title=rm_board_title,
               )
        
        pd.DataFrame({
                    '版名':self.name,
                    '版連結':self.theurl,
                    '版名（路徑）':self.board_name,
                    '分類':self.board_class,
                    '標題':self.board_title,
                    '是否為空版':self.theempty
                    }).to_csv('PTT版.csv', encoding = theEncode, index = 0)

def main(url='https://www.ptt.cc/cls/1',rm_board_name='無資料',rm_board_class='無資料',rm_board_title='無資料'):
    if rm_board_name == '無資料':
        AllBoard().save2csv(url)
    else:
        AllBoard().save2csv(url=url,
                            rm_board_name=rm_board_name,
                            rm_board_class=rm_board_class,
                            rm_board_title=rm_board_title)    
    #範例
    # AllBoard().save2csv(url='https://www.ptt.cc/cls/12759',
    #                     rm_board_name=['CNBBS'],
    #                     rm_board_class=['站台'],
    #                     rm_board_title=['Σ為了不忘卻的紀念及站點聯絡處'])          
    # AllBoard().save2csv(url='https://www.ptt.cc/cls/6124',
    #                     rm_board_name=['A'],
    #                     rm_board_class=['B'],
    #                     rm_board_title=['C'])          
    
    # AllBoard().save2csv('https://www.ptt.cc/cls/1')   
    # AllBoard().save2csv('https://www.ptt.cc/cls/2870')
    

    
if __name__ == '__main__':
    main()