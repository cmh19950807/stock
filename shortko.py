import requests
import json
import datetime
import time
import yaml

#한국 투자

with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
URL_BASE = _cfg['URL_BASE']

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN
    
def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_current_price(code="005930"):
    """현재가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHKST01010100"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    }
    res = requests.get(URL, headers=headers, params=params)
    return int(res.json()['output']['stck_prpr'])

def get_target_price(code="005930"):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
    stck_hgpr = int(res.json()['output'][1]['stck_hgpr']) #전일 고가
    stck_lwpr = int(res.json()['output'][1]['stck_lwpr']) #전일 저가
    target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.3
    return target_price

def get_stock_balance():
    """주식 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8434R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    send_message(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stock_dict[stock['pdno']] = stock['hldg_qty']
            send_message(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주")
            time.sleep(0.1)
    send_message(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
    time.sleep(0.1)
    send_message(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
    time.sleep(0.1)
    send_message(f"총 평가 금액: {evaluation[0]['tot_evlu_amt']}원")
    time.sleep(0.1)
    send_message(f"=================")
    return stock_dict

def get_balance():
    """현금 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8908R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "005930",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    res = requests.get(URL, headers=headers, params=params)
    cash = res.json()['output']['ord_psbl_cash']
    send_message(f"주문 가능 현금 잔고: {cash}원")
    return int(cash)

def buy(code="005930", qty="1"):
    """주식 시장가 매수"""  
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0802U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매수 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매수 실패]{str(res.json())}")
        return False

def sell(code="005930", qty="1"):
    """주식 시장가 매도"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0801U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        send_message(f"[매도 성공]{str(res.json())}")
        return True
    else:
        send_message(f"[매도 실패]{str(res.json())}")
        return False


## New 함수- 기울기 구하기 
def get_avr_rate(code="005930",numb=1):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    sum=0
    for i in range(1,int(numb)+1):
        sum=sum+ int(res.json()['output'][i-1]['stck_clpr'])-int(res.json()['output'][i]['stck_clpr']) 
        ##print(int(res.json()['output'][i-1]['stck_oprc']),' and ',int(res.json()['output'][i]['stck_oprc']) )
        ##print(int(res.json()['output'][i-1]['stck_oprc'])-int(res.json()['output'][i]['stck_oprc']) )
        ##print(i,': ',int(res.json()['output'][i]['stck_oprc']))
    if numb==0:
        avr_price=0;
    else:
        avr_price =sum/numb
    return avr_price

##numb max data=29  29이상 이면 error
## New 함수- 평균값 구하기 

def get_avr_price(code="005930",numb=1):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    sum=0
    for i in range(1,int(numb)+1):
        sum=sum+ int(res.json()['output'][i]['stck_clpr']) 
        ##print(i,': ',int(res.json()['output'][i]['stck_oprc']))
    if numb==0:
        avr_price=int(res.json()['output'][0]['stck_clpr'])
    else:
        avr_price =sum/numb
    return avr_price



def get_yesterday_price(code="005930",numb=1):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)

    return int(res.json()['output'][1]['stck_clpr'])


def get_hi_price(code="005930",numb=1):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    
    return int(res.json()['output'][numb]['stck_hgpr']) 


# 자동매매 시작
try:
    ACCESS_TOKEN = get_access_token()

    #  005930 :삼성전자   035720:카카오
    ##symbol_list = ["005930","035720","000660","069500","035420"]

    # 판매 희망하지 않으면 List에서 out 
    symbol_list = ["302430","089980","109820","195940","035720"] 
    ##symbol_list = ["005930"] # 매수 희망 종목 리스트
    bought_list = [] # 매수 완료된 종목 리스트
    send_list = []
    total_cash = get_balance() # 보유 현금 조회
    stock_dict = get_stock_balance() # 보유 주식 조회
    for sym in stock_dict.keys():
        ##bought_list.append(sym)
        pass

    ##dead code
    nosendlist=['035720']


    list_for_nas=[]
    sell_list_diff=[]

    for x in symbol_list:
        a=[x,999,0,0,0,0,0,0,0,0   ,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,999999,0]
        #s[24]보다 크면 안 산다 (min), s[25]작으면 판다.(max)
        b=[x,0,0,0,0]
        # 사고 판 금액 
        list_for_nas.append(a)
        sell_list_diff.append(b)
    
    ## 구매가 판매 가 선택
    for s in list_for_nas:
        if s[0]=="005930":
            s[24]=99999
            s[25]=0


            print("---------------------")
    buy_sw=True
    sell_sw=True
    by_pass=False

    target_buy_count = 100 # 매수할 종목 수
    buy_percent = 0.90 # 종목당 매수 금액 비율
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
    soldout = False

    counter=0
    counterSet=1
    fristcount=1
    beforstate=0
    currentstate=0
    print('구매 가능 가격: ',buy_amount, '총 금액: ',total_cash)

    if total_cash>100000:
        target_buy_count = 100
        print("구매 희망")
    else:
        target_buy_count = 0
        print("판매 희망")

    print('구매 가능 금액 :',total_cash)

    send_message("===국내 주식 자동매매 프로그램을 시작합니다===")
    while True:
        stt=time.time()


        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
        t_sell = t_now.replace(hour=23, minute=10, second=0, microsecond=0)
        t_exit = t_now.replace(hour=23, minute=30, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        """
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("주말이므로 프로그램을 종료합니다.")
            break
        """
        ## 남은 수량 매도 불필요
        '''
        if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
            for sym, qty in stock_dict.items():
                sell(sym, qty)
            soldout == True
            bought_list = []
            stock_dict = get_stock_balance()
        '''



        ##우선 순위 전일 대비 증가 종목 있음?
        upbyyesday=0;
        for sym in symbol_list:
            current_price = get_current_price(sym)
            yes_price=get_yesterday_price(sym) 
            if (current_price>=yes_price):
                upbyyesday=1
        if upbyyesday==1:
            print('전일 대비 증가 종목 있음')
        else:
            print('증가 종목 없음')

        if (t_start < t_now < t_sell):  # AM 09:05 ~ PM 03:15 : 매수
            print("구매 정보")
            for sym in symbol_list:
                if len(bought_list) < target_buy_count:
                    
                    current_price = get_current_price(sym)
                    target_price = get_target_price(sym)
                    yes_price=get_yesterday_price(sym)  
                    hi20_price=get_hi_price(sym,20)

                    slewrate20=0
                    slewrate10=0
                    slewrate5=0
                    case1=0
                    case2=0
                    case3=0
                    canbuy=0
                    min10=999999
                    min5=9999999
                    max20=0
                    canbuy=0
                    avg5=0
                    avg10=0
                    case4=0
                    case5=0
                    case6=0



                    for s in list_for_nas:
                        if s[0]==sym:
                            if(round(counter%counterSet,3)==0):
                                #변동 가격 대입 
                                for i in range(3,21):
                                    s[23-i]=s[22-i]
                                s[2]=current_price
                                #최저가
                                if s[22]> current_price:
                                    s[22]=current_price
                                #최고가
                                if s[21]< current_price:
                                    s[21]=current_price

                            slewrate20=s[2]-s[20]
                            slewrate10=s[2]-s[11]
                            slewrate5=s[2]-s[7]
                            avg5=(s[3]+s[4]+s[5]+s[6]+s[7])/5
                            avg10=(s[3]+s[4]+s[5]+s[6]+s[7]+s[8]+s[9]+s[10]+s[11]+s[12])/10
                            for  i in range(2,20):
                                if s[i]>max20:
                                    max20=s[i]
                            for  i in range(2,9):
                                if s[i]<min10:
                                    min10=s[i]
                            
                                #값 부족으로 기울기 20 대체값
                            if (counter<counterSet*22):
                                slewrate20=s[13]-s[2]

                            ## 20 평균 기울기 음수  and  10일 평균 기울기 양수  and  5일 평균 기울기 양수 and 제자리 걸음 후 가벼운 상승시 구매 방지
                            case1=( (slewrate20<0)and(current_price>=avg5)and(current_price>=avg10) ) and (current_price*1.005>=min10)
                            
                            # 최초값 안정화 이후 and  정기 입력 값 보다 크고 정기값은 상승 중 일 때 원하는 
                            case3=( (counter>counterSet*12) and (current_price>=s[2])) and (current_price<=s[24])
                            
                            # 당일 최고가 대비 1.5% 감소
                            case2=(current_price<=s[21]*0.985)

                            case4=(upbyyesday==0) or((upbyyesday==1)and(current_price>=yes_price))

                            case5=(max20-current_price>=current_price*0.99)

                            case6=( (current_price>=min10*1.02) ) and (counter>counterSet*12)

                            canbuy=(case1 and case3 and case4 and (case2 or case5)) or case6

                            print(s[0],'||현재 가격: ',current_price,'||변동',": ",round((current_price-s[2])/current_price*100,3),'%',' 1min diff:',round((s[2]-s[3])/current_price*100,3),'%','   ',"||변화=>",s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9])
                            if canbuy==1:
                                if case1:
                                    print("하락 후 상승 중 이므로 구매 희망 ")

                    if (canbuy):
                        buy_qty = 0  # 매수할 수량 초기화
                        lisk=1
                        #추가 구매 갯수

                        #구매 갯수
                        buy_qty = int(buy_amount*lisk // current_price)
                        
                        if buy_qty > 0:
                            ##send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                            send_message(f"{sym} 목표가 달성 매수를 시도합니다.")
                            result = buy(sym, buy_qty)
                            
                            if result:
                                soldout = False
                                bought_list.append(sym)
                                for s in list_for_nas:
                                    if s[0]==sym:
                                        s[1]=current_price
                                target_buy_count=0
                                counter=0
                                get_stock_balance()
                    time.sleep(1)
            time.sleep(1)

        if (t_start < t_now < t_sell):  # PM 03:15 ~ PM 03:20 : 일괄 매도
            print("판매 정보")
            ##if soldout == False:
        


            for sym, qty in stock_dict.items():
                
                if target_buy_count>10:
                    continue
                
                stock_dict = get_stock_balance()
                current_price = get_current_price(sym)
                yes_price=get_yesterday_price(sym)  


                cansell=0
                slewrate20=0
                slewrate10=0
                slewrate5=0
                case0=0
                case1=0
                case2=0
                case3=0
                case4=0

                for s in list_for_nas:
                    if s[0]==sym:
                        '''
                        for x in nosendlist:
                            if x==sym:
                                print('yes')
                                continue
                        '''
                        #구매정보에 구매 값 없으면 현재 값 대입
                        if s[1]==999:
                            s[1]=current_price
                        if target_buy_count==0:
                            if(round(counter%counterSet,3)==0):
                                for i in range(3,21):
                                    s[23-i]=s[22-i]
                                s[2]=current_price
                        slewrate20=s[2]-s[20]
                        avg5=(s[3]+s[4]+s[5]+s[6]+s[7])/5
                        avg10=(s[3]+s[4]+s[5]+s[6]+s[7]+s[8]+s[9]+s[10]+s[11]+s[12])/10
                        avg15=(s[3]+s[4]+s[5]+s[6]+s[7]+s[8]+s[9]+s[10]+s[11]+s[12]+s[13]+s[14]+s[15]+s[16]+s[17]  )/15
                        if (counter<counterSet*22):
                            slewrate20=s[2]-s[13]

                    # 하락 중이고 값이 정상적으로 들어 있을 때
                        case0=( ((current_price<= s[2] )and (s[2]<s[3]))and (counter>counterSet*12) ) 
                    #20 평균 기울기가 0에 가까워지면 판매
                        case1=( ((slewrate20<=current_price*0.005)or (avg15>=current_price)) and(avg10>=current_price)and (avg5>=current_price))
                    #목표 지점 도달
                        case2=( (current_price>=s[1]*1.01) and avg10>=current_price ) or( (current_price>=s[1]*1.02) and avg5>=current_price)
                    # 하락 시 판매
                        case3=(current_price<s[1]*0.99) or (current_price<=s[25])

                        case4=(s[6]>=current_price*1.02)or (s[5]>=current_price*1.02) or (s[4]>=current_price*1.02) or (s[3]>=current_price*1.02) or (s[2]>=current_price*1.02) 

                        cansell=( (case1 or case2 or case3 or case4 ) and case0)
                        
                        
                        #Testing
                        #cansell=0

                        print(s[0],'||now:',current_price,' ||구매 가격 대비 변화:',round((current_price-s[1])/current_price*100,3),'%','|| 1min 변동',": ",round((s[2]-s[3])/current_price*100,3),'%'," ||변화=>",s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9])

                



                        if(cansell):
                                
                                result=sell(sym, qty)
                                print('정규 하락 모두 매도 시작')
                                time.sleep(1)
                                if result:
                                    print('정규 하락 모두 매도 완료')
                                    soldout = False
                                    bought_list.append(sym)
                                    send_list.append(sym)
                                    get_stock_balance()
                                    target_buy_count=100
                                    counter=0
                                time.sleep(1)

        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            send_message("프로그램을 종료합니다.")
            break

        endt=time.time()
        # one cycle 시간
        sttoendtime=round(endt-stt,3)
        #  divide 0 방지 코드
        if sttoendtime==0:
            sttoendtime=1

        
        print(sttoendtime,"걸림")
        if (t_start < t_now < t_sell):
            counter=counter+1
        else:
            print('장 시작 전 1분 sleep')
            time.sleep(60)
        print('counter: ',counter)
        

        if (counter==5):
            counterSet=int((60/sttoendtime)-0.3)
            print('카운터 고정: ',counterSet)
            # dead code ?
            fristcount=counterSet

        #  divide 0 방지 코드
        if counterSet<1:
            counterSet=1
        
        print("one run time",sttoendtime,'counterSet: ',(counterSet))
        print("")
        print('')
        
except Exception as e:
    send_message(f"[오류 발생]{e}")
    time.sleep(1)