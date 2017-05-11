# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class MstKanzya(db.Model):
  Code              = db.IntegerProperty()                    # CD
  Name              = db.StringProperty(multiline=False)      # 患者名
  Kana              = db.StringProperty(multiline=False)      # かな名
  Sex               = db.IntegerProperty()                    # 性別 1:男 2:女
  BirthDay          = db.DateTimeProperty(auto_now_add=False) # 生年月日
  YukoFlg           = db.BooleanProperty()                    # 有効フラグ

  def GetAllCD(self,YukoFlg):

    Sql =  "SELECT * FROM MstKanzya"
    if YukoFlg != "":
      Sql += " Where YukoFlg = " + YukoFlg
    Sql += " Order By Code"
    Snap = db.GqlQuery(Sql)
    Rec = Snap.fetch(Snap.count())

    return Rec

  def GetAllKana(self,YukoFlg):

    Sql =  "SELECT * FROM MstKanzya"
    if YukoFlg != "":
      Sql += " Where YukoFlg = " + YukoFlg
    Sql += " Order By Kana,Code"
    Snap = db.GqlQuery(Sql)
    Rec = Snap.fetch(Snap.count())

    return Rec

  def GetSeibetuKana(self,Sex,YukoFlg):

    Sql =  "SELECT * FROM MstKanzya"
    Sql += " Where Sex = " + str(Sex)
    if YukoFlg != "":
      Sql += " And YukoFlg = " + YukoFlg
    Sql += " Order By Kana,Code"
    Snap = db.GqlQuery(Sql)
    Rec = Snap.fetch(Snap.count())

    return Rec

  def GetSeibetuKensaku(self,Sex,YukoFlg,Zyoken):

    Sql =  "SELECT * FROM MstKanzya"
    Sql += " Where Sex = " + str(Sex)
    if YukoFlg != "":
      Sql += " And YukoFlg = " + YukoFlg
    Sql += " Order By Kana,Code"
    Query = db.GqlQuery(Sql)
    Snap = Query.fetch(Query.count())
    RetList = []
    for Rec in Snap:
      if  Rec.Kana[0:len(Zyoken)] == Zyoken:
        RetList.append(Rec)
      else:
        pass

    return RetList

  def GetRec(self,Code):

    if Code == "" or Code == "None" or Code == None: # 条件指定なし
      return False

    Sql =  "SELECT * FROM MstKanzya"
    Sql += " Where Code = " + str(Code)
    Snap = db.GqlQuery(Sql)
    if Snap.count() == 0:
      Rec = False
    else:
      Rec = Snap.fetch(1)[0]

    return Rec

  def DelRec(self,Code):

    Sql =  "SELECT * FROM MstKanzya"
    Sql += " Where Code = " + str(Code)
    Snap = db.GqlQuery(Sql).fetch(10) # １件以上無いはずだが念のため
    for Rec in Snap:
      Rec.delete()

    return
