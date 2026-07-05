"""
generate_dataset.py
--------------------
Generates a synthetic but linguistically realistic Fake/Real news dataset
completely offline (no internet, no APIs). This is used when the user does
not have the original Kaggle Fake.csv / True.csv files.

If you DO have the original Kaggle "Fake and Real News" dataset, simply
drop Fake.csv and True.csv into this `dataset/` folder and SKIP running
this script - train_model.py will automatically detect and use them.
"""

import csv
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Building blocks for REAL news (formal, attributed, measured tone)
# ---------------------------------------------------------------------------
real_subjects = [
    "the Reserve Bank", "the Ministry of Finance", "the World Health Organization",
    "the United Nations", "the Election Commission", "the Supreme Court",
    "the Prime Minister's Office", "the Department of Health", "NASA",
    "the European Central Bank", "the state government", "local authorities",
    "the city council", "researchers at a leading university", "the central bank",
]
real_actions = [
    "announced a new policy", "released its quarterly report", "held a press conference",
    "signed an agreement with neighboring countries", "approved a new infrastructure project",
    "published updated guidelines", "confirmed a revision in interest rates",
    "launched a public health initiative", "presented the annual budget",
    "concluded an investigation into the matter", "issued an official statement",
    "scheduled a meeting with stakeholders", "released findings from a peer-reviewed study",
]
real_sources = [
    "according to officials", "sources within the department confirmed",
    "as reported by multiple news agencies", "the official spokesperson said",
    "data verified by independent auditors shows", "the report, published on the official website, stated",
    "in a statement released on Tuesday", "citing official records",
]
real_extra = [
    "The decision follows months of deliberation among experts.",
    "Officials stated that further details will be released next week.",
    "The report has been reviewed by independent analysts.",
    "Stakeholders welcomed the move, citing its long-term benefits.",
    "The announcement comes after a series of consultations with industry leaders.",
    "Authorities emphasized that the implementation will be gradual.",
    "The figures were cross-checked against previous quarterly data.",
    "A follow-up briefing is expected to be held later this month.",
]

# ---------------------------------------------------------------------------
# Building blocks for FAKE news (sensational, unverified, emotional tone)
# ---------------------------------------------------------------------------
fake_subjects = [
    "doctors", "a secret government memo", "an anonymous insider", "a viral post",
    "scientists you've never heard of", "a shocking new report", "a leaked document",
    "celebrities", "an unnamed source close to the family", "a popular blogger",
    "a self-proclaimed expert", "social media users", "a mysterious whistleblower",
]
fake_actions = [
    "claim this one weird trick cures everything", "reveal the truth they don't want you to know",
    "warn that the world will end next month", "expose a massive cover-up",
    "say the vaccine secretly contains microchips", "confirm aliens are hiding among us",
    "leak proof of a global conspiracy", "show the shocking secret behind the scenes",
    "reveal celebrities are actually robots", "claim the election was completely rigged",
    "say the government is hiding the cure for cancer", "insist the moon landing was staged",
]
fake_sources = [
    "you won't believe what happens next", "this will shock you", "share before it gets deleted",
    "the mainstream media refuses to report this", "they don't want you to see this",
    "experts are too afraid to speak up", "this has been hidden from the public for years",
    "wake up people, this is huge",
]
fake_extra = [
    "Forward this to everyone you know before it's too late!!!",
    "The mainstream media is completely silent about this shocking truth.",
    "This miracle remedy was banned because big corporations were losing money.",
    "Thousands of people are waking up to the truth every single day.",
    "Click here now before this post gets taken down forever.",
    "Nobody is talking about this and that should scare you.",
    "This proves once and for all what they've been hiding all along.",
    "Share this NOW so the truth can finally come out!!!",
]

topics = [
    "the economy", "the new vaccine", "climate change", "the upcoming election",
    "a popular celebrity", "the stock market", "a major sports event", "a new technology",
    "the housing market", "a viral health trend", "a natural disaster", "the education system",
    "a political scandal", "a tech company's new product", "a global pandemic",
]


def make_real_article():
    subj = random.choice(real_subjects)
    action = random.choice(real_actions)
    source = random.choice(real_sources)
    topic = random.choice(topics)
    extra1 = random.choice(real_extra)
    extra2 = random.choice(real_extra)
    title = f"{subj.capitalize()} {action} regarding {topic}"
    body = (
        f"{source.capitalize()}, {subj} {action} concerning {topic} earlier today. "
        f"{extra1} {extra2} Officials noted that the process will continue to be monitored "
        f"closely over the coming weeks, with further updates expected to follow standard "
        f"procedure. The matter has been documented and is available through official channels."
    )
    return title, body


def make_fake_article():
    subj = random.choice(fake_subjects)
    action = random.choice(fake_actions)
    source = random.choice(fake_sources)
    topic = random.choice(topics)
    extra1 = random.choice(fake_extra)
    extra2 = random.choice(fake_extra)
    title = f"{subj.upper()} {action.upper()} about {topic.upper()}!!!"
    body = (
        f"{source.capitalize()}! {subj.capitalize()} {action} related to {topic}. "
        f"{extra1} {extra2} Sources who wish to remain anonymous say this is just the "
        f"beginning, and that more shocking revelations are coming soon. Do your own research!"
    )
    return title, body


def generate(n_per_class=1500):
    real_rows, fake_rows = [], []
    for _ in range(n_per_class):
        t, b = make_real_article()
        real_rows.append((t, b, "politicsNews", "real"))
        t, b = make_fake_article()
        fake_rows.append((t, b, "News", "fake"))
    return real_rows, fake_rows


def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "text", "subject", "label"])
        writer.writerows(rows)


if __name__ == "__main__":
    real_rows, fake_rows = generate(1500)
    save_csv("dataset/True.csv", real_rows)
    save_csv("dataset/Fake.csv", fake_rows)
    print(f"Generated {len(real_rows)} real and {len(fake_rows)} fake articles.")
    print("Saved to dataset/True.csv and dataset/Fake.csv")
