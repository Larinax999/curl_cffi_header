import typing,curl_cffi

def parse_set_cookie(header: str) -> dict:
    parts = header.split(';')

    # First part is always name=value, but value may contain '='
    name_value = parts[0].strip()
    if '=' not in name_value: raise ValueError("Invalid Set-Cookie header (no = in name-value pair)")

    name, value = name_value.split('=', 1)  # only split on the first '='
    cookie = {'name': name, 'value': value}

    return cookie

class curl_cffi_header:
    def __init__(self,client:curl_cffi.Session,cookies:dict[str,str]={},order_cookie:typing.List[str]=[]):
        # client.verify=False
        self.client=client
        self.cookies=curl_cffi.Cookies()
        for key, value in cookies.items():self.cookies.set(key, value)
        self.order_cookie=order_cookie
    def request(self,method:str,url:str,**kwargs)->curl_cffi.Response: # what the fuck idk what im writing but anyway it working :>

        if kwargs.get("headers"): # fix

            content_length_key = next((k for k in kwargs["headers"].keys() if k.lower() == "content-length"), None)
            if content_length_key is not None:
                data = kwargs.get("data","")
                if not isinstance(data, bytes):data=data.encode()
                kwargs["headers"][content_length_key] = str(len(data))

            cookie_key = next((k for k in kwargs["headers"].keys() if k.lower() == "cookie"), None)

            # HTTP/2: split cookies into separate headers
            if kwargs["headers"].get("Host") == None and not hasattr(self.client,"force_http1"): 
                headers_list = []
                for k, v in kwargs["headers"].items():
                    if k == cookie_key:
                        c=self.cookies.get_dict()
                        for i in self.order_cookie:
                            if c.get(i):headers_list.append((cookie_key, f"{i}={c[i]}"))

                        for i,iv in c.items():
                            if i not in self.order_cookie: headers_list.append((cookie_key, f"{i}={iv}"))

                        if v != "":
                            for part in v.split("; "):
                                if part: headers_list.append((cookie_key, part))
                    else:
                        headers_list.append((k, v))

                kwargs["headers"] = headers_list

            else: # HTTP/1.1: keep single cookie header
                if cookie_key is not None:
                    cookie=""
                    c=self.cookies.get_dict()
                    for i in self.order_cookie:
                        if c.get(i):cookie+=f"{i}={c[i]}; "

                    for i,v in c.items():
                        if i not in self.order_cookie: cookie+=f"{i}={v}; "

                    kwargs["headers"][cookie_key] = cookie + kwargs["headers"][cookie_key] if kwargs["headers"][cookie_key] != "" else cookie[:-2]

        resp=self.client.request(method=method,url=url,**kwargs) # type: ignore

        for c in resp.headers.get_list("set-cookie"): # type: ignore
            if c==None:continue
            a=parse_set_cookie(c) 
            self.cookies.set(a["name"],a["value"])

        return resp # type: ignore :P