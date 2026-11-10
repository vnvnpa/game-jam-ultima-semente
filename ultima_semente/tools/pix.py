"""Kit de pixel art "à mão": canvas RGBA em numpy, sem suavização.
Tudo é desenhado pixel a pixel (linhas Bresenham, círculos de ponto médio,
dithering de Bayer, rampas de cor com mudança de matiz). Nada de supersampling."""
import numpy as np
from PIL import Image

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0 + 1 / 32.0
BAYER2 = np.array([[0, 2], [3, 1]], dtype=np.float32) / 4.0 + 1 / 8.0


def hx(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


class C:
    def __init__(self, w, h=None):
        h = h or w
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    # ------------------------------------------------ primitivas
    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def px(self, x, y, c):
        x, y = int(x), int(y)
        if self.inb(x, y):
            if len(c) == 3:
                c = (*c, 255)
            self.a[y, x] = c

    def get(self, x, y):
        return tuple(int(v) for v in self.a[y, x]) if self.inb(x, y) else (0, 0, 0, 0)

    def over(self, x, y, c):
        """Composição 'over' (para brilhos translúcidos)."""
        if not self.inb(x, y):
            return
        if len(c) == 3:
            c = (*c, 255)
        sa = c[3] / 255.0
        d = self.a[y, x].astype(np.float32)
        da = d[3] / 255.0
        oa = sa + da * (1 - sa)
        if oa <= 0:
            return
        rgb = (np.array(c[:3], np.float32) * sa + d[:3] * da * (1 - sa)) / oa
        self.a[y, x] = (*[int(round(v)) for v in rgb], int(round(oa * 255)))

    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w):
                self.px(x + i, y + j, c)

    def frame(self, x, y, w, h, c):
        for i in range(w):
            self.px(x + i, y, c)
            self.px(x + i, y + h - 1, c)
        for j in range(h):
            self.px(x, y + j, c)
            self.px(x + w - 1, y + j, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.25:
                    self.px(x, y, c)

    def ring(self, cx, cy, r, c, t=1.0):
        for y in range(int(cy - r - 2), int(cy + r + 3)):
            for x in range(int(cx - r - 2), int(cx + r + 3)):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - t / 2 <= d <= r + t / 2:
                    self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x - cx) / max(rx, .01)) ** 2 + ((y - cy) / max(ry, .01)) ** 2 <= 1.0:
                    self.px(x, y, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= y + .5 < y1) or (y1 <= y + .5 < y0):
                    xs.append(x0 + (y + .5 - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(round(xs[i])), int(round(xs[i + 1]))):
                    self.px(x, y, c)

    def art(self, x, y, rows, pal):
        """Desenha arte ASCII: cada caractere é uma chave em `pal` ('.' = vazio)."""
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != "." and ch != " " and ch in pal:
                    self.px(x + i, y + j, pal[ch])

    def paste(self, other, x, y):
        for j in range(other.h):
            for i in range(other.w):
                p = other.a[j, i]
                if p[3]:
                    self.over(x + i, y + j, tuple(int(v) for v in p))

    # ------------------------------------------------ efeitos
    def mask(self):
        return self.a[:, :, 3] > 0

    def outline(self, c, only_empty=True, diag=False):
        m = self.mask()
        out = np.zeros_like(m)
        out[1:, :] |= m[:-1, :]
        out[:-1, :] |= m[1:, :]
        out[:, 1:] |= m[:, :-1]
        out[:, :-1] |= m[:, 1:]
        if diag:
            out[1:, 1:] |= m[:-1, :-1]
            out[:-1, :-1] |= m[1:, 1:]
            out[1:, :-1] |= m[:-1, 1:]
            out[:-1, 1:] |= m[1:, :-1]
        out &= ~m
        for y, x in zip(*np.nonzero(out)):
            self.px(x, y, c)

    def sel_outline(self, fn):
        """Contorno seletivo: cada pixel de borda ganha a cor fn(cor_do_vizinho)."""
        m = self.mask()
        res = []
        for y, x in zip(*np.nonzero(~m)):
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if self.inb(nx, ny) and m[ny, nx]:
                    best = tuple(int(v) for v in self.a[ny, nx])
                    break
            if best:
                res.append((x, y, fn(best)))
        for x, y, c in res:
            self.px(x, y, c)

    def dither_fill(self, x, y, w, h, c1, c2, fn, bayer=BAYER4):
        """Preenche retângulo misturando c1/c2: fn(x,y)->0..1 (prob. de c2)."""
        n = bayer.shape[0]
        for j in range(h):
            for i in range(w):
                t = fn(i, j)
                self.px(x + i, y + j, c2 if t > bayer[(y + j) % n, (x + i) % n] else c1)

    def save(self, path, scale=1):
        im = Image.fromarray(self.a, "RGBA")
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        im.save(path)

    def img(self):
        return Image.fromarray(self.a, "RGBA")


def sheet(frames, cols=None):
    cols = cols or len(frames)
    fw, fh = frames[0].w, frames[0].h
    rows = (len(frames) + cols - 1) // cols
    s = C(fw * cols, fh * rows)
    for k, f in enumerate(frames):
        s.paste(f, (k % cols) * fw, (k // cols) * fh)
    return s


def mix(c1, c2, t):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3)) + (255,)


def darker(c, k=0.55, hue=(20, 10, 40)):
    """Escurece deslocando para frio/violeta (sombra com matiz, não só preto)."""
    return tuple(max(0, min(255, int(c[i] * k + hue[i] * (1 - k)))) for i in range(3)) + (c[3] if len(c) > 3 else 255,)


def contact(paths_or_imgs, scale, cols, out, bg=(30, 36, 40, 255), pad=8):
    ims = []
    for p in paths_or_imgs:
        ims.append(p.convert("RGBA") if isinstance(p, Image.Image) else Image.open(p).convert("RGBA"))
    cw = max(i.width for i in ims) * scale + pad
    ch = max(i.height for i in ims) * scale + pad
    rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGBA", (cw * cols, ch * rows), bg)
    for k, im in enumerate(ims):
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        S.alpha_composite(im, ((k % cols) * cw + pad // 2, (k // cols) * ch + pad // 2))
    S.save(out)
