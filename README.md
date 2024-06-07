#UDP Socket Programming
## 文件列表
- udpserver.py：服务器端代码
- udpclient.py：客户端代码
- readme.txt：运行说明文档

## 运行环境
- Python 3.6 或更高版本

## 配置选项
- 客户端启动命令行格式：
python3 udpclient.py <server_ip> <server_port>
例如：
python3 udpclient.py 192.168.1.100 12345

- 服务器启动命令行格式：
python3 udpserver.py

## 程序运行说明
- 在服务器端运行 udpserver.py，启动服务器。
- 在客户端运行 udpclient.py，指定服务器 IP 地址和端口.
- 程序将模拟 UDP 连接并进行数据交互，客户端将发送 12 个请求数据包到服务器，服务器将随机模拟丢包并进行响应。客户端将打印出每个数据包的序号、服务器 IP 和端口号、往返时间（RTT）以及服务器时间。
- 客户端完成发送后，将打印出汇总信息，包括接收到的 UDP 数据包数量、丢包率、最大 RTT、最小 RTT、平均 RTT、RTT 标准差以及服务器响应时间跨度。
- 程序最后将模拟 TCP 连接释放过程，并关闭客户端与服务器之间的连接。

