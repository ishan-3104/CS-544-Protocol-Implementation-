
import asyncio
import os
import hashlib
from client.protocol import pack_file_meta, pack_file_chunk, unpack_file_ack
from client.state import SessionState

CHUNK_SIZE = 1024

def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

async def main():
    reader, writer = await asyncio.open_connection('localhost', 8888)
    file_path = "client/test.txt"
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    file_hash = compute_sha256(file_path)

    print("Connected to server")

    # INIT: Send file metadata
    meta_msg = pack_file_meta(filename, file_size, file_hash)
    writer.write(meta_msg)
    await writer.drain()
    print("Sent FileMeta with SHA-256:", file_hash)

    # TRANSFER: Send file chunks
    state = SessionState.TRANSFER
    offset = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            chunk_msg = pack_file_chunk(offset, chunk)
            writer.write(chunk_msg)
            await writer.drain()
            print(f"Sent chunk at offset {offset}")
            offset += len(chunk)

    # DONE: Await ACK
    ack_data = await reader.read(9)
    if ack_data:
        msg_type, ack_offset = unpack_file_ack(ack_data)
        print(f" Server acknowledged {ack_offset} bytes")
        if ack_offset == file_size:
            print("File upload complete.")

    writer.close()
    await writer.wait_closed()

asyncio.run(main())
