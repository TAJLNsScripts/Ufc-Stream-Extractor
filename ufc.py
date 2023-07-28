import requests
import time
import json
import base64
import m3u8
import os

def ascii_clear():
    os.system('cls||clear')
    print("""
         ^555555555557     J555555555?    :GBGGGGGGGGGGGGGGGGGGGGB7    ^?PGGGGGGGGGGGGGGGGGPY7:     
         5@@@@@@@@@@@~    !@@@@@@@@@@7    5@@@@@@@@@@@@@@@@@@@@@@#:   J&@@@@@@@@@@@@@@@@@@@@@@&?    
        !@@@@@@@@@@@J    .B@@@@@@@@@P    7@@@@@@@@@@@@@@@@@@@@@@@7   !@@@@@@@@@@@#############&5    
       .G@@@@@@@@@@B.    Y@@@@@@@@@&^   .YGGGGGGGGGGGGGGGGGGGGGGY   .G@@@@@@@@@#~..............     
       ?@@@@@@@@@@@~    ~@@@@@@@@@@Y                                ?@@@@@@@@@@7                    
      :#@@@@@@@@@@Y    .G@@@@@@@@@#:   :!~~~~~~~~~~~~~~~~~~~~~!.   :#@@@@@@@@@G                     
      Y@@@@@@@@@@#:    J@@@@@@@@@@?    G@@@@@@@@@@@@@@@@@@@@@@B.   J@@@@@@@@@&~                     
     ^&@@@@@@@@@@!    ^&@@@@@@@@@B.   ?@@@@@@@@@@@@@@@@@@@@@@&~   ^&@@@@@@@@@Y                      
     P@@@@@@@@@@P     P@@@@@@@@@@!   :#@@@@@@@@@@@@@@@@@@@@@@J    5@@@@@@@@@#:                      
    !@@@@@@@@@@#:    ?@@@@@@@@@@P    5@@@@@@@@@@P^^^^^^^^^^^^    ~@@@@@@@@@@?                       
   .B@@@@@@@@@@5    !&@@@@@@@@@&^   ~@@@@@@@@@@&^                G@@@@@@@@@G                        
   ?@@@@@@@@@@@&PY5B@@@@@@@@@@@Y   .B@@@@@@@@@@J                7@@@@@@@@@@#5YYYYYYYYYYY55^         
  :#@@@@@@@@@@@@@@@@@@@@@@@@@@#:   ?@@@@@@@@@@#.               .B@@@@@@@@@@@@@@@@@@@@@@@@B.         
  :#@@@@@@@@@@@@@@@@@@@@@@@@@B~   ^&@@@@@@@@@@7                :&@@@@@@@@@@@@@@@@@@@@@@@#~          
   ^YGB##################BG57.    Y##########P                  ~5B###################P?:           
      ....................        ...........                      ...................              

                                  Stream extractor
                                    TAJLN 2023
""")

def current_milli_time():
    return round(time.time() * 1000)

def refresh_token(token):
    url = 'https://dce-frontoffice.imggaming.com/api/v2/token/refresh'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'x-api-key': '4dc1e8df-5869-41ea-95c2-6f04c67459ed',
        'app': 'dice',
        'accept-language': 'en-US',
        'realm': 'dce.ufc',
        'authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Content-Length': '525',
        'Host': 'dce-frontoffice.imggaming.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    
    post_data = {
        "refreshToken": "eyJhbGciOiJSUzI1NiIsInB1ciI6IlJFRiIsInNpZyI6ImciLCJ0eXAiOiJKV1QiLCJ2IjozfQ.eyJhcCI6eyJhcHQiOiJJRCJ9LCJhcHIiOiJJRCIsImF1ZCI6ImRjZS51ZmMiLCJkZXYiOiJBTkRST0lEX1BIT05FIiwiZW52IjoicHJvZCIsImV4cCI6MTY5NjkwODg2NCwiZ3VlIjpmYWxzZSwiaWF0IjoxNjg4MjY4ODY0LCJpc3MiOiJkY2UtaWQiLCJzdWIiOiJWY29QdW58NjAzYjVhNDAtNDU0MC00ZjdjLTgzNGMtOTU5ZGI4Y2Y2M2MyIn0.WXIE3Wy_EnUwux146leJtNYN5mrK9yDQw7WEWQGwb9ASGv7WWkLgKNNbqJ9sSCaNB6S_YYUkusf9AdA-dnUlDgfKYVMtBW-t5dTHsRHuSDxkuE_5-jsRu0MqdP5_S031-j9sfXSDL644_lz35PdGlXqGgK5kIicrj5cU5SEyNRs"
    }
    
    post_data = json.dumps(post_data)
    
    response = requests.post(url, headers=headers, data=post_data)
    if response.status_code == 201:
        print('Token refresh successful')
        data = json.loads(response.content)
        return data['authorisationToken']
    else:
        print('Token refresh failed')
        print(response.content)
        quit()
    
