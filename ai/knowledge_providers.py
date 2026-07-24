"""
外部知识库提供者模块 - 支持多种主流知识库平台的API接入

支持的提供商:
  1. webpage: 通用网页抓取（BeautifulSoup解析）
  2. feishu_wiki: 飞书知识库API（tenant_access_token认证）
  3. generic_api: 通用RESTful API接口

调用流程:
  管理员选择提供商类型 → 填写对应凭证 → 系统自动获取内容 → 切分+向量化 → 存入本地数据库
"""
import json
import os
import requests


class BaseKnowledgeProvider:
    """知识库提供者基类"""

    name = "base"
    display_name = "基础"

    def __init__(self, config):
        """
        Args:
            config: dict, 包含该提供商需要的配置信息
                - url: 目标URL或API地址
                - app_id / app_secret / api_key 等: 凭证信息
        """
        self.config = config or {}

    def fetch_content(self):
        """
        从外部源获取文本内容
        
        Returns:
            str: 获取到的纯文本内容
            
        Raises:
            Exception: 获取失败时抛出异常，包含错误描述
        """
        raise NotImplementedError("子类必须实现 fetch_content 方法")

    @staticmethod
    def get_form_fields():
        """
        返回前端表单字段定义列表
        
        Returns:
            list[dict]: 每个dict包含:
                - field: 字段名(str)
                - label: 显示标签(str)
                - type: 输入类型(text/url/textarea/password/select)
                - placeholder: 占位文字(str)
                - required: 是否必填(bool)
                - options: select类型的选项(list)
                - help_text: 帮助提示(str)
        """
        return []

    def validate_config(self):
        """验证配置是否完整有效"""
        return True, ""


class WebpageProvider(BaseKnowledgeProvider):
    """通用网页抓取提供者 - 通过BeautifulSoup解析网页提取纯文本"""

    name = "webpage"
    display_name = "网页链接"

    @staticmethod
    def _browser_headers(url):
        """构造接近真实浏览器的请求头(避免被反爬拦截)。

        注意: 不要手动设置 Accept-Encoding, 否则 requests 不会自动解压响应。
        """
        referer = ''
        try:
            from urllib.parse import urlparse
            p = urlparse(url)
            referer = f"{p.scheme}://{p.netloc}/"
        except Exception:
            pass
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': referer,
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    @staticmethod
    def _fetch_site_cookies(url):
        """抓取目标站点首页以拿到反爬所需的 Cookie(如百度百科的 BAIDUID)。"""
        try:
            from urllib.parse import urlparse
            p = urlparse(url)
            origin = f"{p.scheme}://{p.netloc}/"
            r = requests.get(
                origin,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
                timeout=15,
            )
            if r.cookies:
                return '; '.join(f"{k}={v}" for k, v in r.cookies.items())
        except Exception:
            pass
        return ''

    def fetch_content(self):
        url = self.config.get('url', '')
        if not url:
            raise Exception("URL不能为空")

        headers = self._browser_headers(url)

        try:
            resp = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException as e:
            raise Exception(f"请求发送失败: {e}")

        # 被反爬拦截(403/401/429)时, 先获取站点Cookie再重试一次
        if resp.status_code in (401, 403, 429):
            cookie = self._fetch_site_cookies(url)
            if cookie:
                headers['Cookie'] = cookie
                try:
                    resp = requests.get(url, headers=headers, timeout=30)
                except requests.RequestException:
                    pass

        resp.encoding = resp.apparent_encoding or 'utf-8'

        if resp.status_code != 200:
            raise Exception(
                f"无法访问URL (HTTP {resp.status_code})。该站点可能启用了反爬机制，"
                f"请更换为其他可直接公开访问的来源，或手动复制内容后通过文本方式导入。"
            )

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'lxml')

        # 检测反爬验证页(如「百度安全验证」/Cloudflare验证): 这类页面可能返回200,
        # 但正文为空且需要浏览器执行JS挑战, requests无法绕过。
        if self._is_blocked_page(resp.text, soup):
            raise Exception(
                "该网页返回了「安全验证」拦截页，站点禁止自动化抓取。"
                "请改用其他来源（如维基百科、政府/机构官网等可直接访问的页面），"
                "或手动复制正文后通过文本方式导入。"
            )

        # 移除无关标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()

        text = soup.get_text(separator='\n', strip=True)

        # 清理多余空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        if not text.strip():
            raise Exception("无法从该URL提取有效文本内容")

        return text

    @staticmethod
    def _is_blocked_page(html_text, soup):
        """判断响应是否为反爬验证页(返回200但无真实正文)"""
        lowered = (html_text or '').lower()
        markers = [
            '安全验证', '百度安全验证', 'verify you are a human',
            'just a moment', 'checking your browser', 'captcha',
            'enable javascript and cookies to continue',
            'access denied', 'are you a robot',
        ]
        if any(m in lowered for m in markers):
            return True
        # 正文几乎为空(验证页 body 通常为空)
        try:
            title = (soup.title.string or '') if soup.title else ''
            if '验证' in title or 'verify' in title.lower():
                return True
        except Exception:
            pass
        body_text = soup.get_text(separator='\n', strip=True).strip()
        return len(body_text) < 30

    @staticmethod
    def get_form_fields():
        return [
            {
                'field': 'url',
                'label': '网页URL',
                'type': 'url',
                'placeholder': 'https://www.example.com/article 或 https://www.court.gov.cn/xinxi/...',
                'required': True,
                'help_text': '系统会自动抓取该网页的正文内容并建立索引'
            }
        ]

    def validate_config(self):
        url = self.config.get('url', '')
        if not url or not url.startswith(('http://', 'https://')):
            return False, "请输入有效的URL地址"
        return True, ""


