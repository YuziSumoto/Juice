# -*- coding: UTF-8 -*-

import datetime # 日付モジュール

def CheckDate(self,Hizuke): # 日付チェック

  if Hizuke == "":
    return True

  try:
      newDate=datetime.datetime.strptime(Hizuke,"%Y/%m/%d")
      return True
  except ValueError:
      return False

def CookieAdd(self,cookieStr): # クッキー保存
  cookieStr += ';'
  self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
  return

def CookieGet(self,KeyStr): # クッキー保存
  return self.request.cookies.get(KeyStr)
 
