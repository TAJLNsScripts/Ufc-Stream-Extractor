import requests
import time
import json
import base64
import m3u8
import os
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from bs4 import BeautifulSoup

#Config
PATH_TO_WVD = './WVD.wvd'

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

def do_cdm(pssh, license_url, licence_token, key_id):
    pssh = PSSH(pssh)

    device = Device.load(PATH_TO_WVD)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    challenge = cdm.get_license_challenge(session_id, pssh)

    drm_info_json = {
        "system":"com.widevine.alpha",
        "key_ids":[key_id]
    }

    headers = {
            'Authorization': 'Bearer ' + licence_token,
            'X-DRM-INFO': base64.b64encode(json.dumps(drm_info_json).encode()).decode(),
            'Content-Type': 'application/octet-stream',
            'User-Agent': 'Dice Shield/12.11.0 (Linux;Android 9) ExoPlayerLib/2.18.4',
    }

    licence = requests.post(license_url, headers=headers, data=challenge)
    licence.raise_for_status()

    cdm.parse_license(session_id, licence.content)

    keys = cdm.get_keys(session_id)
    
    cdm.close(session_id)

    for key in keys:
        if key.type != 'SIGNING':
            return f"{key.kid.hex}:{key.key.hex()}"

def find_wv_pssh_offset(raw: bytes) -> str:
    offset = raw.rfind(b'pssh')
    return raw[offset - 4:offset - 4 + raw[offset - 1]]


def to_pssh(content: bytes) -> str:
    wv_offset = find_wv_pssh_offset(content)
    return base64.b64encode(wv_offset).decode()

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
        "refreshToken": "eyJhbGciOiJSUzI1NiIsInB1ciI6IlJFRiIsInNpZyI6ImciLCJ0eXAiOiJKV1QiLCJ2IjozfQ.eyJhcCI6eyJhcHQiOiJJRCJ9LCJhcHIiOiJJRCIsImF1ZCI6ImRjZS51ZmMiLCJkZXYiOiJBTkRST0lEX1BIT05FIiwiZW52IjoicHJvZCIsImV4cCI6MTY5OTMyNDQ1OCwiZ3VlIjpmYWxzZSwiaWF0IjoxNjkwNjg0NDU4LCJpc3MiOiJkY2UtaWQiLCJzdWIiOiJhWHZLclp8MjQ2YWRiNGEtOGI4YS00NWYwLWI2NGYtYjg1ODgxODUzYjNmIn0.DHydVhuWBNdIvfubRG9XujU8IDycfGo3GRdsVpyNArR-2t-WzKKrbD4K-EtYWB6kSAMGtEnfZ8-uYUSxTmBIM0vK3MV8_le5zd5jLCzMoWM89CkwaGWHLkjSMnlrxYagzPeWhLtYZplg7rxygYCh6uX7VG76WVAohmUqaLOZPro"
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
    
    order_id = '9990823415274633304.5480098017970283'
    purchase_token = 'bfokzzrsaqtxcmwklgnxwztz.AO-J1OsFfDYXhRrvKGFBqjOUCiamHLDdHEetbxCVAoBNpOD-mTIQtoB_lLPEinJmPUMurynpiPutfRNNgHlcekcnGpWZiFsSGRYTHOveFjrKRgeLKDYcevlhZbWnRXOLhOGMjKztehMT'
    purchase_time = str(current_milli_time())
    
    reciept_string = '{"orderId":"' + order_id + '","packageName":"com.neulion.smartphone.ufc.android","productId":"' + androidIAPCodes + '","purchaseTime":' + purchase_time + ',"purchaseState":0,"purchaseToken":"' + purchase_token + '","developerPayload":"subs:' + androidIAPCodes + ':{\\"purchaseStrategy\\":{\\"type\\":\\"SUBSCRIPTION\\",\\"subscriptionPeriod\\":\\"P1M\\",\\"subscriptionMarketingPricePeriod\\":\\"P1M\\"},\\"id\\":168}","receiptData":"{\\"orderId\\":\\"6660823415974633704.5480098017970283\\",\\"packageName\\":\\"com.neulion.smartphone.ufc.android\\",\\"productId\\":\\"' + androidIAPCodes + '\\",\\"purchaseTime\\":' + purchase_time + ',\\"purchaseState\\":0,\\"purchaseToken\\":\\"' + purchase_token + '\\",\\"developerPayload\\":\\"subs:' + androidIAPCodes + ':{\\\\\\"purchaseStrategy\\\\\\":{\\\\\\"type\\\\\\":\\\\\\"SUBSCRIPTION\\\\\\",\\\\\\"subscriptionPeriod\\\\\\":\\\\\\"P1M\\\\\\",\\\\\\"subscriptionMarketingPricePeriod\\\\\\":\\\\\\"P1M\\\\\\"},\\\\\\"id\\\\\\":168}\\"}"}'
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
        return [data['hls']['url'], data['dash']['url'], data['dash']['drm']['url'], data['dash']['drm']['jwtToken']]
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
          
