"""Ferramentas de pixel art por supersampling: desenha em alta resolução (formas
suaves) e reduz com NEAREST para um sprite nítido de poucos pixels, depois aplica
o contorno escuro de 1 px. Coordenadas em UNIDADES DO SPRITE FINAL (ex.: 0..32)."""
import numpy as np
from PIL import Image, ImageDraw

OUTLINE = (11, 18, 20, 255)


def tone(c, k):
    """k>0 clareia, k<0 escurece (mantém alfa)."""
    a = c[3] if len(c) > 3 else 255
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c[:3]) + (a,)
    return tuple(int(v * (1 + k)) for v in c[:3]) + (a,)


def outline_img(img, c=OUTLINE):
    a = np.array(img)
    alpha = a[..., 3] > 0
    pad = np.pad(alpha, 1)
    dil = pad[1:-1, 1:-1] | pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    a[dil & ~alpha] = c
    return Image.fromarray(a, "RGBA")


class HD:
    def __init__(self, w, h=None, S=6):
        h = h or w
        self.w, self.h, self.S = w, h, S
        self.im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _s(self, v):
        return [(x * self.S, y * self.S) for x, y in v]

    def ellipse(self, cx, cy, rx, ry, fill):
        S = self.S
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)

    def rect(self, x0, y0, x1, y1, fill, r=0.0):
        S = self.S
        if r > 0:
            self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=fill)
        else:
            self.d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill)

    def poly(self, pts, fill):
        self.d.polygon(self._s(pts), fill=fill)

    def line(self, pts, fill, width=1.0):
        self.d.line(self._s(pts), fill=fill, width=max(1, int(width * self.S)), joint="curve")

    def _paste_masked(self, draw_fn, mask_fn):
        mask = Image.new("L", self.im.size, 0)
        mask_fn(ImageDraw.Draw(mask))
        tmp = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(tmp))
        self.im.paste(tmp, (0, 0), mask)

    def shaded_ellipse(self, cx, cy, rx, ry, base, hi=True):
        S = self.S
        box = [(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S]

        def dr(d):
            d.ellipse(box, fill=tone(base, -0.38))
            d.ellipse([(cx - rx * .94) * S, (cy - ry * .94) * S, (cx + rx * .78) * S, (cy + ry * .8) * S], fill=base)
            if hi:
                d.ellipse([(cx - rx * .62) * S, (cy - ry * .74) * S, (cx - rx * .02) * S, (cy - ry * .14) * S], fill=tone(base, .4))
        self._paste_masked(dr, lambda m: m.ellipse(box, fill=255))

    def shaded_rect(self, x0, y0, x1, y1, base, r=1.0, side=0.28):
        """Retângulo arredondado com lado direito e base mais escuros e topo/esquerda claros."""
        S = self.S
        box = [x0 * S, y0 * S, x1 * S, y1 * S]
        w = x1 - x0

        def dr(d):
            d.rectangle(box, fill=base)
            d.rectangle([(x1 - w * side) * S, y0 * S, x1 * S, y1 * S], fill=tone(base, -0.28))
            d.rectangle([x0 * S, (y1 - (y1 - y0) * .16) * S, x1 * S, y1 * S], fill=tone(base, -0.38))
            d.rectangle([x0 * S, y0 * S, (x0 + w * .22) * S, y1 * S], fill=tone(base, .22))
        self._paste_masked(dr, lambda m: m.rounded_rectangle(box, radius=r * S, fill=255))

    def img(self, outline=True):
        small = self.im.resize((self.w, self.h), Image.NEAREST)
        return outline_img(small) if outline else small


def tint_white(img, k):
    a = np.array(img).astype(float)
    m = a[..., 3] > 0
    for i in range(3):
        a[..., i][m] = a[..., i][m] * (1 - k) + 255 * k
    return Image.fromarray(a.astype("uint8"), "RGBA")


def with_alpha(img, k):
    a = np.array(img)
    a[..., 3] = (a[..., 3] * k).astype("uint8")
    return Image.fromarray(a, "RGBA")
