import struct

FILE_META = 0x01
FILE_CHUNK = 0x02
FILE_ACK = 0x03

def pack_file_meta(filename, file_size, file_hash, version=1):
    filename_bytes = filename.encode('utf-8')
    hash_bytes = bytes.fromhex(file_hash)
    return struct.pack(f'!B B I {len(filename_bytes)}s Q 32s', 0x01, version, len(filename_bytes), filename_bytes, file_size, hash_bytes)

def pack_file_chunk(offset, data):
    return struct.pack(f'!B Q H {len(data)}s', FILE_CHUNK, offset, len(data), data)

def unpack_file_ack(data):
    return struct.unpack('!B Q', data)
