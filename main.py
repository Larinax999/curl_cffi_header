from curl import curl_cffi,curl_cffi_header
import json

def find_header(resp:curl_cffi.Response):
    for h in resp.json()["http2"]["sent_frames"]:
        if h["frame_type"]=="HEADERS":
            return h["headers"]

def main():
    client=curl_cffi_header(curl_cffi.Session(
        impersonate="chrome146",
        default_headers=False,
        discard_cookies=True
    ),{
        "a":"1",
        "b":"2",
        "c":"3"
    },["a","c","b"])

    client2=curl_cffi.Session(
        impersonate="chrome146",
        default_headers=False, # reduce shuffle
        # discard_cookies=True
    )
    client2.cookies.set("a","1")
    client2.cookies.set("b","2")
    client2.cookies.set("c","3")
    
    # GET test
    headers={
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,th;q=0.8,fr;q=0.7,km;q=0.6",
        "cookie":"",
        "priority": "u=0, i"
    }
    resp=client.request("GET","https://tls.peet.ws/api/all",headers=headers)
    header1=find_header(resp) # type: ignore

    # GET test
    del headers["cookie"]
    resp=client2.get("https://tls.peet.ws/api/all",headers=headers,impersonate="chrome146")
    header2=find_header(resp)
    
    print("GET with curl_cffi_header >",json.dumps(header1, indent=4))
    print("GET without curl_cffi_header >",json.dumps(header2, indent=4))

    # POST test
    headers={
        "content-length":"0",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua-platform": "\"Windows\"",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "accept": "*/*",
        "origin": "https://tls.peet.ws",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://tls.peet.ws/api/all",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,th;q=0.8,fr;q=0.7,km;q=0.6",
        "cookie": "",
        "priority": "u=1, i"
    } # header from fetch("https://tls.peet.ws/api/all",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({"a":1,"b":2,"c":3})})
    body={"a":1,"b":2,"c":3}
    resp=client.request("POST","https://tls.peet.ws/api/all",data=json.dumps(body,separators=(",",":")),headers=headers)
    header1=find_header(resp)

    # POST test
    del headers["content-length"]
    del headers["cookie"]
    resp=client2.post("https://tls.peet.ws/api/all",headers=headers,json=body,impersonate="chrome146")
    header2=find_header(resp)
    
    print("POST with curl_cffi_header >",json.dumps(header1, indent=4))
    print("POST without curl_cffi_header >",json.dumps(header2, indent=4))


if __name__ == "__main__":
    main()
