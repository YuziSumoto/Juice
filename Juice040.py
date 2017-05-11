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

from DatKaribarai import *   # 仮払いデータ

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

    # パラメタ受け取り
    Byoto      = self.request.get('Byoto')
    Nengetu    = self.request.get('Nengetu')
    Kubun      = self.request.get('Sex')

    # coolie 保存
    cookieStr = 'Nengetu=' + Nengetu + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    cookieStr = 'Byoto=' + Byoto + ';'
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    cookieStr = 'Kubun=' + Kubun + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    # 画面セット
    Rec['ByotoCD'] = Byoto
    Rec['Byoto']   = MstByoto().GetRec(Byoto).Name
    Rec['Nengetu'] = Nengetu

    if Kubun == "1":
      Rec['Seibetu']  = "男"
    else:
      Rec['Seibetu']  = "女"

    Rec['Data']  = self.DataSet(Rec)

    template_values = {
      'Rec'   : Rec,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice040.html')
    self.response.out.write(template.render(path, template_values))

#-----------------------------------------------------------------------------
  def post(self):   # ボタン押下時

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Rec = {}

    if self.request.get('BtnKettei')  != '': # 決定押下時
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        LblMsg = u"更新完了しました。"
        self.DBSet()
        self.redirect("/Juice020/") # 前画面に戻る
        return

    # Cookie受け取り
    Byoto     = self.request.cookies.get('Byoto')
    Nengetu   = self.request.cookies.get('Nengetu')

    # 画面セット
    Rec['ByotoCD']   = Byoto
    Rec['Byoto']     = MstByoto().GetRec(Byoto).Name
    Rec['Nengetu']   = Nengetu

    ParaNames = self.request.arguments()  # 再表示用
    for ParaName in ParaNames: # 前画面項目引き渡し
      Rec[ParaName]    = self.request.get(ParaName)
#    Rec['Data']  = self.DataSet(Rec)

    template_values = {
      'Rec'   : Rec,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice040.html')
    self.response.out.write(template.render(path, template_values))

###############################################################################
#--------------------------------------------------------------------------------
  def DataSet(self,Rec):  # 入力領域設定

    RecMeisai = DatKaribarai().GetRec(int(Rec['ByotoCD']),Rec['Nengetu'])

    RetStr = ""

    if RecMeisai == []: # レコード無し
      LastDay = datetime.date(int(Rec['Nengetu'][0:4]), int(Rec['Nengetu'][5:7]), 1) - datetime.timedelta(days=1)
      Rec['TxtHizuke1'] =  LastDay.strftime('%m/%d') # 前月最終日
#      Rec['TxtHizuke2'] =  "12/15" # 中間日
    else:
      for Ctr in range(1,4):  # １～３
        if getattr(RecMeisai,"Hizuke"  + str(Ctr)) != None:
          Rec['TxtHizuke'  + str(Ctr)]  = getattr(RecMeisai,"Hizuke"  + str(Ctr)).strftime('%m/%d')
        if getattr(RecMeisai,"Kingaku"  + str(Ctr)) != None:
          Rec['TxtKingaku' + str(Ctr)]  = getattr(RecMeisai,"Kingaku"  + str(Ctr))

    return

#--------------------------------------------------------------------------------
  def ChkInput(self):   # 入力チェック

    KubunName = [u"区分名",u"当初",u"中間",u"追加"] # エラーMSG表示用

    LblMsg = ""
    ErrFlg = True
    Nengetu   = self.request.cookies.get('Nengetu') # 年(12月の場合本当は前年だけどどうせ３１日

    for Ctr in range(1,4):  # １～３
      if self.request.get('TxtHizuke' + str(Ctr)) != "":  # 日付チェック
        Hizuke  = Nengetu[0:5]  # yyyy/
        Hizuke += str(self.request.get('TxtHizuke' + str(Ctr))) # dd/mm
        if common.CheckDate(self,Hizuke) == False:  # 日付としてＮＧ？
          LblMsg = KubunName[Ctr] + u"仮払い日付が正しくありません。"
          break # チェック中断
      if self.request.get('TxtKingaku' + str(Ctr)) != "": # 金額チェック
        Kingaku = str(self.request.get('TxtKingaku'  + str(Ctr)))
        if Kingaku.isdigit() == False: # 数値じゃねぇ！
          LblMsg = KubunName[Ctr] + u"仮払い金額が正しくありません。"
          break # チェック中断
    else:  # ループ終了→エラー無し
      ErrFlg = False

    return (ErrFlg,LblMsg)

#--------------------------------------------------------------------------------
  def  DBSet(self):  # DB保存


    ByotoCode   = int(self.request.cookies.get('Byoto'))  # 病棟CD
    Nengetu      = self.request.cookies.get('Nengetu')
    
    DatKaribarai().DelRec(ByotoCode,Nengetu) # レコード削除

    RecMeisai = DatKaribarai()
    RecMeisai.ByotoCode   = ByotoCode           # 病棟CD
    Hizuke = Nengetu + "/01"     # 日付(対象月１日の日付）
    RecMeisai.Hizuke      = datetime.datetime.strptime(Hizuke, '%Y/%m/%d')

    for Ctr in range(1,4):
      if self.request.get('TxtHizuke' + str(Ctr)) != "": # 日付入力あり？
        if Ctr >= 2: # 当初仮払い以外？
          Hizuke  = Nengetu[0:5]  # yyyy/
        elif str(self.request.get('TxtHizuke1'))[0:2] == "12":  # 当初が１２月なら
          Hizuke = str(int(Nengetu[0:4]) - 1) + "/" # 去年
        else:
          Hizuke  = Nengetu[0:5]  # yyyy/
        Hizuke += str(self.request.get('TxtHizuke' + str(Ctr))) # dd/mm
        setattr(RecMeisai,"Hizuke"  + str(Ctr),datetime.datetime.strptime(Hizuke, '%Y/%m/%d'))

      if self.request.get('TxtKingaku' + str(Ctr)) != "": # 金額入力あり？
        setattr(RecMeisai,"Kingaku" + str(Ctr),int(self.request.get('TxtKingaku' + str(Ctr))))


    RecMeisai.put()  # 保存

    return

###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice040/', MainHandler)
], debug=True)
