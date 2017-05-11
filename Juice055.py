#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import common

import datetime # 日付モジュール

from MstUser       import *   # 使用者マスタ
from MstByoto      import *   # 病棟マスタ
from MstKanzya     import *   # 患者マスタ

from DatKanzya     import *   # 対象患者データ
from DatMeisai     import *   # 明細データ
from DatKaribarai  import *   # 仮払いデータ

class Parameter():
    def __init__(self):
      self.ByotoCD = ""
      self.Byoto   = ""
      self.Hizuke  = ""
      self.Kubun   = ""
      self.Seibetu = ""
      self.KanzyaCD = ""
    def RequestGet(self,Request):
      self.ByotoCD   = Request.request.get('ByotoCD')
      self.Hizuke    = Request.request.get('Hizuke')
      self.Kubun     = Request.request.get('Kubun')
      self.KanzyaCD  = Request.request.get('KanzyaCD')
      return
    def CookieAdd(self,Request):
      common.CookieAdd(Request,'ByotoCD='     + self.ByotoCD)
      common.CookieAdd(Request,'Hizuke='   + self.Hizuke)
      common.CookieAdd(Request,'Kubun='     + self.Kubun)
      common.CookieAdd(Request,'KanzyaCD='  + self.KanzyaCD)
      return
    def CookieGet(self,Request):
      self.ByotoCD   = Request.request.cookies.get('ByotoCD')
      self.Hizuke    = Request.request.cookies.get('Hizuke')
      self.Kubun     = Request.request.cookies.get('Kubun')
      self.KanzyaCD  = Request.request.cookies.get('KanzyaCD')
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

    param = Parameter()
    # パラメタ受け取り
    if self.request.get('ByotoCD') != "": # パラメタ指定？
      param.RequestGet(self)# パラメタ取得
      param.CookieAdd(self)# coolie保存
    else:
      param.CookieGet(self)# Cookie受け取り

    # 画面セット
    param.Byoto   = MstByoto().GetRec(param.ByotoCD).Name
    param.Kanzya  = MstKanzya().GetRec(param.KanzyaCD).Name

    template_values = {
      'SnapIdo'    : self.GetIdo(),
      'Rec'        : param,
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice055.html')
    self.response.out.write(template.render(path, template_values))
#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    param = Parameter()

    # Cookie受け取り
    param.CookieGet(self)# Cookie受け取り

    for InParam in self.request.arguments():
      if "BtnIdo" in InParam:  # 明細ボタン？
        DatMeisai().IdoKousin(param,InParam.replace("BtnIdo",""))
        LblMsg = u"更新しました" + InParam.replace("BtnIdo","")
        self.redirect("/Juice050/") # 前画面に戻る

    # 画面セット
    param.Byoto   = MstByoto().GetRec(param.ByotoCD).Name
    param.Kanzya  = MstKanzya().GetRec(param.KanzyaCD).Name

    template_values = {
      'SnapIdo'    : self.GetIdo(),
      'Rec'        : param,
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice055.html')
    self.response.out.write(template.render(path, template_values))

###############################################################################
#---------------------------------------------
#--------------------------------------------------------------------------------
  def GetIdo(self):  # 移動コンボボックス

    Ido =  ["","入院","退院","預かり開始","預かり中止",
            "３病棟へ","３病棟から",
            "中央病棟へ","中央病棟から",
            "５病棟へ","５病棟から",
            "６病棟へ","６病棟から",
            ]

    return Ido
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice055/', MainHandler)
], debug=True)
