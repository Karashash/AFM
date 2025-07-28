from pathlib import Path
import json, yaml, os
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

PROC_DIR = Path("data/processed")

class Summarizer:
    prompt = PromptTemplate.from_template(
        """You are a scientific writer. Summarize the following collection of news articles on AI in healthcare into an analytical abstract (400–600 words) covering:
• main breakthroughs
• practical applications
• limitations and risks
• future outlook
Articles:\n{docs}\n---\nSUMMARY:"""
    )

    def __init__(self, conf="config.yaml"):
        self.conf = yaml.safe_load(Path(conf).read_text())
        provider = self.conf["models"]["llm"]["provider"]
        if provider == "ollama":
            self.llm = Ollama(model=self.conf["models"]["llm"]["model"])
        else:
            self.llm = OpenAI(model=self.conf["models"]["llm"]["model"], temperature=0.3)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self):
        clustered = json.loads((PROC_DIR / "clustered.json").read_text())
        summaries = {}
        for label, docs in clustered.items():
            joined = "\n\n".join(d["text"][: self.conf["summary"]["tokens_per_article"]] for d in docs)
            summaries[label] = self.chain.run(docs=joined)
        Path(PROC_DIR / "summaries.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2))
        return summaries
