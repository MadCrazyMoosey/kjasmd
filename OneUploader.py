from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from PIL import Image
from rblxopencloud import exceptions
import random, io, threading
from time import sleep as sleepy

OUT:bool = True # Save decals/imgs to out.csv
STATIC:bool = False # Static method
WEBHOOK:str = ''

class DaThreads:
    def run(thread_num,creator,barrier,buffer) -> None:

        barrier.wait()

        while True: # keep uploading till one works :)
            try:
                asset = creator.upload(buffer, "RT", 'DecalUploaderV2')
                break
            except exceptions.RateLimited:
                sleepy(2)
                print('rate limit')

        if asset:
            img_id = Functions.get_image_id(asset.id)
            print(asset.id, img_id)
            if OUT:
                with open('Out.csv','a') as f:
                    f.write(f'#{thread_num},{asset.id},{img_id}\n')
            Checker(asset.id, img_id, WEBHOOK)

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    file = input('Image: ').replace('"', '')
    img = Image.open(file)
    img.thumbnail((400,400))

    if OUT:
        clear = input('Clear Out.csv? (Y/N): ')
        if 'y' in clear.lower():
            with open('Out.csv','w') as clr:
                clr.write('FileName,DecalId,ImageId\n') # CSV headers
                # filename will just be the instance for this for obv reasons

    CREATOR = DecalClass(ROBLOSECURITY)
    threads2make = range(60)
    barrier = threading.Barrier(len(threads2make)+1)
    threads = []
    print('creating images/threads')
    for a in threads2make:
        #region making img hashes
        rgba = img.convert("RGBA")
        data = rgba.getdata()

        newData = []

        for item in data:
            newData.append(item)

        if not STATIC:
            # Picks random pixel to replace
            ran = random.randint(0, len(newData))
            # Sets the color
            newData[ran]=(
                random.randint(0,item[0]),
                random.randint(0,item[1]),
                random.randint(0,item[2]), item[3])
            rgba.putdata(newData)
        else:
            intensity=20
            newData=[
                (item[0]+random.randint(-intensity, intensity),
                item[1]+random.randint(-intensity, intensity),
                item[2]+random.randint(-intensity, intensity),
                item[3])for item in data
            ]
            rgba.putdata(newData)

        buffer = io.BytesIO()
        rgba.save(buffer, format="PNG")
        buffer.seek(0)
        buffer.name = "File.png"
        rgba.close()
        #endregion

        thread = threading.Thread(target=DaThreads.run, args=(a,CREATOR,barrier,buffer,))
        thread.start()
        threads.append(thread)
        
    barrier.wait()
    print('uploading')

    for thread in threads:
        thread.join()
    print('upload finished')
    
    try:
        CREATOR.delete_key()
        print('API key has now ben deleted')
    except:
        print('erm i think you were banned, kinda awkward')
