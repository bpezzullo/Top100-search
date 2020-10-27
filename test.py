import csv
import os

# r = requests.get('https://api.github.com/events')
# events = r.json()
# print(events[0])
# r = {'data': ['key=xwy','age=20','key=abc','age=50']}
# x = r['data']

# count = 0
# for i in range(0,len(x),2):
#     print(x[i])
#     z = x[i+1].split('=')
#     if z[0] == 'age':
#         if int(z[1]) >= 50:
#             count += 1

# print(count)

# z = dict(x)
# print(z)

#function that filters vowels
def filterLetters(letter):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',',']
    return (letter in letters)

hot100 = os.path.join("data", "HotStuff.csv")
with open(hot100, mode='r') as file:
    headers = file.readline()
    headers = headers.lower()
    hdrFiltered = ''
    for letter in headers:
        if filterLetters(letter):
            hdrFiltered += letter
    

    hdr_list = str(hdrFiltered).split(',')
    print(hdr_list)

    # reading the CSV file
    csvFile = csv.reader(file)

    # skip the initial 4 lines of data

    lenHeader = len(headers)

    counter = 0
    for lines in csvFile:
        # print(lines)
        # newSong = Songs(lines)
        # print(f'print class {newSong.songName}')
        counter += 1
        test = zip(hdr_list,lines)
        print(dict(test))
        if counter > 1:
            print("I am done")
            break
