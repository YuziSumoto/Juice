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
      self.Nengetu = ""
      self.Kubun   = ""
      self.Seibetu = ""
      self.KanzyaCD = ""
    def RequestGet(self,Request):
      self.ByotoCD   = Request.request.get('Byoto')
      self.Nengetu   = Request.request.get('Nengetu')
      self.Kubun     = Request.request.get('Kubun')
      self.KanzyaCD  = Request.request.get('KanzyaCD')
      return
    def CookieAdd(self,Request):
      common.CookieAdd(Request,'Byoto='     + self.ByotoCD)
      common.CookieAdd(Request,'Nengetu='   + self.Nengetu)
      common.CookieAdd(Request,'Kubun='     + self.Kubun)
      common.CookieAdd(Request,'KanzyaCD='  + self.KanzyaCD)
      return
    def CookieGet(self,Request):
      self.ByotoCD   = Request.request.cookies.get('Byoto')
      self.Nengetu   = Request.request.cookies.get('Nengetu')
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
    if self.request.get('Byoto') != "": # パラメタ指定？
      param.RequestGet(self)# パラメタ取得
      param.CookieAdd(self)# coolie保存
    else:
      param.CookieGet(self)# Cookie受け取り

    # 画面セット
    param.Byoto   = MstByoto().GetRec(param.ByotoCD).Name
    param.Kanzya  = MstKanzya().GetRec(param.KanzyaCD).Name

    Midashi = self.MidashiSet(param) # 日付項目セット
    self.DataSet(param,Midashi)      # データセット
    AMKei,PMKei = DatMeisai().GetGoukei(param) # 合計取得
    param.AMKei = AMKei
    param.PMKei = PMKei
    param.Goukei = AMKei + PMKei
    
 #   Snap    = self.DataSet(param,Midashi)
    template_values = {
      'SnapIdo'    : self.GetIdo(),
      'Snap'       : Midashi,
      'Rec'        : param,
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice050.html')
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
      if "BtnAM" in InParam:  # 明細ボタン？
        DatMeisai().Kousin(param,InParam.replace("BtnAM",""),"AM")
        LblMsg = u"更新しました"
      if "BtnPM" in InParam:  # 明細ボタン？
        DatMeisai().Kousin(param,InParam.replace("BtnPM",""),"PM")
        LblMsg = u"更新しました"
      if "IdoZyoho" in InParam:  # 明細ボタン？
        LblMsg = u"更新しましたa" + InParam

    # 画面セット
    param.Byoto   = MstByoto().GetRec(param.ByotoCD).Name
    param.Kanzya  = MstKanzya().GetRec(param.KanzyaCD).Name

    Midashi = self.MidashiSet(param) # 日付項目セット
    self.DataSet(param,Midashi)      # データセット

    AMKei,PMKei = DatMeisai().GetGoukei(param) # 合計取得
    param.AMKei = AMKei
    param.PMKei = PMKei
    param.Goukei = AMKei + PMKei

    template_values = {
      'SnapIdo'    : self.GetIdo(),
      'Snap'       : Midashi,
      'Rec'        : param,
      'LblMsg'     : LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice050.html')
    self.response.out.write(template.render(path, template_values))

###############################################################################
#---------------------------------------------
  def MidashiSet(self,param):  # 日付部設定

    Midashi =  []
    Hizuke   = datetime.datetime.strptime(param.Nengetu.replace("/","-")  + "-01", '%Y-%m-%d') # １日
    LastDay  = calendar.monthrange(Hizuke.year,Hizuke.month)[1] # 当月末日
    for Count in range(1,LastDay + 1):
      Naiyo ={}
      Naiyo["Day"] = Count
      Naiyo["Text"] = str(Count) + u"日"
      if datetime.datetime.strptime(param.Nengetu + "/" + str(Count), '%Y/%m/%d').weekday() == 6: # 日曜日
        Naiyo["Style"] = "bgcolor='yellow'"
      else:
        Naiyo["Style"] = "Class='Midashi'"
      Midashi.append(Naiyo)

    return Midashi
#--------------------------------------------------------------------------------
  def DataSet(self,param,Midashi):  # データ部設定

    WkMeisai = DatMeisai()
    for Rec in Midashi: # １日単位で処理
      Hizuke = param.Nengetu + "/" + str(Rec["Day"])
      DataRec = WkMeisai.GetRec(param.ByotoCD,param.KanzyaCD,Hizuke)
      if DataRec == {}: # データ無し
        Rec["AM"] = ""
        Rec["PM"] = ""
        Rec["IdoZyoho"] = ""
      else:
        if  DataRec.AM == 0:
          Rec["AM"] = ""
        else:
          Rec["AM"] = str(DataRec.AM)
        if  DataRec.PM == 0:
          Rec["PM"] = ""
        else:
          Rec["PM"] = str(DataRec.PM)
        Rec["IdoZyoho"] = DataRec.IdoZyoho

    return
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
    ('/Juice050/', MainHandler)
], debug=True)
