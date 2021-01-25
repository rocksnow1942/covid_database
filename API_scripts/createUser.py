from connection import makeServer
import qrcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


server = makeServer('prod')


def padx(text,width=400,cw = 22.1):
    tl = len(text) * cw
    return (width - tl) / 2
    
def createUser(name,role=['reception','testing']):
    res = server.post('/user',json=dict(username=name,role=role))    
    token = res.json()['token']
    printUser(name,role,token)
            

def printUser(name,role,token):
    dst = Image.new('RGBA', (400, 500), 'white')
    draw = ImageDraw.Draw(dst)
    fontName = ImageFont.truetype('./fonts/mono.ttf', 36)
    fontSub = ImageFont.truetype('./fonts/arial.ttf', 28)
    fontTitle = ImageFont.truetype('./fonts/arial.ttf', 36)
    
    qr = qrcode.QRCode()
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.resize((250, 250))
    dst.paste(img, (75, 50))
    draw.text((65,30),'AMS  CLIA  LAB',(0,0,0),fontTitle)
    draw.text((160,290),'NAME',(0,0,0),fontSub)
    draw.text((padx(name),330),name.upper(),(0,0,0),fontName)
    draw.text((160,380),'ROLE',(0,0,0),fontSub)
    draw.text((padx(','.join(role)),420),','.join(role).upper(),(0,0,0),fontName)     
    dst.save(f'{name} badge.png')
    

    
res = createUser('Jones Huang',['testing'])

res = createUser('Logan Roberts',['reception'])


res = printUser('Logan Roberts',['reception'],'9DTZCSXtg5')