def choose_event(token):
    url = 'https://dce-frontoffice.imggaming.com/api/v2/event/live'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'x-api-key': '4dc1e8df-5869-41ea-95c2-6f04c67459ed',
        'app': 'dice',
        'accept-language': 'en-US',
        'realm': 'dce.ufc',
        'authorization': 'Bearer ' + token,
        'Host': 'dce-frontoffice.imggaming.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print('Event list request successful')
        
        data = json.loads(response.content)
        
        events = data['events']
        
        ascii_clear()
        
        print('Found ' + str(len(events)) + ' currently active events:')
        
        i = 1
        for e in events:
            print(str(i) + '. ' + e['title'])
            i+=1
        
        choose = int(input("\nChoose event (To search again type 0): "))
        
        if choose == 0 or choose > len(events):
            return choose_event(token)
        else:
            ascii_clear()
            
            event_id = str(events[choose-1]['id'])
            event_name = events[choose-1]['title']
            
            if 'androidIAPCodes' in json.dumps(events[choose-1]):
                androidIAPCodes = events[choose-1]['availablePurchases'][0]['androidIAPCodes'][0]
            else:
                androidIAPCodes = None
            
            return [event_id, event_name, androidIAPCodes]
        
    else:
        print('Event list request failed')
        print(response.content)
        quit()
    
    
    
def spoof_buy(token, androidIAPCodes):
    
    url = 'https://dce-frontoffice.imggaming.com/api/v2/googlePlay/receipt'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'x-api-key': '4dc1e8df-5869-41ea-95c2-6f04c67459ed',
        'app': 'dice',
        'accept-language': 'en-US',
        'realm': 'dce.ufc',
        'authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Content-Length': '1802',
        'Host': 'dce-frontoffice.imggaming.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0'
    }
    
    reciept_string = '{"orderId":"6660823415274633304.5480098017970283","packageName":"com.neulion.smartphone.ufc.android","productId":"' + androidIAPCodes + '","purchaseTime":' + str(current_milli_time()) + ',"purchaseState":0,"purchaseToken":"bfokzzrsaqtxcmwklgnxwztz.AO-J1OsFfDYXhRrvKGFBqjOUCiamHLDdHEetbxCVAoBNpOD-mTIQtoB_lLPEinJmPUMurynpiPutfRNNgHlcekcnGpWZiFsSGRYTHOveFjrKRgeLKDYcevlhZbWnRXOLhOGMjKztehMT","developerPayload":"subs:' + androidIAPCodes + ':{\\"purchaseStrategy\\":{\\"type\\":\\"SUBSCRIPTION\\",\\"subscriptionPeriod\\":\\"P1M\\",\\"subscriptionMarketingPricePeriod\\":\\"P1M\\"},\\"id\\":168}","receiptData":"{\\"orderId\\":\\"5560823415974633704.5480098017970283\\",\\"packageName\\":\\"com.neulion.smartphone.ufc.android\\",\\"productId\\":\\"' + androidIAPCodes + '\\",\\"purchaseTime\\":1688075795889,\\"purchaseState\\":0,\\"purchaseToken\\":\\"bfokzzrsaqtxcmwklgnxwztz.AO-J1OsFfDYXhRrvKGFBqjOUCiamHLDdHEetbxCVAoBNpOD-mTIQtoB_lLPEinJmPUMurynpiPutfRNNgHlcekcnGpWZiFsSGRYTHOveFjrKRgeLKDYcevlhZbWnRXOLhOGMjKztehMT\\",\\"developerPayload\\":\\"subs:' + androidIAPCodes + ':{\\\\\\"purchaseStrategy\\\\\\":{\\\\\\"type\\\\\\":\\\\\\"SUBSCRIPTION\\\\\\",\\\\\\"subscriptionPeriod\\\\\\":\\\\\\"P1M\\\\\\",\\\\\\"subscriptionMarketingPricePeriod\\\\\\":\\\\\\"P1M\\\\\\"},\\\\\\"id\\\\\\":168}\\"}"}'
    reciept_encoded = base64.b64encode(reciept_string.encode()).decode()
    
    post_data = {
        "base64EncodedReceipt": reciept_encoded
    }
    
    post_data = json.dumps(post_data)
    
    response = requests.post(url, headers=headers, data=post_data)
    if response.status_code == 202:
        print('Modified purchase accepted')
    else:
        print('Modified purchase rejected')
        print(response.content)
        quit()
    
