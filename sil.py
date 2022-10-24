import workk
array = [1,2,3]
arr = [4,5]
array = array + arr
#print(array)
test= workk.payload
match test:

    case workk.payload:
        print("oldu")
        array = array + workk.payload
        print(array)
      