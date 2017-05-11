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
from MstKanzya import *   # 患者マスタ

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    strTable  =  self.TableSet()

    template_values = {'StrTable':strTable,
      'LblMsg': ""
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice910.html')
    self.response.out.write(template.render(path, template_values))
#=============================================================================
  def post(self):   # ボタン押下時

    LblMsg = ""

    Rec = {} # 画面受け渡し用領域
    ParaNames = self.request.arguments()
    for ParaName in ParaNames: # 前画面項目引き渡し
      Rec[ParaName]    = self.request.get(ParaName)

    if self.request.get('BtnSelect')  != '':
      MstRec = MstKanzya().GetRec(int(self.request.get('BtnSelect')))
      Rec["TxtCode"] = MstRec.Code
      Rec["TxtName"] = MstRec.Name
      Rec["TxtKana"] = MstRec.Kana
      Rec["OptSeibetu" + str(MstRec.Sex)] = "checked" # 性別

      if MstRec.YukoFlg == True:
        Rec["ChkYuko"] = "Checked"


    if self.request.get('BtnKousin')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        MstKanzya().DelRec(int(self.request.get('TxtCode')))
        self.DataAdd()
        LblMsg = "更新しました"
        Rec = {} # 更新完了なら画面初期化

    strTable  =  self.TableSet()

    template_values = {
      'Rec'     :Rec,
      'StrTable':strTable,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice910.html')
    self.response.out.write(template.render(path, template_values))

####################################################################################################

#  テーブルセット
  def TableSet(self):

    retStr = ""

    Snap = MstKanzya().GetAllKana("") # 全患者

    for Rec in Snap:

      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン（患者コード)
      retStr += "<input type='submit' value = '"
      retStr += "{0:010d}".format(Rec.Code)
      retStr += "' name='BtnSelect"
      retStr += "' style='width:100px'>"
      retStr += "</TD>"

      retStr += "<TD>"    # 患者名
      if Rec.Sex == 1:
        retStr += "<font color=blue>"
      else:
        retStr += "<font color=red>"

      retStr += Rec.Name
      retStr += "</fot></TD>"

      retStr += "<TD>"    # かな名
      retStr += Rec.Kana
      retStr += "</TD>"

      retStr += "<TD>"    # 無効フラグ
      if Rec.YukoFlg == False:
        retStr += u"無効"
      retStr += "</TD>"

      retStr += "</TR>"

    return retStr

#--------------#
#-入力チェック #
#--------------#
  def ChkInput(self):   # 入力チェック

    ErrFlg = True
    LblMsg = ""

    if self.request.get('TxtCode').isdigit() == False:
      LblMsg = "コードが数値として認識できません。"
    elif self.request.get('TxtName') == "":
      LblMsg = "利用者名を入力してください。"
    elif self.request.get('TxtKana') == "":
      LblMsg = "かな名を入力してください。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

#----------#
# ＤＢ更新 #
#----------#
  def DataAdd(self):

    DynaData = MstKanzya()
    DynaData.Code     = int(self.request.get('TxtCode'))
    DynaData.Name     = self.request.get('TxtName')
    DynaData.Kana     = self.request.get('TxtKana')

    DynaData.Sex      = int(self.request.get('OptSeibetu'))

    if  self.request.get('ChkYuko') == "Checked":
      DynaData.YukoFlg     = True
    else:
      DynaData.YukoFlg     = False

    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/Juice910/', MainHandler)
], debug=True)
