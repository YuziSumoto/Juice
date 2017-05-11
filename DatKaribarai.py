# -*- coding: UTF-8 -*-

from google.appengine.ext import db
import datetime # 日付モジュール

class DatKaribarai(db.Model):
  ByotoCode         = db.IntegerProperty()                    # 病棟CD
  Hizuke            = db.DateTimeProperty(auto_now_add=False) # 対象月１日の日付
  Hizuke1           = db.DateTimeProperty(auto_now_add=False) # 当初刈払日
  Kingaku1          = db.IntegerProperty()                    # 金額
  Hizuke2           = db.DateTimeProperty(auto_now_add=False) # 中間仮払日
  Kingaku2          = db.IntegerProperty()                    # 金額
  Hizuke3           = db.DateTimeProperty(auto_now_add=False) # 追加仮払日
  Kingaku3          = db.IntegerProperty()                    # 金額

  def GetRec(self,ByotoCode,Hizuke): # 病棟,日付指定

    Sql =  "SELECT * FROM DatKaribarai"
    Sql +=  " Where ByotoCode   = " + str(ByotoCode)
    Sql +=  "  And  Hizuke      = DATE('" + Hizuke.replace("/","-")  + "-01')"
    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      Rec = []
    else:
      Rec  = Snap.fetch(Snap.count())[0] # １レコード戻す

    return  Rec
  
  def DelRec(self,ByotoCode,Hizuke): # 病棟,日付,性別指定


    Sql =  "SELECT * FROM DatKaribarai"
    Sql +=  " Where ByotoCode   = " + str(ByotoCode)
    Sql +=  "  And  Hizuke      = DATE('" + Hizuke.replace("/","-")  + "-01')"
    Snap = db.GqlQuery(Sql)

    for Rec in Snap:
      Rec.delete()
    return

