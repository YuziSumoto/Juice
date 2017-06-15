#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###################
#　ジュース一覧印刷
###################

import webapp2

from google.appengine.ext.webapp import template

import datetime
import xlwt

import common

from MstUser       import *   # 使用者マスタ
from MstByoto      import *   # 病棟マスタ
from DatKanzya     import *   # 患者データ
from DatMeisai     import *   # 明細データ
from DatKaribarai  import *   # 仮払いデータ

class MainHandler(webapp2.RequestHandler):
  def get(self):

    # シートセット
    WorkBook =  self.SheetSet(self.request.get('Byoto'),self.request.get('Nengetu'),self.request.get('Kubun')) 

    # HTMLヘッダセット
    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    FileName = self.request.get('Nengetu').replace("/","") + ".xls"
    self.response.headers['Content-disposition'] = 'attachment; filename="' + str(FileName) + '"'
    WorkBook.save(self.response.out)
###############################################################################
  def SheetSet(self,Byoto,Nengetu,Kubun):   # シートセット

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    SheetName = ["区分性別変換",u"男",u"女"]

    WorkSheet = ["性別ワークシート保存領域"]
    AMSum = ["性別ＡＭ合計保存領域"]
    PMSum = ["性別ＰＭ合計保存領域"]

    for Ctr in range(1,3): # 2回ループ

      WorkSheet.append(WorkBook.add_sheet(SheetName[Ctr]))  # 新規Excelシート

      self.SetPrintParam(WorkSheet[Ctr])  # 用紙サイズ等セット
      self.SetColRowSize(WorkSheet[Ctr]) # 行,列サイズセット
      self.SetTitle(WorkSheet[Ctr],Nengetu)      # 固定部分セット

      RetAMSum,RetPMSum = self.SetData(WorkSheet[Ctr],Byoto,Nengetu,Ctr) # データセット

      AMSum.append(RetAMSum)
      PMSum.append(RetPMSum)

      self.SetGoukei(WorkSheet[Ctr],Nengetu)     # 合計欄セット
      self.SetKaribarai(WorkSheet[Ctr],Byoto,Nengetu)  # 仮払い・残額セット

    for Ctr in range(1,3): # 2回ループ
      self.SetAMPMSum(WorkSheet[Ctr],AMSum,PMSum,Ctr)

    return  WorkBook
