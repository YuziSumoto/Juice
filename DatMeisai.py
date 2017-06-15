# -*- coding: UTF-8 -*-

from google.appengine.ext import db
import datetime # 日付モジュール
import calendar # 月末取得用

from operator import itemgetter, attrgetter # ソート用モジュール

class DatMeisai(db.Model):    # 
  ByotoCode         = db.IntegerProperty()                    # 病棟CD
  KanzyaSex         = db.IntegerProperty()                    # 性別 1:男 2:女
  Hizuke            = db.DateTimeProperty(auto_now_add=False) # 日付(対象月１日の日付）
  KanzyaCD          = db.IntegerProperty()                    # 患者CD
  IdoZyoho          = db.StringProperty(multiline=False)      # 移動情報
  AM                = db.IntegerProperty()                    # 午前
  PM                = db.IntegerProperty()                    # 午後

  def GetList(self,ByotoCode,Hizuke,KanzyaSex,KanzyaCD): # 一括 病棟,月,性別,患者指定

    Hizuke   = datetime.datetime.strptime(Hizuke.replace("/","-")  + "-01", '%Y-%m-%d')
    LastDay  = calendar.monthrange(Hizuke.year,Hizuke.month)[1]
    Getumatu = datetime.date(Hizuke.year,Hizuke.month, LastDay)

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(ByotoCode)
    Sql +=  "  And  Hizuke      >= DATE('" + Hizuke.strftime('%Y-%m-%d')  + "')"
    Sql +=  "  And  Hizuke      < DATE('" + Getumatu.strftime('%Y-%m-%d') + "')"
    Sql +=  "  And  KanzyaSex      = " + str(KanzyaSex)
    Sql +=  "  And  KanzyaCD    = " + str(KanzyaCD)

    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      return {}

    Rec  = Snap.fetch(Snap.count())
    sorted(Rec, key=attrgetter('Hizuke')) # 日付でソート

    return Rec

  def GetRec(self,ByotoCode,KanzyaCD,Hizuke): # 病棟,患者,日指定

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(ByotoCode)
    Sql +=  "  And  Hizuke      = DATE('" + Hizuke.replace("/","-")  + "')"
    Sql +=  "  And  KanzyaCD    = " + str(KanzyaCD)
    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      Rec = {}
    else:
      Rec  = Snap.fetch(Snap.count())[0]

    return Rec

  def Kousin(self,param,Hizuke,Kubun): # 病棟,患者,日指定

    Hizuke = param.Nengetu + "/" + str(Hizuke)
    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(param.ByotoCD)
    Sql +=  "  And  Hizuke      = DATE('" + Hizuke.replace("/","-")  + "')"
    Sql +=  "  And  KanzyaCD    = " + str(param.KanzyaCD)
    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      Rec = DatMeisai() # 新規追加
      Rec.ByotoCode         = int(param.ByotoCD)   # 病棟CD
      Rec.KanzyaSex         = int(param.Kubun)     # 性別 1:男 2:女
      Rec.Hizuke            = datetime.datetime.strptime(Hizuke, '%Y/%m/%d') # 日付(対象月１日の日付）
      Rec.KanzyaCD          = int(param.KanzyaCD)  # 患者CD
      Rec.AM                = 0                    # 午前
      Rec.PM                = 0                    # 午前
      Rec.IdoZyoho          = ""                   # 移動情報
    else:
      Rec  = Snap.fetch(Snap.count())[0]

    if Kubun == "AM": # 午前
      if  Rec.AM            == 4:
        Rec.AM              = 0
      else:
        Rec.AM              += 1
    else:  # 午後
      if  Rec.PM            == 4:
        Rec.PM              = 0
      else:
        Rec.PM              += 1

    Rec.put()

    return

  def IdoKousin(self,param,Ido): # 移動更新 病棟,患者,日指定

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(param.ByotoCD)
    Sql +=  "  And  Hizuke      = DATE('" + param.Hizuke.replace("/","-")  + "')"
    Sql +=  "  And  KanzyaCD    = " + str(param.KanzyaCD)
    Snap = db.GqlQuery(Sql)

    if Snap.count() == 0:
      Rec = DatMeisai() # 新規追加
      Rec.ByotoCode         = int(param.ByotoCD)   # 病棟CD
      Rec.KanzyaSex         = int(param.Kubun)     # 性別 1:男 2:女
      Rec.Hizuke            = datetime.datetime.strptime(param.Hizuke, '%Y/%m/%d') # 日付(対象月１日の日付）
      Rec.KanzyaCD          = int(param.KanzyaCD)  # 患者CD
      Rec.AM                = 0                    # 午前
      Rec.PM                = 0                    # 午前
    else:
      Rec  = Snap.fetch(Snap.count())[0]
    Rec.IdoZyoho          = Ido                  # 移動情報
    Rec.put()
    return

  def DelRec(self,DatMeisai): # 削除 病棟,患者,日指定

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(DatMeisai.ByotoCode)
    Sql +=  "  And  Hizuke      = DATE('" + DatMeisai.Hizuke.strftime('%Y-%m-%d') + "')"
    Sql +=  "  And  KanzyaCD    = " + str(DatMeisai.KanzyaCD)
    Snap = db.GqlQuery(Sql)
    for Rec in Snap:
      Rec.delete()
    return

  def GetGoukei(self,param): # 病棟,患者,指定月
    
    Hizuke   = datetime.datetime.strptime(param.Nengetu.replace("/","-")  + "-01", '%Y-%m-%d')
    LastDay  = calendar.monthrange(Hizuke.year,Hizuke.month)[1]
    Getumatu = datetime.date(Hizuke.year,Hizuke.month, LastDay)

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where ByotoCode   = " + str(param.ByotoCD)
    Sql +=  "  And  Hizuke      >= DATE('" + Hizuke.strftime('%Y-%m-%d')  + "')"
    Sql +=  "  And  Hizuke      < DATE('" + Getumatu.strftime('%Y-%m-%d') + "')"
    Sql +=  "  And  KanzyaSex      = " + str(param.Kubun)
    Sql +=  "  And  KanzyaCD    = " + str(param.KanzyaCD)

    Snap = db.GqlQuery(Sql)

    AMKei  = 0
    PMKei  = 0

    for Rec in Snap.fetch(Snap.count()):
      AMKei += Rec.AM
      PMKei += Rec.PM

    return AMKei,PMKei

  def GetAllGoukei(self,Hizuke,KanzyaCD): # 病棟,患者,指定月

    Sql =  "SELECT * FROM DatMeisai"
    Sql +=  " Where Hizuke      >= DATE('" + Hizuke.replace("/","-")  + "')"
    Sql +=  "  And  Hizuke      <  DATE('" + Yokugetu.replace("/","-")  + "')"
    Sql +=  "  And  KanzyaCD  = " + str(KanzyaCD)
    Sql +=  "  Order By ByotoCode"
    Snap = db.GqlQuery(Sql)
    RetStr = ""

    if Snap.count() != 0: # データが１件でもあれば
      ByotoCode = Rec.ByotoCD
      ByotoKei  = 0
      for Rec in Snap: # 全データ集計
        if ByotoCode != Rec.ByotoCD: # 病棟変更時
          if RetStr != "":  # 最初の病棟以外
            RetStr += " + "
          RetStr += str(Rec.ByotoCode) + "F " + str(ByotoKei) + u"本"
          ByotoCode != Rec.ByotoCD
          BtotoKei = 0
        ByotoKei += Rec.AM + Rec.PM
      # 最終病棟出力
      if RetStr != "":  # 最初の病棟以外
        RetStr += " + "
        RetStr += str(Rec.ByotoCode) + "F " + str(ByotoKei) + u"本"

    return RetStr
