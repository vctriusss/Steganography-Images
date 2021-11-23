from PIL import Image
import numpy as np


def refactor_message(text, lsb):
    arr = ['' for _ in range((len(text) - 1) // lsb + 1)]
    for i, symb in enumerate(text):
        arr[i // lsb] += symb
    arr = list(map(lambda x: int(x, 2), arr))
    arr = np.array(arr)
    return arr


def text_to_bin(text):
    msg = ''
    for c in text:
        b = bin(ord(c))[2:]
        if ord(c) > 2047:
            continue
        b = '0' * (11 - len(b)) + b
        msg += b
    return msg


def bin_to_text(msg):
    msg = str(msg)
    text = ''
    for i in range(len(msg) // 11):
        part = msg[11 * i: 11 * (i + 1)]
        text += chr(int(part, 2))
    return text


def main():
    print('Добро пожаловать в программму-реализацию LSB-метода в стеганографии')
    task = input('Что вы хотите сделать:\n'
                 '1) Встроить сообщение\n'
                 '2) Извлечь сообщение\n'
                 '3) Выход\n')
    if task == 3:
        return 0
    name0 = input('Введите имя изначального изображения в формате "name.format"\n')
    global name
    img = Image.open(name0)
    name = name0[:name0.index('.')]
    if img.format != 'BMP':
        img.save(f'{name}.bmp')
        img.close()
        img = Image.open(f'{name}.bmp')
    if task == '1':
        encrypt(img)
    else:
        decrypt(img)


def encrypt(img):
    width, height = img.size
    msg_type = input('\nСообщение - это:\n'
                     '1) Текст\n'
                     '2) Битовая последовательность\n')
    print('Введите информацию для встраивания в файл input.txt')
    lsb = int(input('Введите количество LSB, которые можно изменять (от 1 до 7):\n'))
    with open('input.txt', 'r', encoding='utf-8') as f:
        msg_normal = f.read()
    msg = msg_normal if msg_type == '2' else text_to_bin(msg_normal)
    bin_len = bin(len(msg))[2:]
    msg = '0' * (24 - len(bin_len)) + bin_len + msg
    size = len(msg)
    bin_lsb = bin(lsb)[2:]
    bin_lsb = '0' * (3 - len(bin_lsb)) + bin_lsb
    msg = refactor_message(msg, lsb)
    pixels = np.asarray(img)
    shape = np.shape(pixels)
    pixels = pixels.flatten()
    for i, color in enumerate(pixels[:3]):
        pixels[i] = color - color % 2 + int(bin_lsb[i])
    pixels[3] = int(str(pixels[3])[:-1] + msg_type)
    msgpixels = pixels[4: (size - 1) // lsb + 5]
    msgpixels = np.array(list(map(lambda x: x - (x % (2 ** lsb)), msgpixels)))
    msgpixels = np.add(msg, msgpixels)
    pixels[4:(size - 1) // lsb + 5] = msgpixels
    pixels = pixels.reshape(shape)
    img = Image.fromarray(pixels.astype(np.uint8))
    img.save(f'{name}1.bmp')
    img.close()
    print('Встраивание завершено успешно!\nПолученное изображение находится в той же папке '
          + f'под именем {name}1.bmp')
    print(f'Емкость встраивания: {3 * lsb} бит сообщения (около {round(3 * lsb / 11, 3)} символа) на 1 пиксель '
          f'изображения')
    print(f'Заполненность контейнера: {round((2 + size / (3 * lsb)) * 100 / (width * height), 4)}%')


def decrypt(img):
    pixels = np.asarray(img).flatten()
    lsb = ''
    msg = ''
    for color in pixels[:3]:
        lsb += str(color % 2)
    lsb = int(lsb, 2)
    msg_type = str(pixels[3] % 2)
    bin_len = ''
    for color in pixels[4: 23 // lsb + 5]:
        bin_len += bin(color)[-lsb:]
    if len(bin_len) > 24:
        msg += bin_len[24: len(bin_len)]
        bin_len = bin_len[:24]
    size = int(bin_len, 2)
    delta_msg = len(msg)
    for color in pixels[23 // lsb + 5: 23 // lsb + 6 + (size - delta_msg - 1) // lsb]:
        msg += bin(color)[-lsb:]
    if len(msg) > size:
        msg = msg[:size]
    msg = msg if msg_type == '0' else bin_to_text(msg)
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(msg)
    print('Извлечение прошло успешно!\nСодержимое контейнера находится в файле output.txt')
    img.close()


main()
