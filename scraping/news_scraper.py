from pathlib import Path
import feedparser, newspaper, random, json, yaml, traceback
from utils.helpers import dedupe_by_url

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class NewsScraper:
    def __init__(self, conf_path: str = "config.yaml"):
        self.conf = yaml.safe_load(Path(conf_path).read_text())
        self.feeds = self.conf["scraping"]["rss_feeds"]
        self.max_per = self.conf["scraping"].get("max_per_source", 200)
        self.keywords = [kw.lower() for kw in self.conf["scraping"].get("keywords", [])]

    def _match(self, entry):
        if not self.keywords:
            return True
        txt = ((entry.get("title") or "") + " " + (entry.get("summary") or "")).lower()
        return any(kw in txt for kw in self.keywords)

    def _download(self, url: str) -> str | None:
        try:
            art = newspaper.Article(url)
            art.download()
            art.parse()
            return art.text if art.text.strip() else None
        except Exception:
            return None

    def collect(self, n_target: int = 100):
        items, dropped = [], 0
        for feed in self.feeds:
            parsed = feedparser.parse(feed)
            random.shuffle(parsed.entries)
            filtered = [e for e in parsed.entries if self._match(e)]
            for e in filtered[: self.max_per]:
                text = self._download(e.link) or (e.get("summary") or "")
                if not text.strip():
                    dropped += 1
                    continue
                items.append(
                    dict(
                        title=e.get("title", ""),
                        url=e.link,
                        published=e.get("published", ""),
                        text=text,
                    )
                )
                if len(items) >= n_target:
                    break
            if len(items) >= n_target:
                break

        items = dedupe_by_url(items)
        (DATA_DIR / "articles.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2)
        )

        return items
