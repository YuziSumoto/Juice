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
      self.Kubun   = ""
      self.Hizuke  = "" # 初期値：当日
      self.Byoto   = "" # 病棟マスタより
    def RequestGet(self,Request):
      self.ByotoCD   = Request.request.get('ByotoCD')
      self.Kubun     = Request.request.get('Kubun')
      return
    def CookieAdd(self,Request):
      common.CookieAdd(Request,'ByotoCD=' + self.ByotoCD)
      common.CookieAdd(Request,'Kubun='   + self.Kubun)
      common.CookieAdd(Request,'Hizuke='  + self.Hizuke)
      return
    def CookieGet(self,Request):
      self.ByotoCD   = Request.request.cookies.get('ByotoCD')
      self.Kubun     = Request.request.cookies.get('Kubun')
      self.Hizuke    = Request.request.cookies.get('Hizuke')
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
    if self.request.get('ByotoCD') != "": # パラメタ指定
      param.RequestGet(self)# パラメタ取得
      param.Hizuke = datetime.datetime.now().strftime('%Y/%m/%d') # 当日日付
      param.CookieAdd(self)# coolie保存
    else:
      param.CookieGet(self)# Cookie受け取り
    
    param.Byoto  = MstByoto().GetRec(param.ByotoCD).Name #病棟名セット
    Nengetu = param.Hizuke[0:7] # yyyy/mm

    Meisai = DatKanzya().GetList(param.ByotoCD,Nengetu,param.Kubun) # 患者リスト取得
    param.AMKei,param.PMKei = self.DataSet(param,Meisai)      # データセット
    param.Goukei = param.AMKei + param.PMKei

    template_values = {
      'Rec'        : param, 
      'Snap'       : Meisai,
      'Karibarai'  : DatKaribarai().GetRec(param.ByotoCD,Nengetu),
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice100.html')
    self.response.out.write(template.render(path, template_values))
#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    param = Parameter()
    param.CookieGet(self)# Cookie受け取り
    param.Byoto  = MstByoto().GetRec(param.ByotoCD).Name # 病棟名セット

    if self.request.get('BtnAdd')  != '':
      parm = "?Byoto=" + Byoto
      parm += "&Nengetu=" + Nengetu
      parm += "&Sex=" + Kubun
      self.redirect("/Juice030/" + parm)
      return

    for InParam in self.request.arguments(): 
      if "BtnAM" in InParam:  # 明細ボタン？
        param.KanzyaCD = InParam.replace("BtnAM","")
        param.Nengetu = param.Hizuke[0:7] # yyyy/mm
        DatMeisai().Kousin(param,param.Hizuke[8:10],"AM")
        LblMsg = u"更新しました"
      if "BtnPM" in InParam:  # 明細ボタン？
        param.KanzyaCD = InParam.replace("BtnPM","")
        param.Nengetu = param.Hizuke[0:7] # yyyy/mm
        DatMeisai().Kousin(param,param.Hizuke[8:10],"PM")
        LblMsg = u"更新しました"

    Nengetu = param.Hizuke[0:7] # yyyy/mm

    Meisai = DatKanzya().GetList(param.ByotoCD,Nengetu,param.Kubun) # 患者リスト取得
    param.AMKei,param.PMKei = self.DataSet(param,Meisai)      # データセット
    param.Goukei = param.AMKei + param.PMKei

    template_values = {
      'Rec'        : param, 
      'Snap'       : Meisai,
      'Karibarai'  : DatKaribarai().GetRec(param.ByotoCD,Nengetu),
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice100.html')
    self.response.out.write(template.render(path, template_values))
###############################################################################
#--------------------------------------------------------------------------------
  def DataSet(self,param,Meisai):  # データ部設定

    WkMeisai = DatMeisai()
    AMKei = 0
    PMKei = 0

    for Rec in Meisai: # 全患者処理
      DataRec = WkMeisai.GetRec(param.ByotoCD,Rec.KanzyaCD,param.Hizuke)
      if DataRec == {}: # データ無し
        Rec.AM = 0
        Rec.PM = 0
      else:
        AMKei += DataRec.AM
        Rec.AM = str(DataRec.AM)
        PMKei += DataRec.PM
        Rec.PM = str(DataRec.PM)

    return AMKei,PMKei
###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice100/', MainHandler)
], debug=True)
