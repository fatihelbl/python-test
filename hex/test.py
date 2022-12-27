device= 0
i = device
loop=10
for i in range(loop):
    print(i)
    if(device==3):
        loop= loop + 1
        device = device-1
    elif( i == 5):
        device= device +1
        
    device= device + 1  
    print(device,"dd")  
    