def request_event(token, event_id):
    url = 'https://dce-frontoffice.imggaming.com/api/v2/stream/event/' + event_id

    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'x-api-key': '4dc1e8df-5869-41ea-95c2-6f04c67459ed',
        'app': 'dice',
        'accept-language': 'en-US',
        'realm': 'dce.ufc',
        'authorization': 'Bearer ' + token,
        'Host': 'dce-frontoffice.imggaming.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print('Event request successful')
        data = response.json()
        return data['playerUrlCallback']
    else:
        print('Event request failed')
        print(response.content)
        quit()
        
def request_stream(url):
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'x-api-key': '4dc1e8df-5869-41ea-95c2-6f04c67459ed',
        'app': 'dice',
        'accept-language': 'en-US',
        'realm': 'dce.ufc',
        'Host': 'dge-streaming.imggaming.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.11.0',
    }
    
    response = requests.get(url, headers)
    if response.status_code == 200:
        print('Stream request successful')
        data = response.json()
        return data['hlsUrl']
    else:
        print('Stream request failed')
        print(response.content)
        quit()
        
def stream_exteract(url, user_agent):
    try:
        print('Processing temp m3u8')

        base_url = url.split('/hls/live/', 1)[0] + '/hls/live'
        
        perm_streams = []
        
        headers = {
            'User-Agent': user_agent,
        }
        
        m3u8_obj = m3u8.loads(requests.get(url, headers=headers).content.decode())
        
        ascii_clear()
        
        print('Extracted urls:')
        
        i = 1
        for playlist in m3u8_obj.playlists:
            m3u8_url = playlist.uri.replace('../..', base_url)
            bandwidth = str(playlist.stream_info.bandwidth)
            perm_streams.append({'m3u8_url': m3u8_url, 'bandwidth': bandwidth})
            
            print(str(i) + '. '+ bandwidth + ': ' + m3u8_url)
            
            i+=1
        
        choose = int(input('Choose url for export (0 for none): ' ))
        
        if choose == 0 or choose > len(perm_streams):
            quit()
        else:
            return perm_streams[choose-1]['m3u8_url']

    
    except Exception as e:
        print('Stream extraction failed')
        print(e)
    
    
ascii_clear()    
    
token = 'eyJhbGciOiJSUzI1NiIsInB1ciI6IkFVVCIsInNpZyI6ImciLCJ0eXAiOiJKV1QiLCJ2IjozfQ.eyJhcCI6eyJhcHQiOiJJRCJ9LCJhcHIiOiJJRCIsImF1ZCI6WyJkY2UudWZjIl0sImRldiI6IkFORFJPSURfUEhPTkUiLCJlbnYiOiJwcm9kIiwiZXhwIjoxNjg4MjY5NDY0LCJndWUiOmZhbHNlLCJpYXQiOjE2ODgyNjg4NjQsImlwIjoiMTQ5LjcuMTYuMTQ1IiwiaXNzIjoiZGNlLWlkIiwibG8yIjoiR0IsRW5nbGFuZCxFbmdsYW5kLExvbmRvbixFQzRSLDAsMSwwIiwicm9sIjoiQ1VTVE9NRVIiLCJzdWIiOiJWY29QdW58NjAzYjVhNDAtNDU0MC00ZjdjLTgzNGMtOTU5ZGI4Y2Y2M2MyIiwidXRwIjoiSFVNQU4ifQ.TdtxoCGagJbR6s_-PYsHteZVeizk0Ydbol9CZ5POA_stIGeuIrZGU9a99zMWgrpoVZ5L8a-xVbuVg-1G6wu6B4ub5kZToAzDHVG77CpuK8nI5jWGXwG0OqYvoFU398VDUEUpAzGBv_wnetPQEyNnxcaDJF_7sYhmPYrJGgWklNk'

token = refresh_token(token)

event = choose_event(token)
event_id = event[0]
event_name = event[1]
androidIAPCodes = event[2]

if androidIAPCodes is not None:
    spoof_buy(token, androidIAPCodes)

stream_request_url = request_event(token, event_id)

temp_m3u8 = request_stream(stream_request_url)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
m3u8_url = stream_exteract(temp_m3u8, user_agent)

f = open("playlist.m3u", "w+")
f.write('#EXTINF:-1 tvg-logo="https://www.sportsvideo.org/wp-content/uploads/2021/02/ufc-fight-pass-logo.png" group-title="PPV",' + event_name)
f.write('\n#EXTVLCOPT:http-user-agent=' + user_agent)
f.write('\n' + m3u8_url)

ascii_clear()

f.flush()
f.seek(0)
print('Exported ' + event_name + ' to playlist.m3u')
print('Preview: \n')
print(f.read())
f.close()