# from flask import Flask
#
#
# class RandomChar():
#   """用于随机生成汉字对应的Unicode字符"""
#   @staticmethod
#   def Unicode():
#     val = random.randint(0x4E00, 0x9FBB)
#     return unichr(val)
#
#   @staticmethod
#   def GB2312():
#     head = random.randint(0xB0, 0xCF)
#     body = random.randint(0xA, 0xF)
#     tail = random.randint(0, 0xF)
#     val = ( head << 8 ) | (body << 4) | tail
#     str = "%x" % val
#     #
#     return str.decode('hex').decode('gb2312','ignore')
#
# class ImageChar():
#   def __init__(self, fontColor = (0, 0, 0),
#                      size = (100, 40),
#                      fontPath = 'STZHONGS.TTF',
#                      bgColor = (255, 255, 255, 255),
#                      fontSize = 20):
#     self.size = size
#     self.fontPath = fontPath
#     self.bgColor = bgColor
#     self.fontSize = fontSize
#     self.fontColor = fontColor
#     self.font = ImageFont.truetype(self.fontPath, self.fontSize)
#     self.image = Image.new('RGBA', size, bgColor)
#
#   def rotate(self):
#     img1 = self.image.rotate(random.randint(-5, 5), expand=0)#默认为0，表示剪裁掉伸到画板外面的部分
#     img = Image.new('RGBA',img1.size,(255,)*4)
#     self.image = Image.composite(img1,img,img1)
#
#   def drawText(self, pos, txt, fill):
#     draw = ImageDraw.Draw(self.image)
#     draw.text(pos, txt, font=self.font, fill=fill)
#     del draw
#
#   def randRGB(self):
#     return (random.randint(0, 255),
#            random.randint(0, 255),
#            random.randint(0, 255))
#
#   def randPoint(self):
#     (width, height) = self.size
#     return (random.randint(0, width), random.randint(0, height))
#
#   def randLine(self, num):
#     draw = ImageDraw.Draw(self.image)
#     for i in range(0, num):
#       draw.line([self.randPoint(), self.randPoint()], self.randRGB())
#     del draw
#
#   def randChinese(self, num):
#     gap = 0
#     start = 0
#     strRes = ''
#     for i in range(0, num):
#       char = RandomChar().GB2312()
#       strRes += char
#       x = start + self.fontSize * i + random.randint(0, gap) + gap * i
#       self.drawText((x, random.randint(-5, 5)), char, (0,0,0))
#       self.rotate()
#     print strRes
#     self.randLine(8)
#     return strRes,self.image

# import captcha
# import os
# import sys
#
# print(help(captcha))

# import ast
#
#
# def top_level_functions(body):
#     #判断是不是方法
#     return (f for f in body if isinstance(f, ast.FunctionDef))
#
# # 分析文件
# def parse_ast(filename):
#     with open(filename, "rt") as file:
#         return ast.parse(file.read(), filename=filename)
#
# if __name__ == "__main__":
# # 获得当前文件，files中可以添加其他的文件
#     files = [__file__]
#     for filename in files:
#         print(filename)
#         tree = parse_ast(filename)
#         for func in top_level_functions(tree.body):
#             print("  %s" % func.name)

# print(dir())

# from captcha.image import ImageCaptcha

# dir()方法能查看当前对象能使用的所有函数和方法
print(dir())

for i in range(10):
    print(i)

r = range(10)
print(type(r))
x = list(range(10))
print(type(x))

print(r)
print(x)


class TestDir(object):
    def __init__(self):
        self.name = 'ltwin'
        self.age = 21

    def __str__(self):
        return self.name

    def description(self):
        print('我的名字是：%s，年龄是：%s' % (self.name, self.age))

print(dir(TestDir))
