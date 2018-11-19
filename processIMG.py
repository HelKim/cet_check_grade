import os
from PIL import Image


def process(img):
    # 图像二值化方法
    def binarization(threshold=135):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return table
    # 先灰度化再二值化
    return img.convert('L').point(binarization(), '1')


def crop_img(img):
    # 把验证码切割成单个字符
    start = 18
    width = 37
    top = 25
    height = 95

    imgs = []
    # 切割成4个字符
    for i in range(4):
        new_start = start + width * i
        box = (new_start, top, new_start + width, height)
        piece = img.crop(box)
        imgs.append(piece)
    return imgs


def save_crop_imgs(imgs, img_name, sava_path):
    # 保存切割出来的图片保存起来
    for n, word in enumerate(img_name[:4]):
        if not os.path.exists(sava_path):
            os.mkdir(sava_path)
        file_dir = os.path.join(sava_path, word)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)

        imgs_len = len(os.listdir(file_dir))
        imgs[n].save(os.path.join(sava_path, word, word + str(imgs_len) + ".png"))


if __name__ == '__main__':
    save_path = "crop_images"
    name_list = os.listdir("raw_correct")
    for name in name_list:
        if not name.endswith(".png"):
            continue
        img = Image.open(os.path.join("raw_correct", name))
        img = process(img)
        piece_img_list = crop_img(img.copy())
        save_crop_imgs(piece_img_list, name, save_path)
    print('finish')
