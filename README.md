Installation

It is recommended to use virtual environment to ensure no problem with package version:

python3 -m venv venv
source venv/bin/activate
_Steps: _

Clone repo: git clone https://github.com/clovaai/deep-text-recognition-benchmark
Install: pip install -r requirements.txt
Run: python3 app.py
Test: curl -X POST -F "file=@demo_1.jpg" -F "language=english" http://localhost:5000/upload

**List of language code:**
['english', 'chinese', 'vietnamese', 'spanish', 'italian', 'french', 'german', 'thai', 'korean']
default: english
