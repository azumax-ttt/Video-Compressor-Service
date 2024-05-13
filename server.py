import socket
import os
import subprocess

def process_video(input_file, output_file, method):
    if method == 0:
        cmd = f'ffmpeg -i {input_file} -vcodec h264 -acodec aac {output_file}'
    elif method == 1:
        cmd = f'ffmpeg -i {input_file} -s 1280x720 -c:a copy {output_file}'
    elif method == 2:
        cmd = f'ffmpeg -i {input_file} -aspect 16:9 -c:v libx264 -c:a copy {output_file}'
    elif method == 3:
        cmd = f'ffmpeg -i {input_file} -vn -acodec mp3 {output_file}.mp3'
    elif method == 4:
        cmd = f'ffmpeg -i {input_file} -ss 00:00:10 -to 00:00:20 -c:v libvpx -c:a libvorbis {output_file}.webm'
    subprocess.run(cmd, shell=True)

server_address = '0.0.0.0'
server_port = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((server_address, server_port))
sock.listen(1)
print('クライアントからの接続待機中...')

while True:
    connection, client_address = sock.accept()
    try:
        header = connection.recv(8)
        filename_length = int.from_bytes(header[:1], "big")
        method = int.from_bytes(header[1:2], "big")
        data_length = int.from_bytes(header[2:], "big")

        filename = connection.recv(filename_length).decode('utf-8')
        new_file_path = os.path.join('newFiles', filename)
        os.makedirs('newFiles', exist_ok=True)

        with open(new_file_path, 'wb') as f:
            while data_length > 0:
                data = connection.recv(min(4096, data_length))
                f.write(data)
                data_length -= len(data)

        output_file_path = os.path.splitext(new_file_path)[0] + '.mp4'
        process_video(new_file_path, output_file_path, method)
        print(f'ファイルを作成しました -> {output_file_path}')

    except Exception as e:
        print(f'Error: {str(e)}')

    finally:
        print('サーバーシャットダウン...')
        connection.close()
