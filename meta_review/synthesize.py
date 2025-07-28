from pathlib import Path
import json, yaml
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

PROC_DIR = Path("data/processed")

class Synthesizer:
    def __init__(self, conf: str = "config.yaml"):
        self.conf = yaml.safe_load(Path(conf).read_text())

        self.llm = Ollama(model=self.conf["models"]["llm"]["model"],
                          temperature=0.2)

        self.prompt = PromptTemplate.from_template(
            "You are an expert science journalist writing a coherent "
            "{words}-word meta-review on AI in healthcare. "
            "Use the provided thematic abstracts as base material, synthesize them, "
            "remove duplicates, ensure logical flow (Intro – 5-6 themed sections – Conclusion), "
            "cite concrete studies when available.\n\n"
            "{input}\n\n---\n\nMeta-review:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, outfile: str = "meta_review.txt") -> str:
        summaries = json.loads((PROC_DIR / "summaries.json").read_text())
        scaffold  = "\n\n".join([f"### Theme {i}\n\n{txt}"
                                 for i, txt in summaries.items()])

        article = self.chain.invoke(
            {"input": scaffold,
             "words": self.conf["meta"]["target_words"]}
        )

        if isinstance(article, dict):
            article_text = article.get("text", "")
        else:
            article_text = str(article)

        Path(outfile).write_text(article_text.strip())
        print(f" Meta-review saved {outfile}")
        return article_text

