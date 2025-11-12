* 腾讯云：域名➕网站托管➕云服务器➕备案➕域名解析

---

* 腾讯云静态网站托管：环境免费一个月，ssl证书免费3个月

---

* 七牛云对象储存：一个月，2月25过期

---

* 虚拟机防火墙放行端口

![](https://com.miui.notes/note_image/b984d6112996d32d70d2024fa243a669c745b027)

---

* 虚拟机修改IP地址

1. 进入ens33

![](https://com.miui.notes/note_image/8bbf220fae9fb5c09e19f17b9ffc5e0e18ea214b)

2. 将dhcp改为static，新增红框内容

![](https://com.miui.notes/note_image/dabf97143b01e8605c4686e3af9befc1f26acc76)

3. 重启网卡

![](https://com.miui.notes/note_image/f6c2ab850a5476bb37029dc8d1211ffddb34e957)

4. 最后访问外网：ping 8.8.8.8，再访问常见的网站：ping www.baidu.com

---

* docker配置代理

（以下方法不行的话，使用配置国内镜像）

![](https://com.miui.notes/note_image/896067d5982eb991780032199732740d38eb74e6)

![](https://com.miui.notes/note_image/82711fe297ab056b1fda9044c4ffc90734c8232a)

从自己的主机中看虚拟机的IPv4地址

![](https://com.miui.notes/note_image/768de1cc6f5697021e17f219f5c6e1d7000a0d71)

打开代理后，再打开VPN

![](https://com.miui.notes/note_image/bc81a0d54a8884c6bbec081f161c1206f09bded6)



---

* MySQL配置

一般面试经常问到，实际开发小项目几乎不用考虑

但是如果一直不去考虑数据库优化，真到了需要优化的时候，那就两眼一抹黑了

一般单表数据量在1万以上的时候，索引就必须得加上了

加上索引之后，单表数据在千万级别问题就不大了

然后可以考虑读写分离，主从同步这些

实在不行了，再考虑做水平分表

1. MySQL主从配置

    https://www.wolai.com/fengfeng/mzGYgQRiKP3J4p4qidDiPS

![](https://com.miui.notes/note_image/f8def1490eb1a6c1f6345229514e66e5257c8a59)

### 2.MySQL优化：索引优化，水平分表

    https://www.wolai.com/fengfeng/pXg4Q6X9giMznrZiQg63jG

### 3.后端连接数据库时，通过插件实现读写分离

![](https://com.miui.notes/note_image/36116886c3f43f42eed0b30a280aac92eec03c4d)

---

* 异步并发执行：goroutine协程，channel通道，锁

1. es同步MySQL

2. Redis定时任务：同步缓存中的数据到MySQL中

3. 发送站内消息：赞，收藏，评论和回复，系统消息

4. ai搜索文章，数据传输方式是流式，service中用goroutine协程接收ai接口的响应，接口服务器中用sse传输数据到客户端上

---

* 关于日志

日志中间件：

![](https://com.miui.notes/note_image/d4f0f0c2f5bec672ba6888e3536fb2383eb0602a)

关于日志：

![](https://com.miui.notes/note_image/ce5a3233f1ceb0aa31713ec76bb66a0ccc1d9677)

---

* jwt单令牌登陆认证：

![](https://com.miui.notes/note_image/05c4265dbe733447b272b3da1607b858d68e4332)

jwt的token主动失效，通过redis黑名单机制，存储失效的token：

![](https://com.miui.notes/note_image/a7c85fd4d1ec79dfc811d55ead7c1e199021387d)

jwt双令牌：

![](https://com.miui.notes/note_image/cde9cd3f7f83be443ab1859375a387f47879dd11)

---

* 邮箱注册：

![](https://com.miui.notes/note_image/2c71f146b4f406e41329702eb521f091f0eef8a5)

发送邮箱：

绑定邮箱：

![](https://com.miui.notes/note_image/27a0650a6929bdf1c81eebe09a665cd061c2ea58)

”邮箱注册：

![](https://com.miui.notes/note_image/b2ce81e1737b584d92569b8dd7e28c2a2f4a747f)

![](https://com.miui.notes/note_image/3525e322a27c40378add267fa3f8804f4b9f14fd)

---

* QQ登录：

1. 网站部署：简单的页面，有QQ登录按钮即可，QQ登录按钮点击显示成功信息

2. 网站域名备案：工信部备案➕公安备案(网页再加上一些具体的东西)

3. QQ接口审核：网站域名➕回调地址

4. 流程：

![](https://com.miui.notes/note_image/1f671fc72276da9798df5b85a5c0665536bfea9b)

1. 根据回调地址带的code，获取accessToken

2. 根据accessToken中的openid获取用户信息

![](https://com.miui.notes/note_image/e9f026a1ac23defd53cbf39b53bc495bfdf42c5d)

---

* elasticsearch分布式搜索引擎

es连接，创建es索引，es同步MySQL：

同步首先需要开启MySQL的binlog功能：

![](https://com.miui.notes/note_image/7ade3e1dba8c721af7fd890c4b1d6342d263bf3b)

![](https://com.miui.notes/note_image/8a914a921a92c96c7c2372eba9c3e696f608dcd9)

使用es搜索文章列表：

![](https://com.miui.notes/note_image/bb70e834515ee4b564053ba59e0c51e520093a6a)

![](https://com.miui.notes/note_image/21d2afeb86649ff133a05aded445d98167199665)

![](https://com.miui.notes/note_image/fab77bc70ff3a93c882aee222b27fe0e9ba7f646)

![](https://com.miui.notes/note_image/b52aab6b2687950ed992ce21eaf4c51562d13edd)

![](https://com.miui.notes/note_image/c60de23e81a94d880aeac93a41db6612860d09f2)

es全文搜索： 创建MySQL全文搜索表结构text_model，es构建全文搜索表索引，es同步mysql中的全文搜索记录表

![](https://com.miui.notes/note_image/52277b6999efdde5dbfcab351e00c6eedd9bc57c)

![](https://com.miui.notes/note_image/c5f0ff32b344eec28cf40a524b41a23d7d3ccb0b)

![](https://com.miui.notes/note_image/237723de364ec0e8677c38f996a9630bd07c570b)

![](https://com.miui.notes/note_image/bad73c9ffdf2f5f8b0fbd1ff73c40a1cf919ab29)

![](https://com.miui.notes/note_image/b6ecd8bc0f07fa8b0f40616af4fdfe9606ed8381)



---

* websockt私信：

历史会话列表sql语句：

![](https://com.miui.notes/note_image/49be84488b60b2fb6849edf1bab58fb4134a2e0e)

计算会话个数count：

![](https://com.miui.notes/note_image/ad9ab8ea8fe11827d3e699b9267e6a080a07a3ac)

历史会话列表sql语句解析：

![](https://com.miui.notes/note_image/0bdec426c0d002e98ac26a360a9969e026215092)

websocket：

![](https://com.miui.notes/note_image/ce1d1834c07473dd9e010cdebfeb393c386919b4)

![](https://com.miui.notes/note_image/dfea9b0cd3ad185590d1b5ff5926fc3b51529bf4)

![](https://com.miui.notes/note_image/400b1f28e6ca8d82939f13a26bfcaa73060ed6e7)

---

* 文章接入AI

### Ai返回的结果的数据传输方式有流式和非流式。

![](https://com.miui.notes/note_image/df6ff605fd2995c4bd6f3bf582431c9489c34394)



* ai非流式：

1.发起一个 HTTP POST 请求到指定的 API 地址。https://api.chatanywhere.tech/v1/chat/completions

![](https://com.miui.notes/note_image/ffd158c24d7d89153d2ef278026ee9862533b3dc)

![](https://com.miui.notes/note_image/db1f95818c950a8bb67d103fa86f26c2de8b3cac)

2. 非流式，一次性读取全部数据

* ai流式

流式原始的返回数据: data: {"id":"chatcmpl-B7JQbMi0lv9Exx2yOTYJNHPdvpCea","choices":[{"index":0,"delta":{"content":"可以"},"logprobs":null,"finish_reason":null}],"created":1741082677,"model":"gpt-3.5-turbo-0125","object":"chat.completion.chunk","system_fingerprint":"fp_b705f0c291"}

![](https://com.miui.notes/note_image/2e44369453898bfae85b90ae40d5f91310d523e8)

1.发起一个 HTTP POST 请求到指定的 API 地址。https://api.chatanywhere.tech/v1/chat/completions

![](https://com.miui.notes/note_image/19ea5c6ebbfcbe145c3f39eae28b13134f400946)

2. 流式，循环读取数据

![](https://com.miui.notes/note_image/2c28cdfabb73abbc6ffe802aaa132d3c08e16eba)



* 非流式函数封装

1.  请求体封装

![](https://com.miui.notes/note_image/407d1bd9ae9f5bc4eb8bcc31a21d001e8dd52a7a)

2. ai非流式和流式公共的http请求函数 func BaseRequest(r Request) (res *http.Response, err error){}

![](https://com.miui.notes/note_image/188e8c5724b416654f26479d28a769121afcac5a)

3. 导入提示词文件prompt

![](https://com.miui.notes/note_image/3a2072a77b7774218db3a0cf5428f4b23a1237da)

![](https://com.miui.notes/note_image/e1a488d1b379b3ca31e38767fafcfef627ade696)

4. ai非流式函数

![](https://com.miui.notes/note_image/c629ef5caa8bac3488cf84b0fc352965e9783858)

![](https://com.miui.notes/note_image/8b79bc41a8b56462e764415d0b9e44e4ff3f63c3)

* 流式函数封装

流式原始的返回数据: data: {"id":"chatcmpl-B7JQbMi0lv9Exx2yOTYJNHPdvpCea","choices":[{"index":0,"delta":{"content":"可以"},"logprobs":null,"finish_reason":null}],"created":1741082677,"model":"gpt-3.5-turbo-0125","object":"chat.completion.chunk","system_fingerprint":"fp_b705f0c291"}

1.  流式返回封装 和 流式返回的data中的Choices封装

![](https://com.miui.notes/note_image/16057b39e7684b11421d75272116bba6edab1913)

2. ai非流式和流式公共的http请求函数 func BaseRequest(r Request) (res *http.Response, err error){}

![](https://com.miui.notes/note_image/1924e78d2b921d5206a2ab8e318fe220b09b327a)

3. 导入提示词文件prompt

![](https://com.miui.notes/note_image/126df115341b45c540652f0d11b2ef9fbc7ab810)

![](https://com.miui.notes/note_image/ab2e7d025886431326466451e0933423aadee02d)

4. ai对话非流式函数 func ChatStream(content string, params string) (msgChan chan string, err error) {}

![](https://com.miui.notes/note_image/f890eb6290fe06c9c6246162b186122e2d13e247)

![](https://com.miui.notes/note_image/a648ed1005c0b40c2f8eeff9bf6295b1191bce96)



* ai接口

1. Ai分析一篇文章与正文相关的标题简介分类和标签。

（1）请求体和响应体封装

![](https://com.miui.notes/note_image/12fa3906150c5b1b63aefda1f4eeafd36173b5a5)

（2）ai分析文章函数

![](https://com.miui.notes/note_image/5aa5d66e5fb5af1bf3e2f84c9da00df2bd017061)

2. Ai搜索文章。

（1）请求体封装

![](https://com.miui.notes/note_image/145b478e6b0b4015cf958fc8167d325b085091f8)

（2）ai搜索文章函

        流程：

![](https://com.miui.notes/note_image/f36b56141e56fabb77e030b290b25a31b88a7107)

       函数：

![](https://com.miui.notes/note_image/1a9330ff23ab51793c876089f763c2d2e80db951)

（3）SSE技术

![](https://com.miui.notes/note_image/25541ada490b7e5f4764574adf33c8ff284f7a76)

     函数放在common的res下：

![](https://com.miui.notes/note_image/4381d9a5651104ed8ad44c7abaa680f878546717)

---

* 文章详情缓存中间件

点击文章详情，内容一直是第一次点击的文章。问题可能出在缓存键（key）的生成逻辑上。当前的缓存键没有正确区分不同的文章，导致不同文章的数据覆盖或混淆。

![](https://com.miui.notes/note_image/14a5ae518f1fca38fc62bb139b5baf0a3f9a6c4d)

解决： 确保缓存键中包含文章的唯一标识

1. 修改缓存键的生成逻辑，确保每篇文章的缓存键是唯一的。例如，可以在查询参数中明确包含文章ID。

2. 确保文章ID正确传递

3.  修改缓存键生成逻辑

![](https://com.miui.notes/note_image/2f466ffdc73497538a3a2a5de727f442f4a9d76a)



![](https://com.miui.notes/note_image/23b675d404646cad3b13af29f053bf96dac32428)

![](https://com.miui.notes/note_image/533cdaa0c2b328c0ca5721f888544ebcc19862f1)

缓存中间间请求部分：

![](https://com.miui.notes/note_image/74d3584c55edd777b0c304f8cdd7a9988d07c617)

---

* 项目部署

从服务器拉文件到本地当前目录下：

![](https://com.miui.notes/note_image/869960475b13d0d965bec71d157c99833d2c43e9)

1. 内网部署：

> -t 或 --tag：

用于为构建的镜像指定一个名称和标签（tag）。

![](https://com.miui.notes/note_image/6118d12adf4abbb2273b0c2672ef88602371da32)

2. 服务器部署：

> -o 或 --output：

用于指定输出文件的路径和名称。

![](https://com.miui.notes/note_image/10b772bc14819ff0ed522f9a844a34fb48d5df2d)

> docker load：

这是 Docker 的一个命令，用于从 tar 文件或标准输入中加载镜像。

用于从之前保存的镜像文件（如通过 docker save 生成的文件）中恢复镜像。

> < blogx_server_v2.tar：

这是一个重定向操作，输入重定向 (<) 作用：将文件的内容作为命令的输入。输出重定向 (> 和 >>) 作用：将命令的输出重定向到文件。

表示将 blogx_server_v2.tar 文件的内容作为 docker load 命令的输入。

blogx_server_v2.tar 是之前通过 docker save 命令保存的镜像文件。

![](https://com.miui.notes/note_image/761f372b23b14317c8e5dedd083567f00cf276e7)

![](https://com.miui.notes/note_image/4f67a40871091671261b3c927c3ae53509d74423)

---





- [x] QQ登录api需要增加判断站点配置文件是否开启

- [x] QQ登录api需要增加创建用户登录表(参考pwd登录)

- [x] 文章列表查询，根据收藏夹id查询

- [x] 私信未读数量，自己修改site_msg_api下的 user_msg

- [x] 自己修改search_api下的article-search：加上判断是否为空，否则分页的时候，searchArticleMap中没有置顶的文章的数据，查不到Title和Abstract

![](https://com.miui.notes/note_image/db0d16b749205310eef895967902f2c484bca0d6)

- [x] 文章详情的router：加上缓存中间间后，点击文章详情，文章内容一直是第一次点击的文章。

- [x] 自己修改search_api下的article_search：query.must修改为query.Should，must是and的意思，不然只能搜索出兴趣标签的文章

![](https://com.miui.notes/note_image/325f888098a6fc00be45f3e304a8bafea15ac55d)

- [x] 自己修改ai_api下的article_ai的es搜索，分页数据修改

![](https://com.miui.notes/note_image/661bfc4bb2143f33e7ecbcb12777900b6198f61b)

- [x] 后端268个视频，服务器时间差8小时问题解决

- [x] 导入数据库：服务器进入deploy文件，

>       docker exec -it mysql-master bash

>       use blogx

>       source blogx.sql

- [x] ai_service下的chatStream流式接口，在协程中给channel发送数据，不做判断是否为空的话，可能会导致空指针问题，导致通道异常关闭。

- [x] 重新在虚拟机中部署新的项目，需要把之前的容器挂载的文件数据删除，否则数据库和ES会使用之前的缓存，同步会出问题

> 挂载 ./master/data 到容器的 /var/lib/mysql 是为了实现数据的持久化和可移植性，将容器内的 MySQL 数据目录挂载到宿主机的文件系统中，确保数据不会因为容器的停止、删除或重建而丢失

> 挂载./es/data到容器/usr/share/elasticsearch/data是为了实现数据的持久化和可移植性，将容器内的 ElasticSearch 数据目录挂载到宿主机的文件系统中，确保数据不会因为容器的停止、删除或重建而丢失

![](https://com.miui.notes/note_image/887f9bd90b07abab27ee885ffd15045e152e85dd)


