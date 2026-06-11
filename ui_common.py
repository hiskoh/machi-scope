from __future__ import annotations

import streamlit as st


def apply_base_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --scope-ink: #22302d;
            --scope-muted: #65726f;
            --scope-line: rgba(34, 48, 45, .14);
            --scope-green: #1f7a68;
            --scope-green-soft: #edf6f2;
            --scope-blue: #2f6f9f;
            --scope-gold: #9d6b22;
            --scope-paper: #fffdf8;
            --scope-sky-soft: #eef6fb;
        }
        .stApp {
            background:
                linear-gradient(180deg, #fbfaf6 0%, #f7faf8 46%, #fbfaf6 100%);
        }
        .main .block-container {
            max-width: 1160px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, h4 { letter-spacing: 0; color: var(--scope-ink); }
        div[data-testid="stSidebar"] {
            border-right: 1px solid var(--scope-line);
            background: rgba(255, 253, 248, .82);
        }
        .scope-hero {
            border: 1px solid var(--scope-line);
            background:
                radial-gradient(circle at 12% 20%, rgba(31, 122, 104, .12), transparent 26%),
                radial-gradient(circle at 84% 0%, rgba(47, 111, 159, .11), transparent 28%),
                linear-gradient(135deg, rgba(255, 255, 255, .96), rgba(255, 253, 248, .92)),
                #ffffff;
            border-radius: 8px;
            padding: 1.55rem 1.6rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 32px rgba(34, 48, 45, .07);
        }
        .scope-eyebrow {
            color: var(--scope-green);
            font-size: .88rem;
            font-weight: 700;
            margin-bottom: .32rem;
        }
        .scope-hero h1 {
            margin: 0 0 .45rem;
            font-size: 2.18rem;
            line-height: 1.25;
        }
        .scope-hero p {
            color: var(--scope-muted);
            margin: 0;
            max-width: 780px;
            line-height: 1.75;
        }
        .scope-card {
            border: 1px solid var(--scope-line);
            background: #fff;
            border-radius: 8px;
            padding: 1rem;
            margin: .65rem 0;
            box-shadow: 0 4px 16px rgba(34, 48, 45, .045);
        }
        .scope-card h3 {
            font-size: 1.08rem;
            margin: 0 0 .45rem;
        }
        .scope-card p {
            color: var(--scope-muted);
            line-height: 1.65;
            margin: .35rem 0;
        }
        .scope-action-card {
            border: 1px solid var(--scope-line);
            background: #fff;
            border-radius: 8px;
            padding: 1.25rem;
            min-height: 210px;
            margin: .35rem 0 .65rem;
            box-shadow: 0 10px 28px rgba(34, 48, 45, .065);
        }
        .scope-action-card h2 {
            font-size: 1.55rem;
            line-height: 1.35;
            margin: .55rem 0 .55rem;
        }
        .scope-action-card p {
            color: var(--scope-muted);
            line-height: 1.75;
            margin: 0;
        }
        .scope-kicker {
            color: var(--scope-green);
            font-weight: 700;
            font-size: .88rem;
            margin-bottom: .2rem;
        }
        .scope-pill {
            display: inline-block;
            padding: .16rem .48rem;
            border: 1px solid #cddbd5;
            border-radius: 999px;
            background: var(--scope-green-soft);
            color: #315f53;
            font-size: .82rem;
            margin: 0 .25rem .25rem 0;
        }
        .scope-pill-blue {
            display: inline-block;
            padding: .16rem .48rem;
            border: 1px solid #c9d9e5;
            border-radius: 999px;
            background: var(--scope-sky-soft);
            color: #315d7a;
            font-size: .82rem;
            margin: 0 .25rem .25rem 0;
        }
        .scope-note {
            border-left: 4px solid var(--scope-green);
            background: #fbfdfb;
            padding: .75rem .85rem;
            color: #35413f;
            margin: .75rem 0;
            line-height: 1.65;
        }
        .scope-mini {
            color: var(--scope-muted);
            font-size: .9rem;
            line-height: 1.6;
        }
        .scope-band {
            border: 1px solid var(--scope-line);
            background: rgba(255, 255, 255, .72);
            border-radius: 8px;
            padding: 1rem;
            margin: 1.25rem 0;
        }
        .scope-focus {
            display: grid;
            grid-template-columns: minmax(0, 1.7fr) minmax(240px, .8fr);
            gap: 1rem;
            align-items: stretch;
            margin: 1rem 0 1.35rem;
        }
        .scope-focus-main,
        .scope-focus-side {
            border: 1px solid var(--scope-line);
            background: rgba(255, 255, 255, .78);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 4px 16px rgba(34, 48, 45, .045);
        }
        .scope-focus-main h2 {
            font-size: 1.35rem;
            margin: .15rem 0 .35rem;
        }
        .scope-focus-main p,
        .scope-focus-side span {
            color: var(--scope-muted);
            line-height: 1.65;
            margin: 0;
        }
        .scope-focus-side strong {
            display: block;
            margin-bottom: .35rem;
        }
        .scope-word-cloud {
            border: 1px solid var(--scope-line);
            border-radius: 8px;
            background: #fff;
            padding: 1rem;
            margin: .5rem 0 1rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,.65);
        }
        .scope-word-chip {
            display: inline-block;
            margin: .18rem .32rem;
            padding: .14rem .2rem;
            color: #1f4f45;
            line-height: 1.2;
        }
        .scope-rank-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .75rem;
            margin: .75rem 0 1rem;
        }
        .scope-rank-card {
            border: 1px solid var(--scope-line);
            background: #fff;
            border-radius: 8px;
            padding: .9rem;
            box-shadow: 0 4px 16px rgba(34, 48, 45, .045);
        }
        .scope-rank-card .rank {
            color: var(--scope-green);
            font-size: .82rem;
            font-weight: 700;
        }
        .scope-rank-card strong {
            display: block;
            color: var(--scope-ink);
            font-size: 1.25rem;
            margin: .2rem 0;
        }
        .scope-rank-card span {
            color: var(--scope-muted);
            font-size: .9rem;
        }
        .scope-steps {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .75rem;
        }
        .scope-step {
            border: 1px solid var(--scope-line);
            background: rgba(255,255,255,.82);
            border-radius: 8px;
            padding: .85rem;
        }
        .scope-step strong {
            color: var(--scope-ink);
            display: block;
            margin-bottom: .25rem;
        }
        .scope-step span {
            color: var(--scope-muted);
            font-size: .9rem;
            line-height: 1.55;
        }
        div.stButton > button {
            border-radius: 8px;
            border: 1px solid rgba(31, 122, 104, .24);
            background: #ffffff;
            color: var(--scope-ink);
            min-height: 2.55rem;
        }
        div.stButton > button:hover {
            border-color: rgba(31, 122, 104, .55);
            color: var(--scope-green);
        }
        div[data-testid="stMetric"] {
            border: 1px solid var(--scope-line);
            background: #fff;
            border-radius: 8px;
            padding: .85rem;
        }
        @media (max-width: 760px) {
            .scope-hero h1 { font-size: 1.55rem; }
            .scope-steps { grid-template-columns: 1fr; }
            .scope-focus { grid-template-columns: 1fr; }
            .scope-rank-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_hero(eyebrow: str, title: str, body: str) -> None:
    apply_base_styles()
    st.markdown(
        f"""
        <section class="scope-hero">
            <div class="scope-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{body}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def pill_row(items: tuple[str, ...] | list[str]) -> str:
    return "".join(f'<span class="scope-pill">{item}</span>' for item in items)


def feature_card(title: str, body: str, tags: tuple[str, ...] | list[str], note: str = "") -> None:
    note_html = f'<div class="scope-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <section class="scope-card">
            <h3>{title}</h3>
            <div>{pill_row(tags)}</div>
            <p>{body}</p>
            {note_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def step_row(steps: tuple[tuple[str, str], ...] | list[tuple[str, str]]) -> None:
    step_html = "".join(
        f'<div class="scope-step"><strong>{title}</strong><span>{body}</span></div>'
        for title, body in steps
    )
    st.markdown(f'<div class="scope-steps">{step_html}</div>', unsafe_allow_html=True)