class FeishuWikiProvider(BaseKnowledgeProvider):
    """飞书知识库API提供者 - 通过飞书开放平台API获取知识库文档内容
    
    参考文档: https://open.feishu.cn/document/server-docs/docs/wiki-v2/wiki-overview
    
    认证方式: tenant_access_token (app_id + app_secret)
    
    API流程:
      1. 用 app_id + app_secret 获取 tenant_access_token
      2. 用 token 获取知识空间节点列表
      3. 对每个文档节点获取纯文本内容
    """

    name = "feishu_wiki"
    display_name = "飞书知识库"

    FEISHU_AUTH_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    FEISHU_SPACE_LIST_URL = "https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes"
    FEISHU_DOC_RAW_URL = "https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"

    def fetch_content(self):
        space_id = self.config.get('space_id', '')
        app_id = self.config.get('app_id', '')
        app_secret = self.config.get('app_secret', '')

        if not all([space_id, app_id, app_secret]):
            raise Exception("飞书知识库需要填写 space_id、app_id 和 app_secret")

        # Step 1: 获取 tenant_access_token
        try:
            auth_resp = requests.post(
                self.FEISHU_AUTH_URL,
                json={"app_id": app_id, "app_secret": app_secret},
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            auth_data = auth_resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"连接飞书服务器失败: {e}")

        if auth_data.get('code') != 0:
            msg = auth_data.get('msg', '未知错误')
            raise Exception(f"飞书认证失败 (code={auth_data.get('code')}): {msg}")

        token = auth_data.get('data', {}).get('tenant_access_token')
        if not token:
            raise Exception("未能获取到飞书访问令牌")

        headers = {'Authorization': f'Bearer {token}'}

        # Step 2: 获取知识空间下的所有节点
        try:
            nodes_resp = requests.get(
                self.FEISHU_SPACE_LIST_URL.format(space_id=space_id),
                headers=headers,
                timeout=30,
                params={'page_size': 50}
            )
            nodes_data = nodes_resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取飞书知识空间节点失败: {e}")

        if nodes_data.get('code') != 0:
            msg = nodes_data.get('msg', '未知错误')
            raise Exception(f"获取知识空间失败 (code={nodes_data.get('code')}): {msg}")

        items = nodes_data.get('data', {}).get('items', [])
        if not items:
            raise Exception(f"知识空间 {space_id} 下没有找到任何文档节点")

        # Step 3: 逐个获取文档纯文本内容
        all_texts = []
        doc_count = 0
        for node in items:
            obj_type = node.get('obj_type', '')
            obj_token = node.get('obj_token', '')
            node_title = node.get('node_name', '')

            # 只处理文档类型
            if obj_type != 'docx':
                continue

            try:
                doc_resp = requests.get(
                    self.FEISHU_DOC_RAW_URL.format(document_id=obj_token),
                    headers=headers,
                    timeout=30
                )
                doc_data = doc_resp.json()
            except requests.exceptions.RequestException:
                continue

            if doc_data.get('code') == 0:
                content = doc_data.get('data', {}).get('content', '')
                if content and content.strip():
                    all_texts.append(f"【{node_title}】\n{content}")
                    doc_count += 1

        if not all_texts:
            raise Exception(f"从知识空间 {space_id} 的 {len(items)} 个节点中未提取到任何有效文档内容")

        return '\n\n'.join(all_texts)

    @staticmethod
    def get_form_fields():
        return [
            {
                'field': 'space_id',
                'label': '知识空间ID (space_id)',
                'type': 'text',
                'placeholder': '7034502641455497244',
                'required': True,
                'help_text': '在飞书知识库设置页面地址栏中复制数字部分'
            },
            {
                'field': 'app_id',
                'label': '应用ID (app_id)',
                'type': 'text',
                'placeholder': 'cli_xxxxxxxxxxxxxxxx',
                'required': True,
                'help_text': '飞书开放平台创建的自建应用的 App ID'
            },
            {
                'field': 'app_secret',
                'label': '应用密钥 (app_secret)',
                'type': 'password',
                'placeholder': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'required': True,
                'help_text': '飞书开放平台创建的自建应用的 App Secret'
            }
        ]

    def validate_config(self):
        space_id = self.config.get('space_id', '')
        app_id = self.config.get('app_id', '')
        app_secret = self.config.get('app_secret', '')
        if not space_id or not space_id.isdigit():
            return False, "请输入有效的知识空间ID（数字）"
        if not app_id:
            return False, "请输入飞书应用ID"
        if not app_secret:
            return False, "请输入飞书应用密钥"
        return True, ""