def get_pssh_perm_key_id(dash_url, user_agent):
    headers = {
       'User-Agent': user_agent
    }
    
    response = requests.get(dash_url, headers=headers, allow_redirects=False)
    location_url = response.headers['location']
    
    response = requests.get(location_url, headers=headers)
    
    soup = BeautifulSoup(response.content, features="xml")
    audio_repr = soup.findAll('Representation')[-1]
    audio_base_url = audio_repr.find('BaseURL').text
    audio_key_id = audio_repr.find('ContentProtection')['cenc:default_KID']
    
    location_parts = location_url.split('/')
    location_parts.pop()
    
    init_url = '/'.join(location_parts) + '/' + audio_base_url + 'init_' + audio_repr['id'] + '.m4s'
    
    init_response = requests.get(init_url, headers=headers)
    
    return [to_pssh(init_response.content), location_url, audio_key_id]
    
ascii_clear()
#token = 'eyJhbGciOiJSUzI1NiIsInB1ciI6IkFVVCIsInNpZyI6ImciLCJ0eXAiOiJKV1QiLCJ2IjozfQ.eyJhcCI6eyJhcHQiOiJJRCJ9LCJhcHIiOiJJRCIsImF1ZCI6WyJkY2UudWZjIl0sImRldiI6IkFORFJPSURfUEhPTkUiLCJlbnYiOiJwcm9kIiwiZXhwIjoxNjg4MjY5NDY0LCJndWUiOmZhbHNlLCJpYXQiOjE2ODgyNjg4NjQsImlwIjoiMTQ5LjcuMTYuMTQ1IiwiaXNzIjoiZGNlLWlkIiwibG8yIjoiR0IsRW5nbGFuZCxFbmdsYW5kLExvbmRvbixFQzRSLDAsMSwwIiwicm9sIjoiQ1VTVE9NRVIiLCJzdWIiOiJWY29QdW58NjAzYjVhNDAtNDU0MC00ZjdjLTgzNGMtOTU5ZGI4Y2Y2M2MyIiwidXRwIjoiSFVNQU4ifQ.TdtxoCGagJbR6s_-PYsHteZVeizk0Ydbol9CZ5POA_stIGeuIrZGU9a99zMWgrpoVZ5L8a-xVbuVg-1G6wu6B4ub5kZToAzDHVG77CpuK8nI5jWGXwG0OqYvoFU398VDUEUpAzGBv_wnetPQEyNnxcaDJF_7sYhmPYrJGgWklNk'
token = 'eyJhbGciOiJSUzI1NiIsInB1ciI6IkFVVCIsInNpZyI6ImciLCJ0eXAiOiJKV1QiLCJ2IjozfQ.eyJhcCI6eyJhcHQiOiJJRCJ9LCJhcHIiOiJJRCIsImF1ZCI6WyJkY2UudWZjIl0sImRldiI6IkFORFJPSURfUEhPTkUiLCJlbnYiOiJwcm9kIiwiZXhwIjoxNjkwNjg1MDU4LCJndWUiOmZhbHNlLCJpYXQiOjE2OTA2ODQ0NTgsImlwIjoiMTQ2LjcwLjExNi4xODIiLCJpc3MiOiJkY2UtaWQiLCJsbzIiOiJBVCxWaWVubmEsVmllbm5hLFZpZW5uYSwxMjMwLDAsMSwwIiwicm9sIjoiQ1VTVE9NRVIiLCJzdWIiOiJhWHZLclp8MjQ2YWRiNGEtOGI4YS00NWYwLWI2NGYtYjg1ODgxODUzYjNmIiwidXRwIjoiSFVNQU4ifQ.c3fg5QpwJ3s9YB7R8Fd-UE59_N306MgG0S8vHOKdgD8EzNCyuflDTI-B8JgeYOlyfHN07KivjbZ9DFJwD8B9HRwalSP39hfCRUO00uqPbBZapys_zq0MEtG0SLiqJULewZEICm2Kv6mHR-OjtUy_PBmb9gv_ZWDUjWpNf1fN-Zw'

#user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
user_agent = 'ExoDoris/12.11.0 (Linux;Android 9) ExoPlayerLib/2.18.4'

token = refresh_token(token)

event = choose_event(token)
event_id = event[0]
event_name = event[1]
androidIAPCodes = event[2]

if androidIAPCodes is not None:
    spoof_buy(token, androidIAPCodes)

stream_request_url = request_event(token, event_id)

hls_url, dash_url, licence_url, licence_token = request_stream(stream_request_url)

pssh, perm_dash, key_id = get_pssh_perm_key_id(dash_url, user_agent)

key = do_cdm(pssh, licence_url, licence_token, key_id)
print('Retrieved key: ' + key)

fkeys = key.split(":")
ekeys = base64.b64encode(('{"' + fkeys[0] + '":"' + fkeys[1] + '"}').encode('ascii'))
print("\nReproductor M3U8 link: " + perm_dash + "?&ck=" + ekeys.decode('ascii'))   

confirm = input('\nEnter Y to save to playlist.m3u: ')

if confirm.lower() != 'y':
    quit()

f = open("playlist.m3u", "w+")
f.write('#EXTINF:-1 tvg-logo="https://www.sportsvideo.org/wp-content/uploads/2021/02/ufc-fight-pass-logo.png" group-title="PPV",' + event_name)
f.write('\n#EXTVLCOPT:http-user-agent=' + user_agent)
f.write('\n#KODIPROP:inputstream.adaptive.license_type=clearkey')
f.write('\n#KODIPROP:inputstream.adaptive.license_key=' + key)
f.write('\n' + perm_dash)

ascii_clear()

f.flush()
f.seek(0)
print('Exported ' + event_name + ' to playlist.m3u')
print('Preview: \n')
print(f.read())
f.close()