import socket
import os
import subprocess

def convert_to_mp4(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', output_file]
    subprocess.run(command, check=True)

def protocol_header(filename_length, method, data_length):
    return filename_length.to_bytes(1, 'big') + method.to_bytes(1, 'big') + data_length.to_bytes(6, 'big')

server_address = '0.0.0.0'
server_port = 9001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_address, server_port))

file_name = input('処理するファイルを選択してください（例: example.mov）: ')

print('----------------------------------------')
print('利用したい処理を番号で選択してください')
print('0: 動画を圧縮する')
print('1: 動画の解像度を変更する')
print('2: 動画のアスペクト比を変更する')
print('3: 動画を音声に変換する')
print('4: 指定した時間範囲で GIF や WEBM を作成')
method = int(input('利用する処理: '))

directory_path = os.getcwd()
file_path = os.path.join(directory_path, 'files', file_name)
output_file_path = os.path.join(directory_path, 'mp4files', os.path.splitext(file_name)[0] + '.mp4')
os.makedirs('mp4files', exist_ok=True)

if not os.path.exists(file_path):
    print('ファイルが存在しません')
    sock.close()
    exit()

convert_to_mp4(file_path, output_file_path)

with open(output_file_path, 'rb') as f:
    filesize = os.path.getsize(output_file_path)
    filename_bits = os.path.basename(output_file_path).encode('utf-8')
    header = protocol_header(len(filename_bits), method, filesize)
    
    sock.send(header)
    sock.send(filename_bits)
    data = f.read(4096)
    while data:
        sock.send(data)
        data = f.read(4096)

print('ファイルを送信しました')
sock.close()
