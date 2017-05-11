#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import common

import datetime # 日付モジュール

from MstUser   import *   # 使用者マスタ
from MstByoto  import *   # 病棟マスタ

from DatMeisai import *   # 明細データ

class MainHandler(webapp2.RequestHandler):

  @login_required
###############################################################################
  def get(self):  # 初期表示

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:  # 登録済みユーザ以外は拒否！
      self.redirect(users.create_logout_url(self.request.uri))
      return

    LblMsg = ""

    Rec = {}

    Rec['StrNengetu'] = self.StrNengetuSet()
    Rec['StrByoto']   = self.StrByotoSet()
    Kubun = self.request.cookies.get('Kubun', '')
    if Kubun == "":
      Rec['OptKubun1']  = "checked"
    else:
      Rec['OptKubun' + str(Kubun)]  = "checked"

    template_values = {
      'Rec'   : Rec,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice010.html')
    self.response.out.write(template.render(path, template_values))
#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Rec = {}

    Nengetu = self.request.get('CmbNengetu')
    cookieStr = 'Nengetu=' + Nengetu + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    Rec['StrNengetu'] = self.StrNengetuSet()

    Byoto = self.request.get('CmbByoto')
    cookieStr = 'Byoto=' + Byoto + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    Rec['StrByoto']   = self.StrByotoSet()

    Kubun = self.request.get('OptKubun')
    cookieStr = 'Kubun=' + Kubun + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    if self.request.get('BtnKettei')  != '':
      parm = "?Byoto=" + self.request.get('CmbByoto', '')
      parm += "&Nengetu=" + self.request.get('CmbNengetu', '')
      parm += "&Sex=" + self.request.get('OptKubun', '')
      self.redirect("/Juice020/" + parm)
      return

    if self.request.get('BtnKettei2')  != '': # 一括入力
      parm = "?ByotoCD=" + self.request.get('CmbByoto', '')
      parm += "&Kubun=" + self.request.get('OptKubun', '')
      self.redirect("/Juice100/" + parm)
      return

    Rec['OptKubun' + str(Kubun)]  = "checked"

    template_values = {
      'Rec'   : Rec,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice010.html')
    self.response.out.write(template.render(path, template_values))
###############################################################################
  def StrNengetuSet(self):

    Hizuke = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日

    if self.request.get('CmbNengetu') == "":  # 初画面表示
      SelHizuke = self.request.cookies.get('Nengetu', '')
    else:
      SelHizuke = self.request.get('CmbNengetu')

    retStr = ""

    while  Hizuke > datetime.datetime.strptime('2014/01/01', '%Y/%m/%d'):
      retStr += "<option value='"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "'"
      if SelHizuke == Hizuke.strftime('%Y/%m'):  # 選択？
        retStr += " selected "
      retStr += ">"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "</option>"
      Hizuke = datetime.datetime.strptime(Hizuke.strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Hizuke -= datetime.timedelta(days=1) # 前月末日

    return retStr
#--------------------------------------------------------------------------------
  def StrByotoSet(self):

    if self.request.get('CmbByoto') == "":  # 初画面表示
      SelCode = self.request.cookies.get('Byoto', '')
      if SelCode == "":
        SelCode = 3
    else:
      SelCode = self.request.get('CmbByoto')

    MstSnap = MstByoto().GetAllCD()

    retStr = ""

    for MstRec in MstSnap: 
      retStr += "<option value='"
      retStr += str(MstRec.Code)
      retStr += "'"
      if int(SelCode) == MstRec.Code:  # 選択？
        retStr += " selected "
      retStr += ">"
      retStr += MstRec.Name
      retStr += "</option>"

    return retStr

###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice010/', MainHandler)
], debug=True)
