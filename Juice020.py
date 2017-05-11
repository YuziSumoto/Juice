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

from DatKanzya     import *   # 対象患者データ
from DatMeisai     import *   # 明細データ
from DatKaribarai  import *   # 仮払いデータ

class Parameter():
    def __init__(self):
        self.ByotoCD = ""
        self.Byoto   = ""
        self.Nengetu = ""
        self.Kubun   = ""
        self.Seibetu = ""

class MainHandler(webapp2.RequestHandler):

  @login_required
###############################################################################
  def get(self):  # 初期表示

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:  # 登録済みユーザ以外は拒否！
      self.redirect(users.create_logout_url(self.request.uri))
      return

    LblMsg = ""

#    Rec = {}
    param = Parameter()
    # パラメタ受け取り
    if self.request.get('Byoto') != "": # パラメタ指定
      param.ByotoCD   = self.request.get('Byoto')
      param.Nengetu = self.request.get('Nengetu')
      param.Kubun   = self.request.get('Sex')
      # coolie 保存
      common.CookieAdd(self,'Byoto='   + param.ByotoCD)
      common.CookieAdd(self,'Nengetu=' + param.Nengetu)
      common.CookieAdd(self,'Kubun='   + param.Kubun)
    else:
      # Cookie受け取り
      param.ByotoCD   = self.request.cookies.get('Byoto')
      param.Nengetu = self.request.cookies.get('Nengetu')
      param.Kubun   = self.request.cookies.get('Kubun')
    
    # 画面セット
    param.Byoto  = MstByoto().GetRec(param.ByotoCD).Name

    Meisai = DatKanzya().GetList(param.ByotoCD,param.Nengetu,param.Kubun) # 患者リスト取得
    self.DataSet(param,Meisai)      # 合計セット

    template_values = {
      'Rec'        : param,
      'Snap'       : Meisai,
      'Karibarai'  : DatKaribarai().GetRec(param.ByotoCD,param.Nengetu),
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice020.html')
    self.response.out.write(template.render(path, template_values))
#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    # Cookie受け取り
    Byoto   = self.request.cookies.get('Byoto')
    Nengetu = self.request.cookies.get('Nengetu')
    Kubun   = self.request.cookies.get('Kubun')

    if self.request.get('BtnAdd')  != '':
      parm = "?Byoto=" + Byoto
      parm += "&Nengetu=" + Nengetu
      parm += "&Kubun=" + Kubun
      self.redirect("/Juice030/" + parm)
      return

    if self.request.get('BtnKaribarai')  != '':
      parm = "?Byoto=" + Byoto
      parm += "&Nengetu=" + Nengetu
      parm += "&Sex=" + Kubun
      self.redirect("/Juice040/" + parm)
      return

    for param in self.request.arguments(): 
      if "BtnSel" in param:  # 明細ボタン？
        parm = "?Byoto=" + Byoto
        parm += "&Nengetu=" + Nengetu
        parm += "&Kubun=" + Kubun
        parm += "&KanzyaCD=" + param.replace("BtnSel","")
        self.redirect("/Juice050/" + parm)
        return
      if "BtnDel" in param:  # 明細ボタン？
        RecKanzya = DatKanzya()
        RecKanzya.ByotoCD = int(Byoto)
        RecKanzya.Hizuke = datetime.datetime.strptime(Nengetu  + "/01", '%Y/%m/%d')
        RecKanzya.KanzyaCD = int(param.replace("BtnDel",""))
        RecKanzya.DelRec(RecKanzya)
        LblMsg = u"削除しました"

    # 画面セット
    param = Parameter()  # 画面パラメタ初期化
    param.ByotoCD = self.request.cookies.get('Byoto')
    param.Nengetu = self.request.cookies.get('Nengetu')
    param.Kubun   = self.request.cookies.get('Kubun')
    param.Byoto   = MstByoto().GetRec(param.ByotoCD).Name

    Meisai = DatKanzya().GetList(param.ByotoCD,param.Nengetu,param.Kubun) # 患者リスト取得
    LblMsg = self.DataSet(param,Meisai)      # 合計セット

    template_values = {
      'Rec'        : param,
      'Snap'       : Meisai,
      'Karibarai'  : DatKaribarai().GetRec(param.ByotoCD,param.Nengetu),
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice020.html')
    self.response.out.write(template.render(path, template_values))
###############################################################################
#--------------------------------------------------------------------------------
  def DataSet(self,param,Meisai):  # データ部設定

    WkMeisai = DatMeisai()

    for Rec in Meisai: # 全患者処理
      Goukei = 0
      SnapMeisai = WkMeisai.GetList(param.ByotoCD,param.Nengetu,param.Kubun,Rec.KanzyaCD)
      for RecMeisai in SnapMeisai:
        Goukei += RecMeisai.AM
        Goukei += RecMeisai.PM

      Rec.Goukei= Goukei

    return
###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice020/', MainHandler)
], debug=True)
