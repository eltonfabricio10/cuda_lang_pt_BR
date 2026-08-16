# -*- coding: utf-8 -*-

EN = "~!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?"
RU = "ё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"
 
def qwerty_en_ru(s):
    t = s.maketrans(EN, RU)
    return s.translate(t)

def qwerty_ru_en(s):
    t = s.maketrans(RU, EN)
    return s.translate(t)

#print('1', qwerty_en_ru('qwerty'))
#print('2', qwerty_ru_en('йцукен'))
