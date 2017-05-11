#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import webapp2
import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ (利用者チェック用)

import wsgiref.handlers
import os
import csv
from StringIO import StringIO

from MstKanzya import *  # 患者マスタ
import datetime

class MainHandler(webapp2.RequestHandler):

  @login_required # ログインしてないとダメ！

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    template_values = {'Msg': ""
                      }
    path = os.path.join(os.path.dirname(__file__), "juice915.html")
    self.response.out.write(template.render(path, template_values))

  def post(self):

    Msg  = "bbb"

    Sql =  "SELECT * FROM MstKanzya"   # 現データ削除
    Snap = db.GqlQuery(Sql)
    for Rec in Snap:
      Rec.delete()

    rawfile = self.request.get('file')
    csvfile = csv.reader(StringIO(rawfile))
    for row in csvfile:
      if unicode(row[0], 'cp932').isnumeric() == False:
        continue # 数値以外は無視
      if  u"＊" in unicode(row[2], 'cp932'): # ＊付き患者のみ対象
        pass
      else:
        Msg +=  unicode(row[0], 'cp932') + " "
        Rec = MstKanzya(
              Code     = int(unicode(row[0], 'cp932')),
              Name     = unicode(row[2], 'cp932'),
              Kana     = unicode(row[1], 'cp932'),
              Sex      = int(unicode(row[3], 'cp932')),
              YukoFlg  = True
		  )
        Rec.put()
        Msg +=  unicode(row[0], 'cp932') + " "
        Msg +=  unicode(row[12], 'cp932') + " "
        Msg +=  unicode(row[4], 'cp932') + "<BR>"
      
    template_values = {'Msg': Msg
                      }
    path = os.path.join(os.path.dirname(__file__), "juice915.html")
    self.response.out.write(template.render(path, template_values))

    return
  
app = webapp2.WSGIApplication([
    ('/Juice915/', MainHandler)
], debug=True)
