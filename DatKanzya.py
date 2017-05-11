# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class DatKanzya(db.Model):
  ByotoCD           = db.IntegerProperty()                    # 病棟CD
  KanzyaSex         = db.IntegerProperty()                    # 性別 1:男 2:女
  Hizuke            = db.DateTimeProperty(auto_now_add=False) # 日付(対象月１日の日付）
  KanzyaCD          = db.IntegerProperty()                    # CD
  Name              = db.StringProperty(multiline=False)      # 患者名
  Kana              = db.StringProperty(multiline=False)      # かな名

  # 一覧取得 病棟,年月,性別指定
  def GetList(self,ByotoCD,Nengetu,KanzyaSex):

    Sql =  "SELECT * FROM " + self.__class__.__name__
    Sql +=  " Where ByotoCD     = " + str(ByotoCD) # 病棟
    Sql +=  "  And  KanzyaSex   = " + str(KanzyaSex) # 性別
    Sql +=  "  And  Hizuke      = DATE('" + Nengetu.replace("/","-")  + "-01"  + "')" # 日付

    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      Rec = {}
    else:
      Rec  = Snap.fetch(Snap.count())
      sorted(Rec, key=lambda DatKanzya: DatKanzya.Kana) # かな名でソート

    return Rec

  # レコード取得 病棟,年月,患者
  def GetRec(self,ByotoCD,KanzyaCD,Nengetu):
    
    Sql =  "SELECT * FROM " + self.__class__.__name__
    Sql +=  " Where ByotoCD     = " + str(ByotoCD) # 病棟
    Sql +=  "  And  Hizuke      = DATE('" + Hizuke.replace("/","-")  + "-01')"
    Sql +=  "  And  KanzyaCD    = " + str(KanzyaCD)  # 患者
    Snap = db.GqlQuery(Sql) # 読込
    Rec  = Snap.fetch(Snap.count())

    return Rec

  # レコード削除 病棟,患者,日付指定
  def DelRec(self,DatMeisai):

    Sql =  "SELECT * FROM " + self.__class__.__name__
    Sql +=  " Where ByotoCD     = " + str(DatMeisai.ByotoCD)
    Sql +=  "  And  Hizuke      = DATE('" + DatMeisai.Hizuke.strftime('%Y-%m-%d') + "')"
    Sql +=  "  And  KanzyaCD    = " + str(DatMeisai.KanzyaCD)
    Snap = db.GqlQuery(Sql)
    for Rec in Snap:
      Rec.delete()
    return
  
  # レコード追加
  def AddRec(self,DatMeisai):
    self.DelRec(DatMeisai) # 既存削除
    DatMeisai.put() # 追加
    return
