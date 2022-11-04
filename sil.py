crc=2020

if crc > 255:
        hex_str = '{:04x}'.format(crc)
        print(hex_str)
        x, y = int(hex_str[0:2], 16), int(hex_str[2:4], 16)
        arr = [x, y]
        #arr = [hexstr[2:4],hexstr[4:6]]
        print(arr)