import socket
import random
import time
from datetime import datetime
import struct
import threading
import select

# 配置服务器IP和端口
SERVER_IP = '0.0.0.0'
SERVER_PORT = 12311
PACKET_SIZE = 203  # 数据包大小：2 bytes for Seq no, 1 byte for ver, 200 bytes for "other content"
LOSS_RATE = 0.3  # 丢包率为30%
RESPONSE_CONTENT_SIZE = 200  # "other content" 的大小

# 创建并绑定UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")


def handle_client(data, client_address):
    """
    处理客户端发送的消息并发送相应的响应
    """
    try:
        # 解析收到的数据包
        # 模拟tcp连接释放
        if data == b'SYN':
            server_socket.sendto(b'SYN-ACK', client_address)
        elif data == b'ACK':
            print(f"Connection established with {client_address}")
        elif data.startswith(b'FIN'):
            server_socket.sendto(b'ACK', client_address)
            server_socket.sendto(b'FIN', client_address)
        elif data.startswith(b'FIN-ACK'):
            print(f"Connection with {client_address} closed")
        else:
            seq_no, ver, other_content = struct.unpack('!Hb200s', data)

            # 模拟丢包
            if random.random() < LOSS_RATE:
                print(f"Simulated packet loss for Seq no: {seq_no}")
                return

            # 获取服务器当前时间
            server_time = time.time()
            nserver_time = datetime.fromtimestamp(server_time).strftime('%Y-%m-%d-%H-%M-%S.%f').encode('utf-8')

            # 构建响应数据包
            response = struct.pack('!Hb200s', seq_no, ver, nserver_time.ljust(200))

            # 发送响应数据包
            server_socket.sendto(response, client_address)
            print(f"Response sent to {client_address} for Seq no: {seq_no}")
    except Exception as e:
        print(e)


while True:
    try:
        readable, _, _ = select.select([server_socket], [], [])
        for sock in readable:
            if sock == server_socket:
                # 接收数据包
                data, client_address = server_socket.recvfrom(PACKET_SIZE)
                client_thread = threading.Thread(target=handle_client, args=(data, client_address))
                client_thread.start()
    except KeyboardInterrupt:
        break
    except ConnectionError:
        break


server_socket.close()

