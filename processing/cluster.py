from pathlib import Path
import json, yaml, sys
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from utils.helpers import auto_k

DATA_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")
PROC_DIR.mkdir(parents=True, exist_ok=True)


class Clusterer:
    def __init__(self, conf: str = "config.yaml"):
        self.conf = yaml.safe_load(Path(conf).read_text())
        self.model = SentenceTransformer(self.conf["models"]["embedder"])

    def run(self):
        art_path = DATA_DIR / "articles.json"
        if not art_path.exists():
            raise RuntimeError("файл data/raw/articles.json не найден")

        articles = json.loads(art_path.read_text())

        if not articles:
            raise RuntimeError("кластеризовать нечего")

        target = self.conf.get("n_target") or 100
        if len(articles) < target:
            print(f"сохранено {len(articles)} статей вместо запрошенных {target}", file=sys.stderr)

        texts = [a["text"] for a in articles]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        k = self.conf["clustering"].get("k") or auto_k(len(articles))
        km = KMeans(n_clusters=k, random_state=42).fit(embeddings)

        clustered = {}
        for idx, label in enumerate(km.labels_):
            clustered.setdefault(int(label), []).append(articles[idx])

        (PROC_DIR / "clustered.json").write_text(json.dumps(clustered, ensure_ascii=False, indent=2))
        print(f"кластеров: {len(clustered)}; средний размер: {len(articles)//len(clustered)}")
        return clustered
