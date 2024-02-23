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
1. Download here: https://github.com/thanhnew2001/easyocr3/blob/master/chen.jpg

![chen](https://github.com/thanhnew2001/easyocr3/assets/3261272/38c65902-7318-49c5-9574-c0a25622ea6a)


**Results:**

![result16](https://github.com/thanhnew2001/easyocr3/assets/3261272/7d2c58e8-ef6e-41fb-82c7-d2d2d1cde944)

**New version can scale the size of text:**

![image](https://github.com/thanhnew2001/easyocr3/assets/3261272/d96920c7-2ac4-462a-9dd8-2afc60c2f755)

![result25](https://github.com/thanhnew2001/easyocr3/assets/3261272/4ff1f384-31fa-4320-be43-bfe4ba70a8be)

![image](https://github.com/thanhnew2001/easyocr3/assets/3261272/c58b45ee-aa0c-4ec2-9f71-97c3ea4cb50e)

![result26](https://github.com/thanhnew2001/easyocr3/assets/3261272/00350cd6-a32c-41f5-bb9d-adcf6274e45f)

![image](https://github.com/thanhnew2001/easyocr3/assets/3261272/49388d27-0086-4497-841e-7cd257c933a2)

![result27](https://github.com/thanhnew2001/easyocr3/assets/3261272/d84d902f-7dfd-450d-8b06-6b0048a48395)







**List of language code:**
['english', 'chinese', 'vietnamese', 'spanish', 'italian', 'french', 'german', 'thai', 'korean']
default: english