class GenericApiProvider(BaseKnowledgeProvider):
    """通用RESTful API提供者 - 调用任意返回JSON文本内容的API
    
    适用场景:
      - 自建知识库后端API
      - 腾讯元器/IMA等第三方平台API
      - 任何返回文本内容的RESTful接口
    
    期望响应格式:
      {"content": "..."} 或 {"data": {"content": "..."}}
      支持通过 json_path 配置指定数据路径
    """

    name = "generic_api"
    display_name = "通用API接口"

    def fetch_content(self):
        api_url = self.config.get('api_url', '')
        api_key = self.config.get('api_key', '')
        method = self.config.get('method', 'GET').upper()
        json_path = self.config.get('json_path', 'content')  # 默认取 response.content

        if not api_url:
            raise Exception("API URL不能为空")

        headers = {
            'User-Agent': 'DigitalHeritage-KnowledgeSync/1.0',
            'Accept': 'application/json',
        }

        # 如果有API Key，添加到请求头
        if api_key:
            key_header = self.config.get('key_header', 'Authorization').strip()
            key_format = self.config.get('key_format', 'Bearer {key}').strip()
            headers[key_header] = key_format.format(key=api_key)

        # 构造请求体
        request_body = None
        body_json = self.config.get('body_json', '').strip()
        if method == 'POST' and body_json:
            import ast
            try:
                request_body = ast.literal_eval(body_json)
            except (ValueError, SyntaxError):
                request_body = body_json

        try:
            if method == 'POST':
                resp = requests.post(api_url, json=request_body, headers=headers, timeout=60)
            else:
                params_str = self.config.get('params', '').strip()
                params = {}
                if params_str:
                    import urllib.parse
                    params = dict(urllib.parse.parse_qsl(params_str))
                resp = requests.get(api_url, params=params, headers=headers, timeout=60)
        except requests.exceptions.Timeout:
            raise Exception("API请求超时（超过60秒），请检查网络或API是否可用")
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到API地址: {api_url}")
        except Exception as e:
            raise Exception(f"API请求失败: {e}")

        if resp.status_code != 200:
            raise Exception(f"API返回错误状态码: HTTP {resp.status_code}\n响应内容: {resp.text[:500]}")

        # 解析JSON响应
        try:
            data = resp.json()
        except Exception:
            # 如果不是JSON，尝试直接使用文本
            text = resp.text.strip()
            if text:
                return text
            raise Exception("API返回的内容无法解析为JSON且为空")

        # 按 json_path 提取内容
        content = self._extract_by_path(data, json_path)

        if not content or not str(content).strip():
            raise Exception(f"从API响应中按路径 '{json_path}' 未提取到有效内容。\n原始响应(前500字): {str(data)[:500]}")

        return str(content).strip()

    def _extract_by_path(self, data, path):
        """支持点号分隔的JSON路径提取，如 'data.content' -> data['data']['content']"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    @staticmethod
    def get_form_fields():
        return [
            {
                'field': 'api_url',
                'label': 'API地址',
                'type': 'url',
                'placeholder': 'https://api.example.com/v1/knowledge/retrieve',
                'required': True,
                'help_text': '目标API的完整URL地址'
            },
            {
                'field': 'method',
                'label': '请求方法',
                'type': 'select',
                'options': [
                    {'value': 'GET', 'label': 'GET'},
                    {'value': 'POST', 'label': 'POST'}
                ],
                'default': 'GET',
                'help_text': ''
            },
            {
                'field': 'api_key',
                'label': 'API密钥 (可选)',
                'type': 'password',
                'placeholder': 'sk-xxx 或 Bearer Token',
                'required': False,
                'help_text': '用于身份验证的密钥'
            },
            {
                'field': 'key_header',
                'label': '密钥Header名称',
                'type': 'text',
                'placeholder': 'Authorization',
                'required': False,
                'help_text': '默认 Authorization，可改为 X-API-Key 等'
            },
            {
                'field': 'key_format',
                'label': '密钥格式模板',
                'type': 'text',
                'placeholder': 'Bearer {key}',
                'required': False,
                'help_text': '{key} 会被替换为实际密钥值'
            },
            {
                'field': 'json_path',
                'label': '响应内容路径',
                'type': 'text',
                'placeholder': 'content',
                'required': False,
                'help_text': '从API响应JSON中提取内容的路径，如 data.content、items.0.text 等'
            },
            {
                'field': 'params',
                'label': 'GET参数 (仅GET方法)',
                'type': 'textarea',
                'placeholder': 'query=法律&page=1',
                'required': False,
                'help_text': 'GET请求时的查询参数，格式: key=value&key2=value2'
            },
            {
                'field': 'body_json',
                'label': 'POST请求体 (仅POST方法)',
                'type': 'textarea',
                'placeholder': '{"query": "法律", "top_k": 10}',
                'required': False,
                'help_text': 'POST请求时的JSON请求体'
            }
        ]

    def validate_config(self):
        api_url = self.config.get('api_url', '')
        if not api_url or not api_url.startswith(('http://', 'https://')):
            return False, "请输入有效的API地址"
        return True, ""


# ============================================================
# 提供者注册表 - 所有可用的知识库提供者
# ============================================================
PROVIDER_REGISTRY = {
    WebpageProvider.name: WebpageProvider,
    FeishuWikiProvider.name: FeishuWikiProvider,
    GenericApiProvider.name: GenericApiProvider,
}


def get_provider(provider_name, config):
    """
    工厂函数：根据名称获取对应的提供者实例
    
    Args:
        provider_name: 提供者名称(str)，如 'webpage'/'feishu_wiki'/'generic_api'
        config: 配置字典(dict)
    
    Returns:
        BaseKnowledgeProvider 子类实例
    
    Raises:
        ValueError: 不存在的提供者名称
    """
    cls = PROVIDER_REGISTRY.get(provider_name)
    if not cls:
        available = ', '.join(PROVIDER_REGISTRY.keys())
        raise ValueError(f"未知的知识库提供者: '{provider_name}'，可选值: {available}")
    return cls(config)


def get_all_providers_info():
    """
    返回所有提供者的基本信息供前端渲染表单
    
    Returns:
        list[dict]: [{'name': str, 'display_name': str, 'fields': list}, ...]
    """
    result = []
    for name, cls in PROVIDER_REGISTRY.items():
        result.append({
            'name': name,
            'display_name': cls.display_name,
            'form_fields': cls.get_form_fields()
        })
    return result
