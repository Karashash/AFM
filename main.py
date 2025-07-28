from scraping.news_scraper import NewsScraper
from processing.cluster import Clusterer
from summarization.summarize import Summarizer
from meta_review.synthesize import Synthesizer
import argparse, pathlib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_articles", type=int, default=100)
    parser.add_argument("--out", type=str, default="meta_review.txt")
    args = parser.parse_args()

    pathlib.Path("data").mkdir(exist_ok=True)

    print("Scrapin")
    NewsScraper().collect(n_target=args.n_articles)

    print("Clustering")
    Clusterer().run()

    print("Summarizing clusters")
    Summarizer().run()

    print("Synthesizing meta-review")
    Synthesizer().run(outfile=args.out)

    print(f"Done {args.out}")
