from io import BytesIO
import time
from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import decode
from pyzbar.pyzbar import decode as zbarDecode
from datetime import datetime
from .utils import indexToGridName

class Mock:
    def __getattr__(self,name):
        return lambda *_,**__:0

try:
    from picamera import PiCamera
except ImportError:
    PiCamera = Mock


class Camera(PiCamera):
    def __init__(self,config):
        super().__init__()
        self.loadSettings(config)
        self._captureStream = BytesIO()
        self.overlay = None
        self.startLiveBarcode = False

    def start(self,):
        self.startLiveBarcode = True
        self.start_preview(
            fullscreen=False, window=self._previewWindow, hflip=True, rotation=90)

    def stop(self):
        self.startLiveBarcode = False
        if self.overlay:
            self.remove_overlay(self.overlay)
            self.overlay = None
        self.stop_preview()

    def loadSettings(self,config):
        "load settings from config.ini"
        scanWindow = eval(config['cameraConfig']['scanWindow'])
        scanGrid = eval(config['cameraConfig']['scanGrid'])
        direction = eval(config['cameraConfig']['direction'])
        resW = eval(config['cameraConfig']['scanResolution']) # picture resultion, width. always maintain 4:3
        previewW = 300  # preview width
        self.resolution = (resW, resW*3//4)
        self.framerate = 24
        # preview window is rotated 90 deg and mirrorred.
        self._previewWindow = (20, 20, previewW, previewW*4//3)
        self._scanGrid = scanGrid
        self.direction = direction  # tube scan from top or bottom.

        if scanWindow:
            self._scanWindow = scanWindow
        else:
            scanRatio = 0.8
            scanX = (resW * (1-scanRatio) )// 2
            gridSize =( resW * scanRatio) // (self._scanGrid[0]-1)
            scanY = (resW*3/4 - gridSize*(self._scanGrid[1]-1))//2

            self._scanWindow = (scanX, scanY,
                                scanX + gridSize*(self._scanGrid[0]-1),
                                scanY + gridSize*(self._scanGrid[1]-1))
        self.font = ImageFont.truetype("./ScannerApp/arial.ttf", 26)
        # self.contrast = 100
        # self.brightness = 50

    def drawOverlay(self, highlights=[]):
        pad = Image.new('RGBA', (800, 480))
        padDraw = ImageDraw.Draw(pad)
        column, row = self._scanGrid
        xo, yo, pw, ph = self._previewWindow
        s1, s2, s3, s4 = self._scanWindow
        resolutionX, resolutionY = self.resolution
        # because preview is flipped and rotated,
        # the x overlay offset caused by scan window is actually y offset of scan window
        # in preview window, overlay offset caused by scan window in y direction.
        scan_offset_y = s1 * ph // resolutionX
        # in preview window, overlay offset caused by scan window in x direction.
        scan_offset_x = s2 * pw // resolutionY

        # overlay grid height in preview window, this is actually scan window width.
        gridHeight = (s3-s1) * ph / resolutionX // (column - 1)
        # overlay grid height in preview window, this is actually scan window height.
        gridWidth = (s4-s2) * pw / resolutionY // (row - 1)
        gridW_ = gridWidth*0.9//2  # half width of actually drawing box in preview window
        gridH_ = gridHeight*0.9//2  # half width of actually drawing box in preview window
        for r in range(row):
            for c in range(column):
                idx = r * column + c
                if idx in highlights:
                    outline = (255, 0, 0, 180)
                    width = 3
                else:
                    outline = (0, 255, 0, 180)
                    width = 1
                posy = c * gridHeight + yo + scan_offset_y
                posx = r * gridWidth + xo + scan_offset_x
                padDraw.rectangle([posx-gridW_, posy-gridH_, posx+gridW_, posy+gridH_],
                                  fill=(0, 0, 0, 0), outline=outline, width=width)

        # label A1 - H12
        labelY = yo + scan_offset_y - gridH_
        rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:row]
        rowIndex = rowIndex if self.direction == 'top' else rowIndex[::-1]
        for r in range(row):
            posx = r * gridWidth + xo + scan_offset_x
            label = rowIndex[r]
            padDraw.text((posx, labelY), label, anchor='md',
                         font=self.font, fill=(255, 0, 0, 255))
        labelX = xo + scan_offset_x - gridW_ - 5
        for c in range(column):
            posy = c * gridHeight + yo + scan_offset_y
            padDraw.text(
                (labelX, posy), f'{c+1}', anchor='rm', font=self.font, fill=(255, 0, 0, 255))

        if self.overlay:
            self.remove_overlay(self.overlay)
            self.overlay = None
        self.overlay = self.add_overlay(pad.tobytes(), size=pad.size, layer=3)

    def manualRun(self):
        ""
        while True:
            time.sleep(1)
            action = input("action:\n").strip()
            if action == 's':
                self.snapshot()
            elif action.isnumeric():
                self.drawOverlay(highlights=[int(action)])
            else:
                result = self.scan()
                highlights = []
                for idx, res in enumerate(result):
                    if len(res) != 10 or (not res.isnumeric()):
                        highlights.append(idx)
                self.drawOverlay(highlights)

    def yieldPanel(self, img):
        "yield each panel in a image"
        oversample = 1.4
        column, row = self._scanGrid
        s1, s2, s3, s4 = self._scanWindow
        gridWidth = (s3-s1)//(column-1)
        gridHeight = (s4-s2)//(row-1)
        cropW = gridWidth * oversample // 2
        cropH = gridHeight * oversample // 2
        for r in range(row):
            for c in range(column):
                posx = c * gridWidth + s1
                posy = r * gridHeight + s2
                yield img.crop((posx-cropW, posy-cropH, posx+cropW, posy+cropH))

    def decodePanel(self, panel):
        res = decode(panel, max_count=1, deviation=5,)
        if res:
            return res[0].data.decode()
        return ""

        # px,py = panel.size
        # for size in [100,200]:
        #     resize = panel.resize((size,int(size*py/px)))
        #     res = decode(resize,max_count=1)
        #     if res:
        #         return res[0].data.decode()
        # return ""

    def snapshot(self,):
        "capture and save a image"
        self.capture(
            f'./ScannerApp/snapshots/{datetime.now().strftime("%H:%M:%S")}.jpeg', format='jpeg')

    def scanDTMX(self):
        "perform a capture and decode"
        self._captureStream.seek(0)
        self.capture(self._captureStream, format='jpeg')
        self._captureStream.seek(0)
        img = Image.open(self._captureStream)
        for panel in self.yieldPanel(img):
            # name = indexToGridName(idx, self._scanGrid)
            # panel.save(f'./out/{name}.jpeg')
            yield self.decodePanel(panel)
            # print(f"{name}:{res}")
    
    def translatePoint(self,x,y):
        "map a point xy to preview window corrdinate"
        xo, yo, pw, ph = self._previewWindow
        resolutionX, resolutionY = self.resolution
        pY = x * ph // resolutionX + yo
        pX = y * pw // resolutionY + xo
        return pX,pY
    
    def liveScanBarcode(self,cb=print):
        "use pyzbar to scan"
        self.lastRead = None
        while True:
            time.sleep(0.2)
            self._captureStream.seek(0)
            if not self.startLiveBarcode:
                break
            self.capture(self._captureStream,format='jpeg',) #resize=(c_w,c_h)
            self._captureStream.seek(0)
            img = Image.open(self._captureStream)
            code = zbarDecode(img)
            if code and self.startLiveBarcode:    
                res = code[0].data.decode()
                if res != self.lastRead:
                    cb(res)
                self.lastRead = res                
                pad = Image.new('RGBA',(800,480))
                padDraw = ImageDraw.Draw(pad)
                xy = [self.translatePoint(i.x, i.y) for i in code[0].polygon]
                padDraw.polygon(xy, fill=(0, 0, 0, 0),
                                outline=(0, 255, 0, 205))
                for de in code[1:]:
                    xy = [self.translatePoint(i.x, i.y) for i in de.polygon]
                    padDraw.polygon(xy, fill=(0, 0, 0, 0),
                                    outline=(255, 0, 0, 205))

                if self.overlay:
                    self.remove_overlay(self.overlay)
                    self.overlay = None
                self.overlay = self.add_overlay(pad.tobytes(),size=pad.size, layer=3)
            else:
                if self.overlay:
                    self.remove_overlay(self.overlay)
                    self.overlay = None
                
    def indexToName(self, idx):
        return indexToGridName(idx, grid=self._scanGrid, direction=self.direction)

