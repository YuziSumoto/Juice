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
from MstKanzya import *   # 患者マスタ

from DatKanzya import *   # 患者マスタ

from DatMeisai import *   # 明細データ

class Parameter():
    def __init__(self):
      self.ByotoCD = ""
      self.Nengetu = ""
      self.Kubun   = ""
      self.Zyoken   = ""
    def RequestGet(self,Request):
      self.ByotoCD   = Request.request.get('Byoto')
      self.Nengetu   = Request.request.get('Nengetu')
      self.Kubun     = Request.request.get('Kubun')
      return
    def CookieAdd(self,Request):
      common.CookieAdd(Request,'Byoto='     + self.ByotoCD)
      common.CookieAdd(Request,'Nengetu='   + self.Nengetu)
      common.CookieAdd(Request,'Kubun='     + self.Kubun)
      return
    def CookieGet(self,Request):
      self.ByotoCD   = Request.request.cookies.get('Byoto')
      self.Nengetu   = Request.request.cookies.get('Nengetu')
      self.Kubun     = Request.request.cookies.get('Kubun')
      return

class MainHandler(webapp2.RequestHandler):

  @login_required
###############################################################################
  def get(self):  # 初期表示

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:  # 登録済みユーザ以外は拒否！
      self.redirect(users.create_logout_url(self.request.uri))
      return

    LblMsg = ""

    # パラメタ受け取り
    param = Parameter()
    if self.request.get('Byoto') != "": # パラメタ指定？
      param.RequestGet(self)# パラメタ取得
      param.CookieAdd(self)# coolie保存
    else:
      param.CookieGet(self)# Cookie受け取り

    param.Zyoken = u"ｱ"
    SnapKanzya = MstKanzya().GetSeibetuKensaku(param.Kubun,"",param.Zyoken)

    template_values = {
      'Rec'    : param,
      'Snap'   : SnapKanzya,
      'LblMsg' : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice030.html')
    self.response.out.write(template.render(path, template_values))

#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg =""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    param = Parameter()
    # Cookie受け取り
    param.CookieGet(self)# Cookie受け取り

    for InParam in self.request.arguments(): 
      if "BtnSel" in InParam:  # 選択
        RecKanzya = DatKanzya()
        RecKanzya.ByotoCD    = int(param.ByotoCD)
        RecKanzya.KanzyaSex  = int(param.Kubun)
        RecKanzya.Hizuke     = datetime.datetime.strptime(param.Nengetu + "/01", '%Y/%m/%d')
        RecKanzya.KanzyaCD   = int(InParam.replace("BtnSel",""))
        RecMst = MstKanzya().GetRec(int(InParam.replace("BtnSel","")))
        RecKanzya.Kana       = RecMst.Kana
        RecKanzya.Name       = RecMst.Name
        RecKanzya.AddRec(RecKanzya) # レコード保存

        LblMsg = u"追加しました。(" + InParam.replace("BtnSel","") + ")"
    param.Zyoken = self.request.get('Zyoken')
    SnapKanzya = MstKanzya().GetSeibetuKensaku(param.Kubun,"", param.Zyoken)

    template_values = {
      'Rec'    : param,
      'Snap'   : SnapKanzya,
      'LblMsg' : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice030.html')
    self.response.out.write(template.render(path, template_values))

###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice030/', MainHandler)
], debug=True)
