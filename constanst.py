ACK_start_byte = 222 # 0xDE
state_start_byte = 0
state_output = 1
state_checksum =2
start_byte = 253 # 0xfd


payload = [1,8,2]
command_ıd = 0
BTL_LENGHT=5
ACK_CRC =[31,27]
RJT_CRC =[66,173]


"""
        CRC-16-CCITT Algorithm
        Parameters
        ----------
        data : list
        Returns
        -------
        list
            crc flipped if 2 bytes
            (e.g)
            crc = 0xc0c1 -> [0xc1, 0xc0]
    """
def crc16_generator(data):
    
    data = bytearray(data)
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(0, 8):
            
            bcarry = crc & 0x0001
            crc >>= 1

            if bcarry:
                crc ^= 0xa001
    #print("Generated CRC", (crc,), (hex(crc),))

    if crc > 255:
        hex_str = hex(crc)
        x, y = int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        arr = [x, y]
        #arr = [hexstr[2:4],hexstr[4:6]]
        return arr