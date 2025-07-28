
# Karashash

Я выбрала локальный Ollama (`mistral:7b-instruct`). Библиотеки: `langchain`, `sentence-transformers`, `scikit-learn`, `feedparser`, `newspaper3k`. И без langgraph, все решается простым вызовом LLM.

## Структура проекта
```
ai-healthcare-meta-review/
├── main.py                     # точка входа orchestrates 4 шага
├── config.example.yaml         # шаблон настроек
├── requirements.txt            # зависимости
├── scraping/
│   └── news_scraper.py         # RSS-скрапинг + извлечение текста
├── processing/
│   └── cluster.py              # эмбеддинги + KMeans
├── summarization/
│   └── summarize.py            # резюме каждого кластера
├── meta_review/
│   └── synthesize.py           # финальный мета-обзор
├── utils/
│   └── helpers.py              # мелкие функции
└── data/                       # результаты работы
    ├── raw/articles.json       # собранные статьи
    └── processed/…             # кластеры и резюме
```

## как запустить
```bash
cd ai-healthcare-meta-review

# окружение
python3 -m venv .venv && source .venv/bin/activate

# зависимости
pip install -r requirements.txt

# Ollama
brew install ollama         
ollama pull mistral:7b-instruct

# конфиг
cp config.example.yaml config.yaml  

# запуск
python main.py --n_articles 100 --out meta_review.txt
```
После выполнения появятся `data/raw/articles.json`, промежуточные файлы и `meta_review.txt`.

## ключевые файлы
`news_scraper.py` - Собирает новости по RSS, чистит HTML, пишет JSON
`cluster.py` - Строит эмбеддинги (SentenceTransformers) и K-Means-кластеры
`summarize.py` - Для каждого кластера вызывает LLM 400–600 слов
`synthesize.py` - Склеивает все резюме в единый мета-текст нужного объема
`main.py` - Автоматический прогон четырех шагов пайплайна

## cодержимое `data/`

- `raw/articles.json` — 86 статей, собранных при прогоне
- `processed/clustered.json` — 8 кластеров
- `processed/summaries.json` — краткие тематические обзоры
- `meta_review.txt` — итоговый материал для публикации

