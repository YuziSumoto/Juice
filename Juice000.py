#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

from MstUser   import *   # 使用者マスタ

class MainHandler(webapp2.RequestHandler):

  @login_required

###############################################################################
  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:  # 登録済みユーザ以外は拒否！
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnLogout')  != '':
      self.redirect(users.create_logout_url(self.request.uri))
      return

    template_values = {'LblMsg': ""}
    path = os.path.join(os.path.dirname(__file__), 'Juice000.html')
    self.response.out.write(template.render(path, template_values))

###############################################################################
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Juice000/', MainHandler)
], debug=True)
