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
arr2=[76,233]
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
        hexstr = hex(crc)
        x, y = int(hexstr[2:4], 16), int(hexstr[4:6], 16)
        arr = [x, y]
        #arr = [hexstr[2:4],hexstr[4:6]]
        return arr

    """"
    arr = [crc]
    print("Must send this list to receiever", arr)
    print( )
    return arr"""""

x = crc16_generator([253, 0, 0, 4, 1, 8, 2, 17])
print(x,"")

