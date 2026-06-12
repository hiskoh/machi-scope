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
            border: 0;
            background:
                radial-gradient(circle at 16% 12%, rgba(255, 255, 255, .18), transparent 28%),
                radial-gradient(circle at 90% 0%, rgba(255, 255, 255, .14), transparent 30%),
                linear-gradient(135deg, #146857 0%, #1f7a68 48%, #2f6f9f 100%);
            border-radius: 8px;
            padding: 1.7rem 1.65rem;
            margin-bottom: 1.1rem;
            box-shadow: 0 16px 36px rgba(31, 122, 104, .18);
        }
        .scope-eyebrow {
            color: rgba(255, 255, 255, .82);
            font-size: .88rem;
            font-weight: 700;
            margin-bottom: .32rem;
        }
        .scope-hero h1 {
            margin: 0 0 .45rem;
            font-size: 2.18rem;
            line-height: 1.25;
            color: #fff;
        }
        .scope-hero p {
            color: rgba(255, 255, 255, .86);
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
        .scope-rank-headings {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 2rem;
            margin: 1rem 0 .2rem;
        }
        .scope-rank-headings h3 {
            margin: 0;
            color: var(--scope-ink);
            font-size: 1.45rem;
            line-height: 1.25;
        }
        .scope-rise-card {
            border: 1px solid rgba(31, 122, 104, .16);
            background: #fff;
            border-radius: 8px;
            padding: .78rem .82rem;
            margin: .8rem 0 .32rem;
            min-height: 6.25rem;
            box-shadow: 0 8px 24px rgba(34, 48, 45, .055);
        }
        .scope-rise-head {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr) auto;
            gap: .58rem;
            align-items: baseline;
        }
        .scope-rise-head > span {
            display: inline-grid;
            place-items: center;
            width: 1.55rem;
            height: 1.55rem;
            border-radius: 999px;
            background: rgba(31, 122, 104, .1);
            color: var(--scope-green);
            font-weight: 800;
            font-size: .85rem;
        }
        .scope-rise-head strong {
            color: var(--scope-ink);
            font-size: 1.2rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .scope-rise-badge {
            border: 1px solid rgba(31, 122, 104, .2);
            background: #c9f3d0;
            color: #1b6d35;
            border-radius: 999px;
            font-size: .92rem;
            font-weight: 800;
            line-height: 1.1;
            text-align: center;
            padding: .26rem .52rem .3rem;
            letter-spacing: 0;
            white-space: nowrap;
        }
        .scope-rise-sub {
            display: flex;
            justify-content: space-between;
            gap: .7rem;
            align-items: baseline;
            margin-top: .42rem;
            color: var(--scope-muted);
            font-size: .82rem;
        }
        .scope-rise-sub b {
            color: var(--scope-green);
            font-weight: 700;
            white-space: nowrap;
        }
        .scope-rise-track {
            height: .44rem;
            border-radius: 999px;
            background: #edf5f0;
            overflow: hidden;
            margin-top: .62rem;
        }
        .scope-rise-track div {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #1f7a68, #72bf8a);
        }
        .scope-word-rank-card {
            border: 1px solid rgba(47, 111, 159, .14);
            background: #fff;
            border-radius: 8px;
            padding: .78rem .82rem;
            margin: .8rem 0 .32rem;
            min-height: 6.25rem;
            box-shadow: 0 8px 24px rgba(34, 48, 45, .045);
        }
        .scope-word-rank-head {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr) auto;
            gap: .58rem;
            align-items: baseline;
        }
        .scope-word-rank-head span {
            display: inline-grid;
            place-items: center;
            width: 1.55rem;
            height: 1.55rem;
            border-radius: 999px;
            background: rgba(47, 111, 159, .1);
            color: #2f6f9f;
            font-weight: 800;
            font-size: .85rem;
        }
        .scope-word-rank-head strong {
            color: var(--scope-ink);
            font-size: 1.2rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .scope-word-rank-head em {
            color: #2f6f9f;
            font-size: 1rem;
            font-weight: 800;
            font-style: normal;
            white-space: nowrap;
        }
        .scope-word-rank-track {
            height: .44rem;
            border-radius: 999px;
            background: #eef4f5;
            overflow: hidden;
            margin-top: .62rem;
        }
        .scope-word-rank-track div {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #2f6f9f, #5ba6a3);
        }
        .scope-stat-scope {
            border: 1px solid rgba(31, 122, 104, .14);
            background: linear-gradient(180deg, rgba(247, 251, 249, .96), #fff);
            border-radius: 8px;
            padding: .9rem 1rem;
            margin: .2rem 0 1rem;
        }
        .scope-stat-scope strong {
            display: block;
            color: var(--scope-ink);
            font-size: 1.1rem;
            line-height: 1.25;
        }
        .scope-stat-scope em {
            display: block;
            color: var(--scope-muted);
            font-style: normal;
            font-size: .84rem;
            margin-top: .18rem;
        }
        .scope-stat-scope div {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .68rem;
        }
        .scope-stat-scope span {
            border: 1px solid rgba(31, 122, 104, .16);
            background: #eef7f2;
            color: #1f5f52;
            border-radius: 999px;
            font-size: .82rem;
            padding: .22rem .55rem;
        }
        .scope-detail-card {
            border: 1px solid rgba(47, 111, 159, .2);
            background: #fff;
            border-radius: 8px;
            padding: .95rem 1rem;
            margin: .62rem 0 .45rem;
            box-shadow: 0 6px 18px rgba(34, 48, 45, .045);
        }
        .scope-detail-card span {
            display: block;
            color: var(--scope-muted);
            font-size: .84rem;
            margin-bottom: .2rem;
        }
        .scope-detail-card strong {
            display: block;
            color: #1f7a68;
            font-size: 1rem;
            margin-bottom: .35rem;
        }
        .scope-detail-card p {
            color: var(--scope-ink);
            line-height: 1.65;
            margin: 0;
        }
        .scope-signal-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .8rem;
            margin: .9rem 0 1rem;
        }
        .scope-signal-card {
            border: 1px solid rgba(31, 122, 104, .14);
            background: #fff;
            border-radius: 8px;
            padding: .9rem 1rem;
            box-shadow: 0 6px 18px rgba(34, 48, 45, .045);
        }
        .scope-signal-card.is-up {
            border-color: rgba(31, 122, 104, .22);
            background: linear-gradient(180deg, rgba(236, 249, 241, .88), #fff);
        }
        .scope-signal-card.is-down {
            border-color: rgba(157, 107, 34, .2);
            background: linear-gradient(180deg, rgba(250, 244, 232, .9), #fff);
        }
        .scope-signal-card span {
            display: block;
            color: var(--scope-muted);
            font-size: .78rem;
            margin-bottom: .15rem;
        }
        .scope-signal-card strong {
            display: block;
            color: var(--scope-ink);
            font-size: clamp(1.55rem, 4vw, 2.15rem);
            line-height: 1.05;
        }
        .scope-signal-card em {
            display: block;
            color: var(--scope-green);
            font-size: .82rem;
            font-style: normal;
            margin-top: .2rem;
        }
        .scope-delta-row {
            display: flex;
            align-items: center;
            gap: .65rem;
            margin: .55rem 0 .35rem;
        }
        .scope-delta-track {
            flex: 1;
            height: .62rem;
            border-radius: 999px;
            background: #edf2ef;
            overflow: hidden;
            box-shadow: inset 0 0 0 1px rgba(34, 48, 45, .05);
        }
        .scope-delta-fill {
            height: 100%;
            min-width: .35rem;
            border-radius: 999px;
            background: linear-gradient(90deg, #1f7a68, #2f6f9f);
        }
        .scope-delta-fill.is-down {
            background: linear-gradient(90deg, #9d6b22, #d6a950);
        }
        .scope-delta-label {
            color: var(--scope-muted);
            font-size: .82rem;
            white-space: nowrap;
        }
        .scope-delta-years {
            display: flex;
            justify-content: space-between;
            gap: .75rem;
            color: var(--scope-muted);
            font-size: .82rem;
            margin-top: .45rem;
        }
        .scope-panel-title {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: .75rem;
            margin: 1.15rem 0 .35rem;
        }
        .scope-panel-title h3 {
            margin: 0;
            font-size: 1.25rem;
        }
        .scope-panel-title span {
            color: var(--scope-muted);
            font-size: .86rem;
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
        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            border-color: rgba(31, 122, 104, .88);
            background: var(--scope-green);
            color: #fff;
        }
        div.stButton > button:hover {
            border-color: rgba(31, 122, 104, .55);
            color: var(--scope-green);
        }
        div.stFormSubmitButton > button {
            border-radius: 8px;
            min-height: 2.55rem;
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
            .scope-rank-headings { display: none; }
            .scope-signal-grid { grid-template-columns: 1fr; }
            .scope-panel-title { display: block; }
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