#-----------------------------------------------------------------------------#
  def SetData(self,WorkSheet,Byoto,Nengetu,Kubun):  # データセット

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    Style2 =  self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    Font1 = xlwt.Font() # Create the Font
    Font1.height       = 12 * 20  # 20倍するとポイントになる
    Style2.font         = Font1

    Style3 =  self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    Font2 = xlwt.Font() # Create the Font
    Font2.height       = 6 * 20  # 20倍するとポイントになる
    Style3.font        = Font2

    StyleRed =  self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    Font3 = xlwt.Font() # Create the Font
    Font3.heigh        = 6 * 20  # 20倍するとポイントになる
    Font3.colour_index = 0x35  # 20倍するとポイントになる
    StyleRed.font        = Font3

    SnapKanzya = DatKanzya().GetList(int(Byoto),Nengetu,Kubun)

    Ctr = 0

    AMSum     = [0] * 32 # 性別合計AM
    PMSum     = [0] * 32 # 性別合計PM

    Row = 1
    WkMeisai = DatMeisai()

    for RowCtr in range(0,33): # 空行も枠線は引く！
      Row += 2
      if RowCtr >= len(SnapKanzya):
        WorkSheet.write_merge(Row,Row +1 ,1,1,"",Style)
        WorkSheet.write(Row,2,"",Style)
        for DayCtr in range(1,32): # 日別ループ
          OutCol = 4 + (DayCtr - 1) * 2
          WorkSheet.write(Row,OutCol    ,"",Style)
          WorkSheet.write(Row,OutCol + 1,"",Style)
          WorkSheet.write_merge(Row+1,Row+1,OutCol,OutCol + 1,"",Style)
        WorkSheet.write(Row,3,"",Style)
        WorkSheet.write(Row + 1,3,"",Style3)
      else: # 明細無し
        RecKanzya = SnapKanzya[RowCtr]  # 患者ループ
        OutStr = "%08d" % RecKanzya.KanzyaCD # 患者コード
        WorkSheet.write_merge(Row,Row +1 ,1,1,OutStr,Style)
        WorkSheet.write(Row,2,RecKanzya.Name,Style)

        Goukei = 0
        LastIdo = ""

        for DayCtr in range(1,32): # 日別ループ
          OutCol = 4 + (DayCtr - 1) * 2
          Hizuke = Nengetu + "/" + str(DayCtr)
          DataRec = WkMeisai.GetRec(Byoto,RecKanzya.KanzyaCD,Hizuke)
          if DataRec == {}: # データ無し
            WorkSheet.write(Row,OutCol    ,"",Style)
            WorkSheet.write(Row,OutCol + 1,"",Style)
            WorkSheet.write_merge(Row+1,Row+1,OutCol,OutCol + 1,"",Style)
          else:
            if  DataRec.AM == 0:
              WorkSheet.write(Row,OutCol    ,"",Style)
            else:
              AMSum[DayCtr] += DataRec.AM
              Goukei += DataRec.AM
              WorkSheet.write(Row,OutCol    ,str(DataRec.AM),Style)
            if  DataRec.PM == 0:
              WorkSheet.write(Row,OutCol + 1,"",Style)
            else:
              PMSum[DayCtr] += DataRec.PM
              Goukei += DataRec.PM
              WorkSheet.write(Row,OutCol + 1,str(DataRec.PM),Style)
            WorkSheet.write_merge(Row+1,Row+1,OutCol,OutCol + 1,DataRec.IdoZyoho,Style3)
            if DataRec.IdoZyoho == u"退院":
              LastIdo = "退院"
            elif  DataRec.IdoZyoho == u"預かり開始":
              LastIdo = u"預かり開始"
            elif  DataRec.IdoZyoho == u"預かり中止":
              LastIdo = u"＊"
            elif  DataRec.IdoZyoho == u"３病棟へ":
              LastIdo = u"□"
            elif  u"へ" in DataRec.IdoZyoho:
              LastIdo = u"△"

        WorkSheet.write(Row,3,str(Goukei),Style)
        if len(LastIdo) > 2:
          WorkSheet.write(Row + 1,3,LastIdo,Style3)
        else:
          WorkSheet.write(Row + 1,3,LastIdo,Style)

    return (AMSum,PMSum)
#=============================================================================
  def SetAMPMSum(self,WorkSheet,AMSum,PMSum,Kubun): # 性別合計セット

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    # 性別合計表示

    for Ctr in range(1,3):
      Row = 68 + Ctr
      Goukei = 0
      for  DayCtr in range(1,32): # 31日分
        Col = 2 + (DayCtr * 2)
        WorkSheet.write(Row,Col    ,str(AMSum[Ctr][DayCtr]),Style)
        WorkSheet.write(Row,Col + 1,str(PMSum[Ctr][DayCtr]),Style)
        Goukei += AMSum[Ctr][DayCtr] + PMSum[Ctr][DayCtr]
      WorkSheet.write(Row,3    ,str(Goukei),Style) 

    return

#------------------------------------------------------------------------------#
  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定
#    WorkSheet.set_paper_size_code(13) # B5
    WorkSheet.set_paper_size_code(9) # A4
    WorkSheet.set_portrait(1) # 縦
    WorkSheet.top_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
    WorkSheet.fit_num_pages = 1
    return
