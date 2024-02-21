**Installation**

It is recommended to use virtual environment to ensure no problem with package version:

python3 -m venv venv
source venv/bin/activate

_Steps: _

1. Clone repo: git clone https://github.com/thanhnew2001/easyocr3

2. Install: pip install -r requirements.txt
3. Run: python3 app.py
4. Test:

curl -X POST -F "files=@demo_image/demo_1.png" -F "files=@demo_image/demo_2.png" http://localhost:5000/upload 

**Results:**
{
  "results": [
    {
      "filename": "demo_1.png",
      "recognized_labels": [
        "available"
      ]
    },
    {
      "filename": "demo_2.png",
      "recognized_labels": [
        "shakeshack"
      ]
    }
  ]
}


**List of language code:**
['english', 'chinese', 'vietnamese', 'spanish', 'italian', 'french', 'german', 'thai', 'korean']
default: english
