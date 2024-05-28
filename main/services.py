from random import randint
from PIL import Image, ImageDraw


def create_random_image(full_path):
    try:
        color = (randint(0, 255),
                 randint(0, 255),
                 randint(0, 255))
        img = Image.new('RGB', (250, 215), color=color)
        draw = ImageDraw.Draw(img)

        for _ in range(10):
            start = (randint(0, img.width), randint(0, img.height))
            end = (randint(0, img.width), randint(0, img.height))
            draw.line((start, end), fill='white')

        for _ in range(10):
            x1 = randint(0, img.width)
            y1 = randint(0, img.height)
            x2 = randint(x1, img.width)
            y2 = randint(y1, img.height)
            draw.ellipse(((x1, y1), (x2, y2)), outline='white')

        img.save(full_path)

    except Exception as e:
        print(e)