#------------------------------------------------------------------------------#
  def SetColRowSize(self,WorkSheet):  # 行,列サイズセット

    ColWidth = ["列の幅",3,10,19,6]
    ColScale = 300

    for i in range(1,5):
      WorkSheet.col(i - 1).width = int(ColWidth[i] * ColScale)

    for i in range(5,67): # 5～66
      WorkSheet.col(i - 1).width = int(3 * ColScale)

    WorkSheet.col(67 - 1).width = int(14 * ColScale)
    WorkSheet.col(68 - 1).width = int(16 * ColScale)

    RowScale = 20

    for i in range(1,75): # 1～74
      WorkSheet.row(i - 1).height_mismatch = True
      WorkSheet.row(i - 1).height = 14 * RowScale
    WorkSheet.row(75 - 1).height_mismatch = True
    WorkSheet.row(75 - 1).height = 37 * RowScale

    return
#------------------------------------------------------------------------------#
  def SetGoukei(self,WorkSheet,Nengetu):  # 合計欄セット

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    COL = []
    ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ALPHAS = ' ' + ALPHA
    for d1 in ALPHAS:
      for d2 in ALPHA:
        COL.append((d1 + d2).strip())
    
    WorkSheet.write(71,3 ,xlwt.Formula(COL[3] + '69+' + COL[3] + '70'),Style);
    WorkSheet.write(72,3 ,xlwt.Formula(COL[3] + '72 * 100'),Style);
    for i in range(1, 32): # 日別列
      Col = i * 2 + 2
      Siki =  COL[Col] + '70+' + COL[Col] + '71+'         # 計算式 AM男 + AM女 +
      Siki += COL[Col + 1] + '70+' + COL[Col + 1] + '71'  # 計算式 PM男 + AM女
      WorkSheet.write_merge(71,71,Col,Col + 1,xlwt.Formula(Siki),Style)     # 合計本数

      Siki = xlwt.Formula(COL[Col] + '72 * 100')              # 計算式
      WorkSheet.write_merge(72,72,Col,Col + 1,Siki,Style)     # 出勤金額

    return
#------------------------------------------------------------------------------#
  def SetKaribarai(self,WorkSheet,Byoto,Nengetu):  # 仮払い・残額セット

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    COL = []
    ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ALPHAS = ' ' + ALPHA
    for d1 in ALPHAS:
      for d2 in ALPHA:
        COL.append((d1 + d2).strip())

    RecKaribarai = DatKaribarai().GetRec(Byoto,Nengetu)

    DayCol = (4,32,56)
    for Ctr in range(3):
      if RecKaribarai == []: # 無し？
        StrDay = ""
        Kingaku= 0
      else:
        StrDay  = getattr(RecKaribarai,"Hizuke" + str(Ctr + 1)).strftime('%m/%d')
        Kingaku = u"￥" + str(getattr(RecKaribarai,"Kingaku" + str(Ctr + 1)))
      WorkSheet.write_merge(0,0,DayCol[Ctr] + 0,DayCol[Ctr] + 1,StrDay,Style)     # 合計本数
      WorkSheet.write_merge(0,0,DayCol[Ctr] + 2,DayCol[Ctr] + 4,Kingaku,Style)     # 合計本数

    return
