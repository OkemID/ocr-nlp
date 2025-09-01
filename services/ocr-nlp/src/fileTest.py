# To test file before connecting to node api

import easyocr

reader = easyocr.Reader(["en"], gpu=False)
result = reader.readtext ("test.png")

print(result)