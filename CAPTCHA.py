import tensorflow as tf
import os
from PIL import Image
import random
import numpy as np
from tensorflow import keras
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import h5py

# CHAlen = 4      # 验证码字母的个数
CHArange = 10 + 26      # 一个字母的范围，这里是0-9，a-z。
alpha1 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# alpha2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
#           'W', 'X', 'Y', 'Z']
alpha3 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
          'w', 'x', 'y', 'z']
alphabet = alpha1 + alpha3
num_classes = CHArange

img_rows = 70
img_cols = 37

input_shape = (img_rows, img_cols, 1)
batch_size = 128
epochs = 20

crop_images_path = 'crop_images'


def text2vec(ch):
    '''
    将文本标签转换为训练可用的向量标签
    :param text: 文本标签，验证码的文本
    :return:
        label_vec: 向量标签
    '''
    # 将0-9，A-Z，a-z依次映射到0-61
    if ord(ch) not in range(97, 123) and ord(ch) not in range(48, 58):
        raise ValueError(ch + " is not define.")
    asc = ord(ch) - 48
    if asc > 9:
        asc = ord(ch) - 87
    return asc


def vec2text(vec):
    '''
    将标签向量转换为文本标签
    :param vec: 标签向量
    :return:
    '''
    maxIndex = np.argmax(vec)
    return alphabet[maxIndex]


def get_train_set(rate=0.1):
    '''
    划分训练集和测试集
    :param rate: 划分数据集的比例，为测试集/训练集
    :return:
    '''
    # 读取图片
    images_name = os.listdir(crop_images_path)
    images = []
    raw_labels = []
    for item in images_name:
        direct = os.listdir(os.path.join(crop_images_path, item))
        for con in direct:
            images.append(np.array(Image.open(os.path.join(crop_images_path, item, con)).convert('L')))
            raw_labels.append(item)
    # 打乱图片
    randnum = random.randint(0, 100)
    random.seed(randnum)
    random.shuffle(images)
    random.seed(randnum)
    random.shuffle(raw_labels)

    # Image.fromarray(images[16]).show(title=raw_labels[10])
    # print(raw_labels[16])

    # 数据集总数
    images_len = len(images)
    # 测试集个数
    test_len = int(rate * images_len / (1 + rate))
    test_img = images[:test_len]
    train_img = images[test_len:]

    train_img = np.array(train_img)
    test_img = np.array(test_img)
    test_img = test_img.reshape(test_img.shape[0], img_rows, img_cols, 1)
    train_img = train_img.reshape(train_img.shape[0], img_rows, img_cols, 1)
    print(train_img.shape, test_img.shape)

    # 标签向量化
    labels = []
    for text in raw_labels:
        labels.append(text2vec(text))
    train_labels = np.array(labels[test_len:])
    test_labels = np.array(labels[:test_len])

    return train_img, train_labels, test_img, test_labels


def train_cnn():
    x_train, y_train, x_test, y_test = get_train_set()
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    print('x_train shape:', x_train.shape)
    print('x_test shape:', y_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    model = keras.models.Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])

    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=1,
              validation_data=(x_test, y_test))
    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    model.save("model.h5")


def retrain(old_model_name, new_model_name):
    x_train, y_train, x_test, y_test = get_train_set()
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    print('x_train shape:', x_train.shape)
    print('x_test shape:', y_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    model = keras.models.load_model(old_model_name)
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=1,
              validation_data=(x_test, y_test))
    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    # model.save(new_model_name)


if __name__ == '__main__':
    # train_cnn()
    retrain('model.h5', 'model.h5')

