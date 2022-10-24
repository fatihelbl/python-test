def crc16(data: bytes):
 crc = 0xffff
 for cur_byte in data:
   crc = crc ^ cur_byte
   for _ in range(8):
      a = crc
      carry_flag = a & 0x0001
      crc = crc >> 1
      if carry_flag == 1:
         crc = crc ^ 0xa001
   return bytes([crc % 256, crc >> 8 % 256])


def crc (buffer,lenght):
    crc= 0xffff
    for i in range(lenght):
        crc = crc ^ i
        for j in range(8):
            if((crc & 0x0001) == 1):
                crc = crc >> 1
                crc = crc ^ 0xA001
            else:
                crc= crc >>1
    return crc

data = b"\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x00"
crc = crc16(data)

crc_str = " ".join("{:02x}".format(x) for x in crc)
print(crc_str)
#crc=crc(data,6)

print(crc)