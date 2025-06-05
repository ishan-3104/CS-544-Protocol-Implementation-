import asyncio
import struct
import hashlib
from server.protocol import FILE_META, FILE_CHUNK, FILE_ACK
from server.state import SessionState

class FTPQServer:
    def __init__(self):
        self.state = SessionState.INIT
        self.file = None
        self.expected_size = 0
        self.received_bytes = 0
        self.expected_hash = ""
        self.filename = ""
        self.buffer = b""

    def compute_sha256(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()

    def process_buffer(self):
        responses = []
        while self.buffer:
            msg_type = self.buffer[0]

            if msg_type == FILE_META:
                if len(self.buffer) < 6:
                    break  # Not enough for version + filename length
                version = self.buffer[1]
                fn_len = struct.unpack('!I', self.buffer[2:6])[0]

                if len(self.buffer) < 6 + fn_len + 8 + 32:
                    break  # Not enough for full FileMeta

                self.filename = struct.unpack(f'!{fn_len}s', self.buffer[6:6+fn_len])[0].decode()
                self.expected_size = struct.unpack('!Q', self.buffer[6+fn_len:6+fn_len+8])[0]
                self.expected_hash = self.buffer[6+fn_len+8:6+fn_len+8+32].hex()

                self.file = open(f"received_{self.filename}", "wb")
                self.received_bytes = 0
                self.state = SessionState.TRANSFER

                print(f"[META] Receiving {self.filename} of size {self.expected_size} (version {version})")
                self.buffer = self.buffer[6 + fn_len + 8 + 32:]

            elif msg_type == FILE_CHUNK:
                if len(self.buffer) < 11:
                    break  # Not enough for chunk header
                offset = struct.unpack('!Q', self.buffer[1:9])[0]
                length = struct.unpack('!H', self.buffer[9:11])[0]

                if len(self.buffer) < 11 + length:
                    break  # Not enough for full chunk data

                chunk_data = self.buffer[11:11 + length]
                self.file.seek(offset)
                self.file.write(chunk_data)
                self.received_bytes += len(chunk_data)

                print(f"[CHUNK] {len(chunk_data)} bytes at offset {offset}")

                if self.received_bytes >= self.expected_size:
                    self.file.close()
                    self.state = SessionState.DONE
                    print("[DONE] File received successfully.")

                    actual_hash = self.compute_sha256(f"received_{self.filename}")
                    if actual_hash == self.expected_hash:
                        print("SHA-256 hash verified.")
                    else:
                        print("SHA-256 hash mismatch!")

                responses.append(struct.pack('!B Q', FILE_ACK, self.received_bytes))
                self.buffer = self.buffer[11 + length:]

            else:
                print("[ERROR] Unknown message type")
                break

        return responses

async def handle_client(reader, writer):
    handler = FTPQServer()
    while not reader.at_eof():
        data = await reader.read(4096)
        if not data:
            break
        handler.buffer += data
        responses = handler.process_buffer()
        for response in responses:
            writer.write(response)
            await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 8888)
    addr = server.sockets[0].getsockname()
    print(f"FTP-Q TCP Server running on {addr}")
    async with server:
        await server.serve_forever()

asyncio.run(main())
