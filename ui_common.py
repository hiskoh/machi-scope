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
        }
        .main .block-container {
            max-width: 1160px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, h4 { letter-spacing: 0; color: var(--scope-ink); }
        div[data-testid="stSidebar"] {
            border-right: 1px solid var(--scope-line);
        }
        .scope-hero {
            border: 1px solid var(--scope-line);
            background:
                linear-gradient(135deg, rgba(31, 122, 104, .08), rgba(47, 111, 159, .08)),
                #ffffff;
            border-radius: 8px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1rem;
        }
        .scope-eyebrow {
            color: var(--scope-green);
            font-size: .88rem;
            font-weight: 700;
            margin-bottom: .32rem;
        }
        .scope-hero h1 {
            margin: 0 0 .45rem;
            font-size: 2rem;
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
            border-top: 1px solid var(--scope-line);
            border-bottom: 1px solid var(--scope-line);
            padding: 1rem 0;
            margin: 1.25rem 0;
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
