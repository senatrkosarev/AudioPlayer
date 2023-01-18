import io

from PIL import Image


def find_average_color(image_path: str):
    image = Image.open(image_path)
    pixels = image.load()
    x, y = image.size
    r_sum, g_sum, b_sum = 0, 0, 0
    for i in range(x):
        for j in range(y):
            r_sum += pixels[i, j][0]
            g_sum += pixels[i, j][1]
            b_sum += pixels[i, j][2]
    square = x * y
    result = [int(r_sum / square), int(g_sum / square), int(b_sum / square)]
    for i in range(3):
        if result[i] > 170 and sum(result) > 510:
            result[i] -= 50
    return result


def save_audio_image(image: str):
    img = Image.open(io.BytesIO(image))
    img = img.resize((340, 340))
    img.save('App/resources/temp.png')
