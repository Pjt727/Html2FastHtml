# Html2FastHtml 
This is small server to convert html to FastHtml components.
The web server is made with [FastHtml](https://github.com/AnswerDotAI/fasthtml "fasthtml github") and
   uses [ruff](https://github.com/astral-sh/ruff "Ruff github") as a code formatter by default.
It works by taking forming the submitted html into a tree and then traverses that tree
   generating FastHtml components.
Once the FastHtml component string is done it writes it to a file and then formats it.
Any formatter configuration you wish to apply should work like normal.
# demo

# setup
- Clone the repository
- Install dependencies (pip venv example below)
    - `python -m venv venv` (creates virtual environment)
    - windows: `.\venv\Scripts\activate` OR Mac/Linux `source venv/bin/activate` (activates the virtual environment)
    - `pip install -r requirement.txt` (installs required libaries: fasthtml and ruff)
- run the website locally `python main.py`
