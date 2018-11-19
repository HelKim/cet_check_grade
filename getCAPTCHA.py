from tensorflow import keras
import processIMG
import CAPTCHA
import numpy as np
from PIL import Image


model = keras.models.load_model('model.h5')


def getCode(img):
    img = processIMG.process(img)
    img_list = processIMG.crop_img(img)
    result = ""
    for img in img_list:
        im = np.array(img).reshape(1, CAPTCHA.img_rows, CAPTCHA.img_cols, 1)
        result_vec = model.predict(im)
        result += CAPTCHA.vec2text(result_vec[0])
    return result


if __name__ == '__main__':
    print(getCode(Image.open('./raw_correct/2a5g.png')))
