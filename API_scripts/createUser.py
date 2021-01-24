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
            
    dst = Image.new('RGBA', (400, 600), 'white')
    draw = ImageDraw.Draw(dst)
    fontName = ImageFont.truetype('./fonts/mono.ttf', 36)
    fontSub = ImageFont.truetype('./fonts/arial.ttf', 28)
    fontTitle = ImageFont.truetype('./fonts/arial.ttf', 36)
    
    qr = qrcode.QRCode()
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.resize((400, 400))
    dst.paste(img, (0, 30))
    draw.text((70,30),'AMS  CLIA  LAB',(0,0,0),fontTitle)
    draw.text((160,390),'NAME',(0,0,0),fontSub)
    draw.text((padx(name),430),name.upper(),(0,0,0),fontName)
    draw.text((160,480),'ROLE',(0,0,0),fontSub)
    draw.text((padx(','.join(role)),520),','.join(role).upper(),(0,0,0),fontName)
    dst.save(f'{name} badge.png')
    
    
    
    
res = createUser('Jim Jang',['testing'])

res = createUser('Logan Roberts',['reception'])
