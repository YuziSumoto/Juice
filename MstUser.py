# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class MstUser(db.Model):
  Name              = db.StringProperty(multiline=False)      # ユーザ名

  def ChkUser(self,Name):

    if Name == "Dummy": # ダミーでのログオンは不可！
      return False

    Sql  =  "SELECT * FROM MstUser"
    Query = db.GqlQuery(Sql)
    if Query.count() == 0: # 0件時はダミー追加
      DynaUser =  MstUser()    # システム導入時のみダミー追加
      DynaUser.Name = "Dummy"  
      DynaUser.put()           # 管理コンソールでメールアドレス登録!

    Sql  =  "SELECT * FROM MstUser"
    Sql  +=  " Where Name = '" + Name + "'"
    Query = db.GqlQuery(Sql)
    Snap = Query.fetch(Query.count())

    if Query.count() == 0: # 無し
      RetFlg = False
    else:
      RetFlg = True

    return RetFlg

