# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class MstByoto(db.Model):
  Code              = db.IntegerProperty()                    # CD
  Name              = db.StringProperty(multiline=False)      # 病棟名
  Kigo              = db.StringProperty(multiline=False)      # 記号

  def GetAllCD(self):

    Sql =  "SELECT * FROM MstByoto"
    Sql += " Order By Code"
    Snap = db.GqlQuery(Sql)
    Rec = Snap.fetch(Snap.count())

    return Rec

  def GetRec(self,Code):

    if Code == "" or Code == "None" or Code == None: # 条件指定なし
      return False

    Sql =  "SELECT * FROM MstByoto"
    Sql += " Where Code = " + str(Code)
    Snap = db.GqlQuery(Sql)
    if Snap.count() == 0:
      Rec = False
    else:
      Rec = Snap.fetch(1)[0]

    return Rec

  def DelRec(self,Code):

    Sql =  "SELECT * FROM MstByoto"
    Sql += " Where Code = " + str(Code)
    Snap = db.GqlQuery(Sql).fetch(10) # １件以上無いはずだが念のため
    for Rec in Snap:
      Rec.delete()

    return


