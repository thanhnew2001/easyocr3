# How to install and run?

## Installation
It is recommended to use virtual environment to ensure no problem with package version:

python3 -m venv venv
source venv/bin/activate

## Steps

1. Clone repo: git clone https://github.com/thanhnew2001/easyocr3

2. Install: pip install -r requirements.txt
3. Run: python3 app.py

## Run: Open another Terminal window
### Image --> images + translated text

curl -X POST -F "file=@demo_image/chen.jpg" -F "source_lang=zh" -F "target_lang=en"  http://localhost:5000/upload --output result.jpg

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

### List of boundary images --> image file names + recognized text + translated text

```
curl -X POST -F "file=@demo_image/demo_1.png" -F "file=@demo_image/demo_2.png" -F "source_lang=en" -F "target_lang=vi"  http://localhost:5000/upload_textonly

```

### Translation only: support both GET and POST
```
curl -X POST -F "file=@demo_image/demo_1.png" -F "source_lang=en" -F "target_lang=vi"  http://localhost:5000/upload_textonly
```

```
curl -X POST -H "Content-Type: application/json" \
-d '{"text": "Hello", "source_lang": "en", "target_lang": "es"}' \
"http://localhost:5000/translate"
```