#------------------------------------------------------------------------------#
  def SetTitle(self,WorkSheet,Nengetu):  # 固定部分セット

    Hizuke =  u"平成" + str(datetime.datetime.now().year - 1988) + u"年" 
    Hizuke += str(datetime.datetime.now().month) + u"月"
    Hizuke += str(datetime.datetime.now().day) + u"日"

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)

    WorkSheet.write(0,67 ,Hizuke)
    WorkSheet.write_merge(0,0,2,3,u"当初仮払金額",Style)
    WorkSheet.write_merge(0,0,27,31,u"中間仮払金額",Style)
    WorkSheet.write_merge(0,0,53,55,u"追加仮払",Style)

    WorkSheet.write_merge(1,2,1,1,u"患者番号",Style)
    WorkSheet.write(1,2,u"名前",Style)
    WorkSheet.write(2,2,u"あいうえお順",Style)
    WorkSheet.write(1,3,u"",Style)
    WorkSheet.write(2,3,u"",Style)

    Row = 1

    StyleYellow = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
    StyleYellow.pattern = pattern

    for i in range(1,32): # 日付
      # 日付チェック
      Hizuke = Nengetu + "/" + "%02d" % i
      if common.CheckDate(self,Hizuke) == False: # yyyy/mm/ + 日付
        break  # 当月終了

      Col = 2 +(i*2)

      if datetime.datetime.strptime(Hizuke, '%Y/%m/%d').weekday() == 6: # 日曜日
        WorkSheet.write_merge(Row,Row,Col,Col + 1,str(i),StyleYellow)
        WorkSheet.write(Row + 1,Col    ,"AM",StyleYellow)
        WorkSheet.write(Row + 1,Col + 1,"PM",StyleYellow)
      else:
        WorkSheet.write_merge(Row,Row,Col,Col + 1,str(i),Style)
        WorkSheet.write(Row + 1,Col    ,"AM",Style)
        WorkSheet.write(Row + 1,Col + 1,"PM",Style)

    # 灰色背景色
    StyleLG = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER)
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
    StyleLG.pattern = pattern

    Col = 0
    for i in range(1,34): # 行番号
      Row = 1+(i*2)
      if i % 2 == 0:
        WorkSheet.write_merge(Row,Row + 1,Col,Col,str(i),Style)
      else:
        WorkSheet.write_merge(Row,Row + 1,Col,Col,str(i),StyleLG)

    Col = 1
    Row = 69
    WorkSheet.write_merge(Row,Row + 3,Col,Col,u"日計",Style)
    WorkSheet.write(73,Col,u"累計",Style)
    WorkSheet.write_merge(74,74,Col,Col + 1,u"病棟担当者押印か署名",Style)
    Col = 3
    WorkSheet.write_merge(74,74,Col,Col,u"",Style)
    for i in range(1,32): # 日付
      # 日付チェック
      Hizuke = Nengetu + "/" + "%02d" % i
      if common.CheckDate(self,Hizuke) == False: # yyyy/mm/ + 日付
        break  # 当月終了
      Col = 2 +(i*2)
      WorkSheet.write_merge(74,74,Col,Col + 1,u"",Style)

    Col = 1
    WorkSheet.write_merge(75,75,Col,Col + 12,
      u"*　10日、20日（土日祝の場合は前後でします）に事務所からチェックに伺います。",Style)

    Col = 2
    WorkSheet.write(69,Col,u"男性本数計",Style)
    WorkSheet.write(70,Col,u"女性本数計",Style)
    WorkSheet.write(71,Col,u"本数合計",Style)
    WorkSheet.write(72,Col,u"出勤金額",Style)
    WorkSheet.write(73,Col,u"当日残高",Style)

    return
#------------------------------------------------------------------------------#
  def SetStyle(self,Top,Bottom,Right,Left,Vert,Horz):  # セルスタイルセット

    Style = xlwt.XFStyle()
    Border = xlwt.Borders()
    if Top == "THIN":
      Border.top     = xlwt.Borders.THIN
    elif Top == "DOTTED":
      Border.top     = xlwt.Borders.DOTTED

    if Bottom == "THIN":
      Border.bottom  = xlwt.Borders.THIN
    elif Bottom == "DOTTED":
      Border.bottom     = xlwt.Borders.DOTTED

    if   Left == "THIN":
      Border.left    = xlwt.Borders.THIN
    elif Left == "DOTTED":
      Border.left    = xlwt.Borders.DOTTED

    if   Right == "THIN":
      Border.right   = xlwt.Borders.THIN
    elif Right == "DOTTED":
      Border.right   = xlwt.Borders.DOTTED

    Style.borders = Border
    
    Alignment      = xlwt.Alignment()

    if Vert != False:
      Alignment.vert = Vert
    if Horz != False:
      Alignment.horz = Horz

    Style.alignment = Alignment

    return Style

###############################################################################
app = webapp2.WSGIApplication([
    ('/Juice025/', MainHandler)
], debug=True)
