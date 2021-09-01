import os
import sys
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errcode import *
from PyQt5.QtTest import *
from config.kiwoomType import *






class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스 입니다")

        self.realType = RealType()

        #### EVENT_LOOP 모음 ####
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()

        #######변수모음######
        self.account_num = None
        self.account_stock_dict = {}
        self.un_account_stock_dict = {}
        self.portfolio_stock = {}
        self.jango_dict = {}

        #####스크린번호 모음 #####
        self.screen_basic_info = "0"
        self.screen_start_stop_stock = "1000"
        self.screen_my_info = "2000"
        self.screen_caculation_stock = "4000"
        self.screen_real_stock = "5000"
        self.screen_meme_stock = "6000"





        #######계좌관련변수#######
        self.use_money = 0
        self.use_money_percent = 0.5
        #######종목분석용 변수#####
        self.calcul_data = []

        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slot()

        self.signal_login_commConnect()
        self.get_accout_info()
        self.detail_account_info() #예수금상세현황요청
        self.detail_account_mystock() #계좌평가잔고내역요청
        self.un_concluded_account() # 미체결 요청

        self.read_code() #저장된 종목들 불러온다.
        self.screen_num_set() #스크린번호 할당





        #장 시작시간이냐 아니냐
        self.dynamicCall("SetRealReg(QString,QString,QString,QString)", self.screen_start_stop_stock, '',self.realType.REALTYPE['장시작시간']['장운영구분'],"0")
        for code in self.portfolio_stock.keys():
            screen_num = self.portfolio_stock[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString,QString,QString,QString)", screen_num, code, fids,"1")
            print("실시간 등록 코드 : %s , 스크린번호 : %s, 번호 : %s" %(code,screen_num,fids))
        self.calculator_fnc()


    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
    #### EVENT #####
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
        self.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.real_data_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)

    def chejan_slot(self, sGubun, nItemCnt, sFidList):
        if int(sGubun) == 0:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()
            orgin_order_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])
            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            order_quan = int(order_quan)
            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            order_price = int(order_price)
            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chegual_quan = int(not_chegual_quan)
            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)
            chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])
            if chegual_quan == '':
                chegual_quan = 0
            else:
                chegual_quan = int(chegual_quan)
            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if order_number not in self.un_account_stock_dict.keys():
                self.un_account_stock_dict.update({order_number:{}})
            self.un_account_stock_dict[order_number].update({'종목코드': sCode})
            self.un_account_stock_dict[order_number].update({'주문번호': order_number})
            self.un_account_stock_dict[order_number].update({'종목명': stock_name})
            self.un_account_stock_dict[order_number].update({'주문상태': order_status})
            self.un_account_stock_dict[order_number].update({'주문수량': order_quan})
            self.un_account_stock_dict[order_number].update({'주문가격': order_price})
            self.un_account_stock_dict[order_number].update({'미체결수량': not_chegual_quan})
            self.un_account_stock_dict[order_number].update({'원주문번호': orgin_order_num})
            self.un_account_stock_dict[order_number].update({'주문구분': order_gubun})
            self.un_account_stock_dict[order_number].update({'주문/체결시간': chegual_time_str})
            self.un_account_stock_dict[order_number].update({'체결가': chegual_price})
            self.un_account_stock_dict[order_number].update({'체결량': chegual_quan})
            self.un_account_stock_dict[order_number].update({'현재가': current_price})
            self.un_account_stock_dict[order_number].update({'(최우선)매도호가': first_sell_price})
            self.un_account_stock_dict[order_number].update({'(최우선)매수호가': first_buy_price})

            print(self.un_account_stock_dict)


        elif int(sGubun) == 1:
            account_num = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()
            current_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))
            stock_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)
            like_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)
            buy_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))
            total_buy_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)
            meme_gubun = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]
            first_sell_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))
            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})
            self.jango_dict[sCode].update({"현재가":current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]
                self.dynamicCall(("SetRealRemove(QString,QString"), self.portfolio_stock[sCode]['스크린번호'],sCode)

    #송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName,sTrCode,msg):
        print("스크린 : %s 요청이름 :%s 코드 : %s --- %s"%(sScrNo,sRQName,sTrCode,msg))

    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")



    def real_data_slot(self, sCode, sRealType, sRealData):
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QSting,int)",sCode,fid)
            if value == '0':
                print("장 시작 전")
            elif value == "3":
                print("장이 시작되었습니다.")
            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
            elif value == "4":
                print("3시30분 장 종료")
                for code in self.portfolio_stock.keys():
                    self.dynamicCall("SetRealRemove(String,String)",self.portfolio_stock[code]['스크린번호'])
                QTest.qWait(3000)





                self.file_delete()
                self.calculator_fnc()

                sys.exit()
        elif sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['체결시간'])
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['현재가'])
            b = abs(int(b))
            c = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))
            d = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d)
            e = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))
            f = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))
            g = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))
            h = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))
            i = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))
            j = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))
            k = self.dynamicCall("GetCommRealData(QString, int)", sCode,self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock:
                self.portfolio_stock.update({sCode:{}})
            self.portfolio_stock[sCode].update({'체결시간':a})
            self.portfolio_stock[sCode].update({'현재가':b})
            self.portfolio_stock[sCode].update({'전일대비':c})
            self.portfolio_stock[sCode].update({'등락율':d})
            self.portfolio_stock[sCode].update({'(최우선)매도호가':e})
            self.portfolio_stock[sCode].update({'(최우선)매수호가':f})
            self.portfolio_stock[sCode].update({'거래량':g})
            self.portfolio_stock[sCode].update({'누적거래량':h})
            self.portfolio_stock[sCode].update({'고가':i})
            self.portfolio_stock[sCode].update({'시가':j})
            self.portfolio_stock[sCode].update({'저가':k})

            print(self.portfolio_stock[sCode])
            #계좌잔고내역에는 있고 오늘 산 잔고 내역에는 없는
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                asd = self.account_stock_dict[sCode]
                meme_rate = (b-asd['매입가'])/asd['매입가']*100

                if asd['매매가능수량'] > 0 and (meme_rate > 10 or meme_rate <-5):
                    order_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                        ["신규매도", self.portfolio_stock[sCode]['주문용스크린번호'], self.account_num, 2,
                        sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ''])
                    if order_success == 0 :
                        print("매도주문 전달 성공")
                        del self.account_stock_dict[sCode]

                    else :
                        print("매도주문 전달 실패")


            elif sCode in self.jango_dict.keys():
                jd = self.jango_dict[sCode]
                meme_rate = (b-jd['매입단가'])/jd['매입단가']*100
                if jd['주문가능수량'] > 0 and (meme_rate > 10 or meme_rate < -5):
                    order_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                        ["신규매도", self.portfolio_stock[sCode]['주문용스크린번호'], self.account_num, 2,
                         sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])
                    if order_success == 0:
                        self.logging.Logger.debug("매도주문전달 성공")
                    else:
                        self.logging.Logger.debug("매도주문전달 실패")

            elif d > 1 and sCode not in self.jango_dict.keys():
                result = (self.use_money * 0.1) / e
                quantity = int(result)
                order_success = self.dynamicCall(
                    "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                    ["신규매수", self.portfolio_stock[sCode]['주문용스크린번호'], self.account_num, 1,
                     sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ''])
                if order_success == 0:
                    self.logging.logger.debug("매수주문전달 성공")
                else:
                    self.logging.logger.debug("매수주문전달 실패")

            not_meme_list = list(self.un_account_stock_dict)

            for order_num in not_meme_list:
                code = self.un_account_stock_dict[order_num]['종목코드']
                meme_price = self.un_account_stock_dict[order_num]['주문가격']
                not_quantity = self.un_account_stock_dict[order_num]['미체결수량']
                order_gubun = self.un_account_stock_dict[order_num]['주문구분']
                if order_gubun == "매수" and not_quantity > 0  and e > meme_price:
                    order_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                        ["신규매도", self.portfolio_stock[sCode]['주문용스크린번호'], self.account_num, 3,
                         sCode, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num])
                    if order_success == 0:
                        self.logging.Logger.debug("매수 취소 전달 성공")
                    else:
                        self.logging.Logger.debug("매수 취소 전달 실패")
                elif not_quantity == 0:
                    del self.un_account_stock_dict[order_num]




    def login_slot(self, errCode):
        print(errors(errCode))
        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec()


    def get_accout_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(";")[0]
        print("나의 보유계좌 번호 %s" % self.account_num) #5427647210

    def detail_account_info(self): ##예수금 받아오는 부분
        print("예수금 요청 부분")
        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String,String,int,String)","예수금상세현황요청","opw00001","0",self.screen_my_info)
        ## SCREEN NUM = 1000(잔고조회용),2000(실시간데이터요청용),3000(주문요청용), 등으로 그룹핑해줌
        ## SCREEN NUM 최대200개 사용 가능 / SCREEN NUM당 최대 100개
        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext='0'):
        print("계좌평가잔고내역요청")
        self.dynamicCall("SetInputValue(String,String", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String", "조회구분", "2")
        self.dynamicCall("CommRqData(String,String,int,String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()



    def un_concluded_account(self, sPrevNext="0"):
        print("미체결요청")
        self.dynamicCall("SetInputValue(QString,QString", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString,QString", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString,QString", "매매구분", "0")
        self.dynamicCall("CommRqData(QString,QString,int,QString)", "미체결요청", "opw10075", sPrevNext,
                             self.screen_my_info)

        self.detail_account_info_event_loop.exec_()



    def trdata_slot(self, sScrNo, sRQName,sTrCode,sRecordName,sPrevNext):
        '''
        tr요청을 받는 구역! 슬롯!
        :param sScrNo: 스크린번호
        :param sRQName: 요청 이름
        :param sTrCode: tr코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음페이지가 있는가?
        :return:
        '''




        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,"예수금")
            print("예수금 %s원" % int(deposit))
            self.use_money = int(deposit) * self.use_money_percent
            self.usemoney = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,"출금가능금액")
            print("출금가능금액 %s원" % int(ok_deposit))



            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            total_buy = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,"총매입금액")
            print("총매입금액 %s원" % int(total_buy))
            total_profit_rate = self.dynamicCall("GetCommData(String,String,int,String)",sTrCode,sRQName,0,"총수익률(%)")
            print("총수익률(%s): %s" %("%", float(total_profit_rate)/100))

            rows = self.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName) #보유종목반환
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'종목명')
                code_nm = code_nm.strip()

                stock_quantity = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"보유수량")
                stock_quantity = int(stock_quantity.strip())

                buy_price = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"매입가")
                buy_price = int(buy_price.strip())

                learn_rate = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"수익률(%)")
                learn_rate = float(learn_rate.strip())

                current_price = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"현재가")
                current_price = int(current_price.strip())

                total_chegual_price = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"매입금액")
                total_chegual_price = int(total_chegual_price.strip())


                possible_quantity = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"매매가능수량")
                possible_quantity = int(possible_quantity.strip())
                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                self.account_stock_dict[code].update({"종목명":code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt +=1




            print("보유종목수 : %s" %cnt)
            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()
        if sRQName == "미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName) #보유종목반환
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString,QString,int,QString0)",sTrCode,sRQName,i,"종목코드")
                code = code.strip()

                code_nm = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'종목명')
                code_nm = code_nm.strip()

                order_status = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'주문상태')
                order_status = order_status.strip()

                order_no = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'주문번호')
                order_no = int(order_no.strip())

                order_quantity = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'주문수량')
                order_quantity = int(order_quantity.strip())

                order_price = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'주문가격')
                order_price = int(order_price.strip())

                order_gubun = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'주문구분')
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

                not_quantity = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'미체결수량')
                not_quantity = int(not_quantity.strip())

                ok_quantity = self.dynamicCall("GetCommData(QString,QString,int,QString)",sTrCode,sRQName,i,'체결량')
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.un_account_stock_dict:
                    pass
                else:
                    self.un_account_stock_dict[order_no] = {}

                nasd = self.not_account_stock_dict[order_no]


                self.un_account_stock_dict[order_no].update({"종목코드": code})
                self.un_account_stock_dict[order_no].update({"종목명": code_nm})
                self.un_account_stock_dict[order_no].update({"주문번호": order_no})
                self.un_account_stock_dict[order_no].update({"주문상태": order_status})
                self.un_account_stock_dict[order_no].update({"주문수량": order_quantity})
                self.un_account_stock_dict[order_no].update({"주문가격": order_price})
                self.un_account_stock_dict[order_no].update({"주문구분": order_gubun})
                self.un_account_stock_dict[order_no].update({"미체결수량": not_quantity})
                self.un_account_stock_dict[order_no].update({"체결량": ok_quantity})
                print("미체결종목 : %s" % self.un_account_stock_dict[order_no])
            self.detail_account_info_event_loop.exit()

        if sRQName == "주식일봉차트조회":

            code = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode,sRQName,0,"종목코드")
            code = code.strip()


            cnt = self.dynamicCall("GetRepeatCnt(QString,QString)",sTrCode,sRQName)


            for i in range(cnt):

                data = []

                current_price = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,"현재가")
                value = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                                 "거래량")
                trading_value = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                         "거래대금")
                date = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                                 "일자")
                start_price = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                                 "시가")
                high_price = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                                 "고가")
                low_price = self.dynamicCall("GetCommData(QString,QString,int,QString)", sTrCode, sRQName, i,
                                                 "저가")
                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())




                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else: #120일 이상
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    print(total_price)
                    moving_average_total_price = total_price / 120 ##120일 이동평균선
                    bottom_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_total_price and moving_average_total_price <= int(self.calcul_data[0][6]):
                        print("오늘 주가가 이평선에 걸쳐있음")
                        bottom_price = True
                        check_price = int(self.calcul_data[0][6])


                    ### 과거 일봉들이 120일 이평선보다 아래에 있는지 확인
                    ### 일봉이 120일 이평선보다 위에 있게되면 계산 진행

                    prev_price = None ##과거 일봉 저가

                    if bottom_price == True:

                        moving_average_prev = 0
                        price_top_moving = False
                        idx = 1
                        while True:

                            if len(self.calcul_data[idx:]) < 120: #120일치가 존재하는지 확인
                                break
                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_prev = total_price / 120
                            if moving_average_prev <= int(self.calcul_data[0][6]) and idx <= 20:
                                price_top_moving = False
                                break
                            elif int(self.calcul_data[0][7]) > moving_average_prev and idx > 20:
                                price_top_moving = True
                                prev_price = int(self.calcul_data[0][7])
                                break

                            idx += 1
                        if price_top_moving == True:
                            if moving_average_total_price > moving_average_prev and check_price > prev_price:
                                pass_success = True
                if pass_success == True:
                    print("조건부 통과")
                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                    f = open("files/condition_stock.txt", "a", encoding="utf-8")
                    f.write("%s\t%s\t%s\n" %(code,code_nm,str(self.calcul_data[0][1])))
                    f.close()
                elif pass_success == False:
                    pass

                self.calcul_data.clear()

                self.calculator_event_loop.exit()




        # 미체결 잔고 확인 opt10075


    def get_code_list_by_market(self, market_code):
        '''
            종목 코드 반환

            :param self:
            :param market_code:
            :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]
        return code_list
    ### 임시 ####
    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("0") #0 : 코스피 8:ETF 10: 코스닥
        print("코스피 갯수 %s" % len(code_list))

        for idx,  code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_caculation_stock)

            print("%s / %s : KOSDAQ Stock Code : %s is updating..." %(idx+1, len(code_list), code))
            self.day_kiwoom_db(code=code)




    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(4500)
        self.dynamicCall("SetInputValue(QString, Qstring)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, Qstring)", "수정주가구분", "1")
        if date != None:
            self.dynamicCall("SetInputValue(QString,QString)","기준일자", date)

        self.dynamicCall("CommRqData(QString,QString,int,QString)","주식일봉차트조회","opt10081",sPrevNext,self.screen_caculation_stock)
        self.calculator_event_loop.exec_()



    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt","r", encoding="utf8")
            lines = f.readlines()


            for line in lines:
                if line != "":
                    ls = line.split("\t")
                    print(ls)
                    stock_code = ls[0]
                    stock_nm = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.portfolio_stock.update({stock_code:{"종목명":stock_nm,"현재가":stock_price}})
            f.close()

    def screen_num_set(self):
        screen_overwrite = []
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        for order_number in self.un_account_stock_dict.keys():
            code = self.un_account_stock_dict[order_number]['종목코드']
            if code not in screen_overwrite:
                screen_overwrite.append(code)
        for code in self.portfolio_stock.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)
            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)
            if (cnt % 50) == 0:
                meme_screen +=1
                self.screen_meme_stock = str(meme_screen)
            if code in self.portfolio_stock.keys():
                self.portfolio_stock[code].update({"스크린번호":str(self.screen_real_stock)})
                self.portfolio_stock[code].update({"주문용스크린번호":str(self.screen_meme_stock)})
            elif code not in self.portfolio_stock.keys():
                self.portfolio_stock.update({code : {"스크린번호":str(self.screen_real_stock),"주문용스크린번호":str(self.screen_meme_stock)}})

            cnt += 1
        print(self.portfolio_stock)
