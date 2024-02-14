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


def get_stock_balance1():
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
    evaluation = res.json()['output2'][0]['tot_evlu_amt']
    '''
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
    '''
    return evaluation

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



def get_beforeday_price(code="005930",numb=1):
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

    return int(res.json()['output'][numb]['stck_clpr'])

def get_yesterday_price(code="005930"):
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

    #  005930 :삼성전자   035720:카카오 #035420 네이버 제외
    symbol_list = ["005930","035720","000660","069500"] 
    ##symbol_list = ["005930"] # 매수 희망 종목 리스트
    bought_list = [] # 매수 완료된 종목 리스트
    send_list = []
    total_cash = get_balance() # 보유 현금 조회
    stock_dict = get_stock_balance() # 보유 주식 조회
    
    
    short_list=[]
    ## 강제 판매 종목



    buy_hope_list=[]
    buy_list=[]
    not_cell=[]
    cell_hope_list=[]

    for x in symbol_list:
        #21 최고가 22 최저가 
        a=[x, 999,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,  0,999,0]
        buy_list.append(a)

    buy_sw=True
    sell_sw=True
    by_pass=False

    canusecash=int(get_stock_balance1())
    print('total cash: ',canusecash,end=', ')
    print('현재 구매 가능 금액 :',total_cash)

    target_buy_count = 100 # 매수할 종목 수
    buy_percent = 0.95 # 종목당 매수 금액 비율
    buy_amount = canusecash * buy_percent  # 종목별 주문 금액 계산
    soldout = False

    counter=0
    counterSet=1
    fristcount=1
    beforstate=0
    currentstate=0

    buy_short=0

    if total_cash>100000:
        target_buy_count = 100
        print("구매 Start")
    else:
        target_buy_count = 0
        print("판매 Start")
    
    #구매 판매 test
    target_buy_count=100
    

    # 한종목 구매 또는 단타 진행 할지 check
    buylist_check_end=0

    print('')
    print('')
######################################################################################################################################################################
# 반복 시작
    send_message("===국내 주식 자동매매 프로그램을 시작합니다===")
    while True:
        print()
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
        t_sell = t_now.replace(hour=23, minute=10, second=0, microsecond=0)
        t_exit = t_now.replace(hour=23, minute=30, second=0,microsecond=0)


        t_10minbef = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_earlyexit = t_now.replace(hour=13, minute=00, second=0, microsecond=0)
        '''
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            send_message("주말이므로 프로그램을 종료합니다.")
            break
        '''
######################################################################################################################################################################
# 구매 종목 선택 
# 구매 가능 금액 이하이면 pass
        if ( (t_10minbef < t_now) and (buylist_check_end==0) and( target_buy_count>10) ) : 
            print('오늘 구매 가능한 종목')
            for sym in symbol_list:
                #강제 판매 종목 pass
                if sym in short_list:
                    continue
                current_price = get_current_price(sym)
                yes_price=get_beforeday_price(sym,1)  
                agv5=get_avr_price(sym,5)
                agv10=get_avr_price(sym,10)
                bef20_price=get_beforeday_price(sym,20)
                print('"',sym,'"',': ',round(((current_price-yes_price)/yes_price*100),4),'%')
                #print('"',sym,'"',agv5,agv10,bef20_price)
                
                # 구매 가능 조건 
                if (current_price>=agv5)and(current_price>=agv10)and(bef20_price>=yes_price)and(current_price>=yes_price):
                    buy_hope_list.append(sym)
            print()
            print('구매 희망 종목:',buy_hope_list)
            a=''
            b=0
            time.sleep(1)
            for sym in buy_hope_list:
                #희망 구매 종목에서 가장 높은 증가율 한 종목 선택(a) 
                current_price = get_current_price(sym)
                yes_price=get_beforeday_price(sym,1)  
                #어제 대비 증가율
                print(sym,': ',round((current_price-yes_price)/yes_price*100,4))
                time.sleep(1)
                # 이전 증가율보다 큰 증가율이 있으면  
                if round((current_price-yes_price)/yes_price*100,4)>=b:
                    # 증가율 b에 입력 
                    b=round((current_price-yes_price)/yes_price*100,4)
                    a=sym
            buy_hope_list=[]

            if a=='':
                pass
            else:
                # 가장 높은 증가율 a를 구매 희망 종목에 입력 
                buy_hope_list.append(a)
            
            
            #print(buy_hope_list)
            if (len(buy_hope_list))==0:
                buy_short=1
                print('금일 구매 희망 종목 없어 단타 진행')
                for sym in symbol_list:
                    current_price = get_current_price(sym)
                    yes_price=get_beforeday_price(sym,1)  
                    
                    #어제보다 증가 항목만 희망 구매 항목에 추가 
                    if current_price>yes_price:
                        buy_hope_list.append(sym)
                print('어제보다 상승 종목',buy_hope_list)
                
                #어제보다 증가 종목도 없으면 
                if (len(buy_hope_list))==0:
                    print()
                    print('!!!아무 종목 없음 => 모든 종목에 대해서 진행')
                    buy_hope_list=symbol_list
            else:
                print('구매 희망 중 가장 큰 상승 종목:',buy_hope_list,' , ',b,'%')
            print('최종 구매 종목: ',buy_hope_list)
            
            buylist_check_end=1

