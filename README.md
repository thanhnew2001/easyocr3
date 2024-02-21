**Installation**

It is recommended to use virtual environment to ensure no problem with package version:

python3 -m venv venv
source venv/bin/activate
_Steps: _

1. Clone repo: git clone https://github.com/thanhnew2001/easyocr3

2. Install: pip install -r requirements.txt
3. Run: python3 app.py
4. Test: curl -X POST -F "file=@demo_1.jpg" -F "language=english" http://localhost:5000/upload

**List of language code:**
['english', 'chinese', 'vietnamese', 'spanish', 'italian', 'french', 'german', 'thai', 'korean']
default: english
