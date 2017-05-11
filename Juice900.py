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
    path = os.path.join(os.path.dirname(__file__), 'Juice900.html')
    self.response.out.write(template.render(path, template_values))
#=============================================================================
  def post(self):   # ボタン押下時

    LblMsg = ""

    Rec = {} # 画面受け渡し用領域
    ParaNames = self.request.arguments()
    for ParaName in ParaNames: # 前画面項目引き渡し
      Rec[ParaName]    = self.request.get(ParaName)

    if self.request.get('BtnSelect')  != '':
      MstRec = MstByoto().GetRec(int(self.request.get('BtnSelect')))
      Rec["TxtCode"] = MstRec.Code
      Rec["TxtName"] = MstRec.Name
      Rec["TxtKigo"] = MstRec.Kigo

    if self.request.get('BtnKousin')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        MstByoto().DelRec(int(self.request.get('TxtCode')))
        self.DataAdd()
        LblMsg = "更新しました"
        Rec = {} # 更新完了なら画面初期化

    strTable  =  self.TableSet()

    template_values = {
      'Rec'     :Rec,
      'StrTable':strTable,
      'LblMsg': LblMsg
      }
    path = os.path.join(os.path.dirname(__file__), 'Juice900.html')
    self.response.out.write(template.render(path, template_values))

####################################################################################################

#  テーブルセット
  def TableSet(self):

    retStr = ""

    Snap = MstByoto().GetAllCD() # 全病棟

    for Rec in Snap:

      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン（コード)
      retStr += "<input type='submit' value = '"
      retStr += "{0:010d}".format(Rec.Code)
      retStr += "' name='BtnSelect"
      retStr += "' style='width:100px'>"
      retStr += "</TD>"

      retStr += "<TD>"    # 病棟名
      retStr += Rec.Name
      retStr += "</fot></TD>"

      retStr += "<TD>"    # 記号
      retStr += Rec.Kigo
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
      LblMsg = "病棟名を入力してください。"
    elif self.request.get('TxtKigo') == "":
      LblMsg = "記号を入力してください。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

#----------#
# ＤＢ更新 #
#----------#
  def DataAdd(self):

    DynaData = MstByoto()
    DynaData.Code     = int(self.request.get('TxtCode'))
    DynaData.Name     = self.request.get('TxtName')
    DynaData.Kigo     = self.request.get('TxtKigo')
    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/Juice900/', MainHandler)
], debug=True)
