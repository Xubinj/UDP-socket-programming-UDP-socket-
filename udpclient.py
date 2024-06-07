import socket
import struct
import time
from datetime import datetime
import statistics
import sys

# 配置服务器IP和端口
SERVER_IP = sys.argv[1]  # 从命令行参数获取服务器IP
SERVER_PORT = int(sys.argv[2])  # 从命令行参数获取服务器端口
PACKET_SIZE = 203  # 数据包大小：2 bytes for Seq no, 1 byte for ver, 200 bytes for "other content"
TIMEOUT = 0.1  # 超时时间100ms
RETRIES = 2  # 最大重传次数

# 创建UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

# 模拟tcp连接建立过程（三次握手）
print(f"Establishing connection to {SERVER_IP}:{SERVER_PORT}")
# 发送 SYN 报文
client_socket.sendto(b'SYN', (SERVER_IP, SERVER_PORT))
try:
    response, _ = client_socket.recvfrom(PACKET_SIZE)
    if response == b'SYN-ACK':
        client_socket.sendto(b'ACK', (SERVER_IP, SERVER_PORT))
        print("Connection established")
    else:
        print("Failed to establish connection")
        client_socket.close()
        sys.exit(1)
except socket.timeout:
    print("Connection timed out")
    client_socket.close()
    sys.exit(1)

# 初始化统计数据
received_packets = 0
rtt_list = []
first_response_time = None
last_response_time = None

# 发送12个请求数据包
for i in range(1, 13):
    seq_no = i
    ver = 2
    other_content = b'x' * 200
    request_packet = struct.pack('!Hb200s', seq_no, ver, other_content)

    for attempt in range(RETRIES + 1):
        try:
            # 记录发送时间
            send_time = time.time()
            client_socket.sendto(request_packet, (SERVER_IP, SERVER_PORT))

            # 接收响应数据包
            response_packet, _ = client_socket.recvfrom(PACKET_SIZE)
            recv_time = time.time()

            # 解析响应数据包
            response_seq_no, response_ver, response_content = struct.unpack('!Hb200s', response_packet)

            # 计算RTT
            rtt = (recv_time - send_time) * 1000
            server_time = response_content.decode().strip()

            # 打印响应信息
            print(
                f"Sequence No: {response_seq_no}, Server: {SERVER_IP}:{SERVER_PORT}, RTT: {rtt:.2f} ms, Server Time: {server_time[11:19]}")

            # 更新统计数据
            received_packets += 1
            rtt_list.append(rtt)

            if first_response_time is None:
                first_response_time = datetime.strptime(server_time, "%Y-%m-%d-%H-%M-%S.%f").timestamp()
            last_response_time = datetime.strptime(server_time, "%Y-%m-%d-%H-%M-%S.%f").timestamp()
            break
        except socket.timeout:
            # 处理超时重传
            if attempt < RETRIES:
                print(f"Sequence No: {seq_no}, request timeout, retrying...")
            else:
                print(f"Sequence No: {seq_no}, request timeout, giving up...")
        except Exception as e:
            print(f"An error occurred: {e}")
            break

# 计算并打印汇总信息
if rtt_list:
    max_rtt = max(rtt_list)
    min_rtt = min(rtt_list)
    avg_rtt = sum(rtt_list) / len(rtt_list)
    std_rtt = statistics.stdev(rtt_list) if len(rtt_list) > 1 else 0.0
else:
    max_rtt = min_rtt = avg_rtt = std_rtt = 0.0

# 计算服务器响应时间跨度
total_rtt = (last_response_time-first_response_time)*1000 if first_response_time and last_response_time else 0
print("\n--- Summary ---")
print(f"Received UDP packets: {received_packets}")
print(f"Loss rate: {((12 - received_packets) / 12) * 100:.2f}%")
print(f"Max RTT: {max_rtt:.2f} ms")
print(f"Min RTT: {min_rtt:.2f} ms")
print(f"Average RTT: {avg_rtt:.2f} ms")
print(f"RTT Standard Deviation: {std_rtt:.2f} ms")
print(f"Server response time span: {total_rtt:.2f} ms")

# 模拟连接释放过程（四次挥手）
print("Releasing connection")
client_socket.sendto(b'FIN', (SERVER_IP, SERVER_PORT))
try:
    response, _ = client_socket.recvfrom(PACKET_SIZE)
    if response == b'ACK':
        response, _ = client_socket.recvfrom(PACKET_SIZE)
        if response == b'FIN':
            client_socket.sendto(b'FIN-ACK', (SERVER_IP, SERVER_PORT))
            print("Connection released")
            client_socket.close()
except socket.timeout:
    print("Connection release timed out")
