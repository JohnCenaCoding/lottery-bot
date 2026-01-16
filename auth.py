import copy
import requests
from HttpClient import HttpClientSingleton

class AuthController:
    _REQ_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "https://www.dhlottery.co.kr",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "https://www.dhlottery.co.kr/",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,ko-KR;q=0.7",
    }

    _AUTH_CRED = ""

    def __init__(self):
        self.http_client = HttpClientSingleton.get_instance()

    def login(self, user_id: str, password: str):
        assert type(user_id) == str
        assert type(password) == str

        # 2026년 사이트 리뉴얼 대응: 로그인 페이지 방문하여 JSESSIONID 획득
        default_auth_cred = self._get_default_auth_cred()

        headers = self._generate_req_headers(default_auth_cred)
        data = self._generate_body(user_id, password)

        _res = self._try_login(headers, data)
        
        # 로그인 후 쿠키에서 JSESSIONID 추출
        try:
            session_id = self._get_j_session_id_from_response(_res)
            self._update_auth_cred(session_id)
        except KeyError:
            # 응답에 JSESSIONID가 없으면 기존 세션 유지
            self._update_auth_cred(default_auth_cred)

    def add_auth_cred_to_headers(self, headers: dict) -> str:
        assert type(headers) == dict
        copied_headers = copy.deepcopy(headers)
        copied_headers["Cookie"] = f"JSESSIONID={self._AUTH_CRED}"
        return copied_headers

    def _get_default_auth_cred(self):
        # 2026년 리뉴얼: 로그인"https://www.dhlottery.co.kr/main",            "https://www.dhlottery.co.kr/login",
            headers={"User-Agent": self._REQ_HEADERS["User-Agent"]}
                return self._get_j_session_id_from_response(res)

    def _get_j_session_id_from_response(self, res: requests.Response):
        assert type(res) == requests.Response
        for cookie in res.cookies:
            if cookie.name == "JSESSIONID":
                return cookie.value
        raise KeyError("JSESSIONID cookie is not set in response")

    def _generate_req_headers(self, j_session_id: str):
        assert type(j_session_id) == str
        copied_headers = copy.deepcopy(self._REQ_HEADERS)
        copied_headers["Cookie"] = f"JSESSIONID={j_session_id}"
        return copied_headers

    def _generate_body(self, user_id: str, password: str):
        assert type(user_id) == str
        assert type(password) == str
        return {
            "returnUrl": "https://www.dhlottery.co.kr/common.do?method=main",
            "userId": user_id,
            "password": password,
            "checkSave": "on",
            "newsEventYn": "",
        }

    def _try_login(self, headers: dict, data: dict):
        assert type(headers) == dict
        assert type(data) == dict
        res = self.http_client.post(
            "https://www.dhlottery.co.kr/userSsl.do?method=login",
            headers=headers,
            data=data,
        )
        return res

    def _update_auth_cred(self, j_session_id: str) -> None:
        assert type(j_session_id) == str
        # TODO: judge whether login is success or not
        # 로그인 실패해도 jsession 값이 갱신되기 때문에, 마이페이지 방문 등으로 판단해야 할 듯
        # + 비번 5번 틀렸을 경우엔 비번 정확해도 로그인 실패함
        self._AUTH_CRED = j_session_id
