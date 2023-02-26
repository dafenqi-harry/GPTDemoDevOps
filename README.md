# GPTDemoDevOps
This is a Demo application to show integration between ChatGPT/OpenAI API and Azure DevOps.
Steps:

1. Build

Open your IDE such as VS Code for example. In a terminal,  

```bash
git clone https://github.com/dafenqi-harry/GPTDemoDevOps.git
```

<aside>
💡 index.html for front render template.

Modify with your own OpenAI API Key and save file.
  
</aside>

Run the application in [localhost](http://localhost) to validating that the web app is ready.

```bash
cd GPTDemoDevOps

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

flask run
```
