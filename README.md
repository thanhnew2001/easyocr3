**Installation**

It is recommended to use virtual environment to ensure no problem with package version:

python3 -m venv venv
source venv/bin/activate

_Steps: _

1. Clone repo: git clone https://github.com/thanhnew2001/easyocr3

2. Install: pip install -r requirements.txt
3. Run: python3 app.py
4. Test:

curl -X POST -F "file=@chen.jpg" -F "source_lang=zh" -F "target_lang=en"  http://localhost:5000/upload --output result16.jpg

**Source file:**

![chen](https://github.com/thanhnew2001/easyocr3/assets/3261272/38c65902-7318-49c5-9574-c0a25622ea6a)


**Results:**

![result16](https://github.com/thanhnew2001/easyocr3/assets/3261272/7d2c58e8-ef6e-41fb-82c7-d2d2d1cde944)



**List of language code:**
['english', 'chinese', 'vietnamese', 'spanish', 'italian', 'french', 'german', 'thai', 'korean']
default: english