##-----------------------------------------------------------------------------------------------------------------------------------------------------
        # 이게 왜 여기 있음??
        stt=time.time()


        print()
        print("구매 정보")

        if (t_start < t_now < t_sell):  # AM 09:05 ~ PM 03:15 : 매수
            for sym in buy_hope_list:
                if len(bought_list) < target_buy_count:
                    
                    current_price = get_current_price(sym)
                    yes_price=get_beforeday_price(sym,1)  

                    slewrate20=0
                    slewrate10=0
                    slewrate5=0
                    case0=0
                    case1=0
                    case2=0
                    case3=0
                    min20=999
                    max20=0
                    canbuy=0
                    avg5=0
                    avg10=0


                    # 뭐하는거임?? buy_hope_list 그냥 여기에 있는 항목 들고 오면 안되나?
                    #=> List형태 필요 :안된다
                    for s in buy_list:
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
                            for  i in range(2,20):
                                if s[i]>max20:
                                    max20=s[i]
                                if s[i]<min20:
                                    if(s[i]==0):
                                        pass
                                    else:
                                        min20=s[i]
                            avg5=(s[3]+s[4]+s[5]+s[6]+s[7])/5
                            avg10=(s[3]+s[4]+s[5]+s[6]+s[7]+s[8]+s[9]+s[10]+s[11]+s[12])/10

                            #값 부족으로 기울기 20 대체값
                            slewrate20=s[2]-s[20]
                            if (counter<counterSet*22):
                                slewrate20=s[2]-s[13]

                            case0=( (counter>counterSet*5) and (current_price>=s[2]) and(current_price>=avg5) and (current_price>=avg10) )
                            # 반드시 만족해야 함
                            # 최초값 안정화 이후 and  정기 입력 값 보다 크고 5분 평균 이상 and 10분 평균 이상
                            
                            case1=( (max20-current_price) > current_price*0.01)
                            # 20분 동안 1% 감소 한 경우

                            case2=( (buy_short==0) and (slewrate20<0)and (t_earlyexit < t_now) )
                            # 단타가 아니고 1시 반 이후 20일 평균 기울기 감소 
                            
                            case3=(current_price<=s[21]*0.985)
                            # 당일 최고가 대비 1.5% 감소

                            canbuy=(case0 and (case1 or case3 or case3))

                            print(s[0],': ',end=',')
                            for i in range(2,21):
                                print(s[i],end=', ')
                            print()
                            print('case  만족 여부=> 반드시 만족 : ',case0,' 하나 만족 :',case1,case2,case3,'최종 구매 여부: ',canbuy)
                            if canbuy==1:
                                if case1:
                                    print("20분 안에 급 하락 ")
                                if case2:
                                    print("단타 아닌 상태에서 1시반 이후 희망 구매 조건 만족 ")
                                if case3:
                                    print("당일 최고가 대비 1.5% 감소 ")
                                ''''
                                ## 20 평균 기울기 음수  and  10일 평균 기울기 양수  and  5일 평균 기울기 양수 
                                case1=( (slewrate20<0)and(slewrate10>0)and(slewrate5>0) )
                                # 최초값 안정화 이후 and  정기 입력 값 보다 크고 정기값은 상승 중 일 때
                                case3=( (counter>counterSet*12) and (current_price>=s[2]) and (s[2]>=s[3]))

                                canbuy=(case1 and case3)
                                print('   1min diff:',round(s[2]-s[3],3),"5min diff slew: ",slewrate5,end=' s=>')
                                print(s[1],"변화=>",s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9])
                                if canbuy==1:
                                    if case1:
                                        print("하락 후 상승 중 이므로 구매 희망 ")
                                '''
                    if (canbuy):
                        buy_qty = 0  # 매수할 수량 초기화
                        lisk=1;
                        #추가 구매 갯수

                        #구매 갯수
                        buy_qty = int(buy_amount*lisk // current_price)
                        
                        if buy_qty > 0:
                            print(sym,'종목',buy_qty,'매수를 시작 합니다!')
                            result = buy(sym, buy_qty)
                            if result:
                                print(sym,'종목',buy_qty,'매수를 성공!!!!!!축하합니다!')
                                target_buy_count=0
                                for s in buy_list:
                                    if s[0]==sym:
                                        s[1]=current_price
                                counter=0
                                soldout = False
                                get_stock_balance()
                    time.sleep(1)
            time.sleep(1)
##-----------------------------------------------------------------------------------------------------------------------------------------------------
        print('-----------------------------------------')
        print("판매 정보")
        if (t_start < t_now < t_sell):  # PM 03:15 ~ PM 03:20 : 일괄 매도
            ##if soldout == False:
            ##한번 출력 cell_hope_list
            stock_dict = get_stock_balance()

            for sym, qty in stock_dict.items():
                if target_buy_count>10:
                    continue
                
                if sym in not_cell:
                    continue
                        

                current_price = get_current_price(sym)
                yes_price=get_beforeday_price(sym,1)  
                agv5=get_avr_price(sym,5)
                agv10=get_avr_price(sym,10)
                bef20_price=get_beforeday_price(sym,15)
                print('"',sym,'"',': ',round(((current_price-yes_price)/yes_price*100),4),'%')

                canbysell=(  ((current_price<=agv5)and(current_price<=agv10)and(current_price-bef20_price<=0.2)and (current_price<=yes_price)) or (buy_short==1) or (current_price<yes_price*0.97)  )
                for x in cell_hope_list:
                    if x==sym:
                        canbysell=1
                if canbysell:
                    print('금일 판매 희망')
##-------------------------------------------------------------
                slewrate20=0
                slewrate10=0
                slewrate5=0
                case0=0
                case1=0
                case2=0
                case3=0
                case4=0

                min20=999
                max20=0
                avg5=0
                avg10=0
                cansell=0

                for s in buy_list:
                    if s[0]==sym:
                        #구매정보에 구매 값 없으면 현재 값 대입
                        if s[1]==999:
                            s[1]=current_price
                        if(round(counter%counterSet,3)==0):
                            for i in range(3,21):
                                s[23-i]=s[22-i]
                            s[2]=current_price
                            #최저가
                            if s[22]> current_price:
                                s[22]=current_price
                            #최고가
                            if s[21]< current_price:
                                s[21]=current_price

                        slewrate20=s[20]-s[2]
                        slewrate10=s[11]-s[2]
                        slewrate5=s[7]-s[2]

                        if (counter<counterSet*22):
                            slewrate20=s[13]-s[2]

                        case0=( (s[2]<=s[3]) )and (counter>counterSet*12) 
                        case1=( (slewrate20<0.2) and(slewrate10<0)and (slewrate5<0))
                        case2=( (current_price>=s[1]*1.01) )
                        case3=( current_price<s[1]*0.992)
                        #case4=( current_price<=max5*0.995)
                        case4=(canbysell and (t_earlyexit < t_now) ) 

                        cansell=( canbysell and  case0 and case1 and ( case2 or case3 or case4)  )

                        print(s[0],': ',end=',')
                        for i in range(2,21):
                            print(s[i],end=', ')
                        print()
                        print(s[0],'현재 가격',current_price,' 예상 판매 가격:', bef20_price+0.2, end ='|||||||||')
                        print('판매 조건 만족:',( case2 or case3 or case4),end=' =>')
                        print('5min diff: ',current_price-s[6],end=',')
                        print('10min diff: ',current_price-s[11],end=',')
                        print('20min diff: ',current_price-s[20])
                        print('____________________________________________________________')
                        #print('case  만족 여부=> 반드시 만족 : ',canbysell, case0, case1,' 하나 만족 :',case2,case3,case4,'최종 구매 여부: ',cansell)

                        '''
                        # 하락 중이고 값이 정상적으로 들어 있을 때
                        case0=( ( ( (s[2]<=s[3])and(s[3]<=s[4])) )and (counter>counterSet*12) )
                        #20 평균 기울기가 0에 가까워지면 판매
                        case1=( (slewrate20<=100) and(slewrate10<0)and (slewrate5<0))
                        #목표 지점 도달
                        case2=( (current_price>=s[1]*1.008) )
                        # 하락 시 판매
                        case3=(current_price<s[1]*0.905)
                        '''

                        print('____________________________________________________________')

                
                if(cansell):
                        result=sell(sym, qty)
                        print(sym,'종목 ',qty,'개 시작')
                        time.sleep(1)
                        if result:
                            print(sym,'종목 ',qty,'개 시작')
                            target_buy_count=100
                            counter=0
                            buylist_check_end=0
                            canbysell=0
                            buy_short=0


                            soldout = False
                            bought_list.append(sym)
                            send_list.append(sym)
                            get_stock_balance()
                        time.sleep(1)

        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            send_message("프로그램을 종료합니다.")
            break
        if (t_earlyexit < t_now) and (target_buy_count<10) and (canbysell==0) and (buy_short==0):
            print('조기 퇴근 합니다!')
            send_message("프로그램을 종료합니다.")
            break

        endt=time.time()
        print()
        # one cycle 시간
        sttoendtime=round(endt-stt,3)
        #  divide 0 방지 코드
        if sttoendtime==0:
            sttoendtime=1

        
        print(sttoendtime,"걸림")
        if (t_start < t_now < t_sell):
            counter=counter+1
        else:
            time.sleep(60)

        if (counter==3):
            counterSet=int((60/sttoendtime)-0.3)
            # dead code ?
            fristcount=counterSet

        #  divide 0 방지 코드
        if counterSet<1:
            counterSet=1

        print('counter: ',counter)
        print("one run time",sttoendtime,'counterSet: ',(counterSet))
        print("##############################################################################################")
        print("")
        
except Exception as e:
    send_message(f"[오류 발생]{e}")
    time.sleep(1)