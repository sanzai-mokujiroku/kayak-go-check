#!/usr/bin/env python3
"""富山湾 出艇判断チェック用のアプリアイコンを生成（外部ライブラリ不要）。"""
import zlib, struct, math

S = 512

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def make_pixels():
    top    = (0x16, 0x5a, 0x8a)   # 明るい海色
    bottom = (0x07, 0x2c, 0x47)   # 深い海色
    wave1  = (0xff, 0xff, 0xff)   # 白波
    wave2  = (0xbf, 0xe3, 0xf7)   # 淡い波
    hull   = (0xff, 0xd1, 0x66)   # カヤック（黄）
    paddle = (0xe8, 0xf4, 0xff)

    px = bytearray()
    for y in range(S):
        row = bytearray()
        row.append(0)  # PNG filter type 0
        for x in range(S):
            t = y / S
            r, g, b = lerp(top, bottom, t)
            a = 255

            # 波のバンド（sine）
            yc = y
            w_a = 26*math.sin(x/55.0) + 320
            w_b = 22*math.sin(x/48.0 + 1.7) + 360
            if abs(yc - w_a) < 7:
                r, g, b = wave2
            if abs(yc - w_b) < 6:
                r, g, b = lerp((r,g,b), wave1, 0.85)

            # カヤック船体（横長の楕円）
            cx, cy = S*0.5, S*0.46
            ex, ey = 150, 34
            if ((x-cx)/ex)**2 + ((y-cy)/ey)**2 <= 1:
                r, g, b = hull
            # コックピット（中央の暗い楕円）
            if ((x-cx)/55)**2 + ((y-(cy-4))/18)**2 <= 1:
                r, g, b = (0x07, 0x2c, 0x47)
            # パドルの軸（斜めの線）
            d = abs((y - cy) - 0.9*(x - cx))
            if d < 7 and abs(x-cx) < 175 and y < cy+10:
                r, g, b = paddle

            row += bytes((r, g, b, a))
        px += row
    return bytes(px)

def write_png(path, raw):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", S, S, 8, 6, 0, 0, 0)  # RGBA
    idat = zlib.compress(raw, 9)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

if __name__ == "__main__":
    write_png("icon-512.png", make_pixels())
    print("icon-512.png done")
