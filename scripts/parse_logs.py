# ============================================
# SQUID LOG PARSER
# Transforme les logs bruts en DataFrame structuré
# ============================================

import re
import pandas as pd
from datetime import datetime
import random

def generate_synthetic_logs(n=5000):
    """
    Génère des logs Squid synthétiques réalistes
    pour démonstration et analyse
    """
    random.seed(42)

    domains = {
        'Travail':       ['github.com','stackoverflow.com','gitlab.com',
                          'docs.python.org','npmjs.com','pypi.org'],
        'Recherche':     ['google.com','bing.com','duckduckgo.com',
                          'scholar.google.com','wikipedia.org'],
        'E-Commerce':    ['amazon.fr','fnac.com','cdiscount.com',
                          'leboncoin.fr','aliexpress.com'],
        'Réseaux Sociaux':['facebook.com','instagram.com','twitter.com',
                           'linkedin.com','tiktok.com'],
        'Streaming':     ['youtube.com','netflix.com','twitch.tv',
                          'spotify.com','deezer.com'],
        'Actualités':    ['lemonde.fr','lefigaro.fr','bbc.com',
                          'reuters.com','20minutes.fr'],
        'Bloqué':        ['malware-site.com','phishing.net',
                          'blocked-ads.com','tracker.net']
    }

    users = [f'user{i}' for i in range(1, 31)]
    ips   = [f'192.168.1.{i}' for i in range(10, 41)]

    statuses = {
        'TCP_MISS':    ('200', 0.55),
        'TCP_HIT':     ('200', 0.25),
        'TCP_DENIED':  ('403', 0.10),
        'TCP_EXPIRED': ('200', 0.07),
        'TCP_ERROR':   ('500', 0.03),
    }

    records = []
    base_ts = 1704067200  # 2024-01-01 00:00:00

    for i in range(n):
        # Timestamp progressif sur 365 jours
        ts        = base_ts + random.randint(0, 365 * 86400)
        dt        = datetime.fromtimestamp(ts)

        user      = random.choice(users)
        ip        = random.choice(ips)
        elapsed   = random.randint(20, 2000)

        # Choix catégorie & domaine
        if dt.weekday() >= 5:  # week-end → plus de streaming
            cat_weights = [0.15, 0.10, 0.15, 0.20, 0.30, 0.08, 0.02]
        elif 8 <= dt.hour <= 18:  # heures de travail
            cat_weights = [0.35, 0.20, 0.10, 0.05, 0.08, 0.15, 0.07]
        else:
            cat_weights = [0.10, 0.10, 0.20, 0.25, 0.20, 0.12, 0.03]

        categories = list(domains.keys())
        category   = random.choices(categories, weights=cat_weights)[0]
        domain     = random.choice(domains[category])

        # Statut
        status_keys   = list(statuses.keys())
        status_weights = [statuses[s][1] for s in status_keys]
        squid_status  = random.choices(status_keys, weights=status_weights)[0]
        http_code     = statuses[squid_status][0]

        # Taille réponse
        if squid_status == 'TCP_DENIED':
            size = 0
        elif category == 'Streaming':
            size = random.randint(500000, 5000000)
        else:
            size = random.randint(500, 100000)

        records.append({
            'timestamp':    ts,
            'datetime':     dt,
            'date':         dt.date(),
            'hour':         dt.hour,
            'weekday':      dt.strftime('%A'),
            'month':        dt.strftime('%Y-%m'),
            'elapsed_ms':   elapsed,
            'client_ip':    ip,
            'user':         user,
            'squid_status': squid_status,
            'http_code':    http_code,
            'bytes':        size,
            'method':       random.choice(['GET', 'GET', 'GET', 'POST', 'CONNECT']),
            'domain':       domain,
            'category':     category,
            'is_blocked':   squid_status == 'TCP_DENIED',
            'is_hit':       squid_status == 'TCP_HIT'
        })

    return pd.DataFrame(records)


def compute_kpis(df):
    """Calcule les KPIs réseau à partir des logs parsés"""
    total     = len(df)
    blocked   = df['is_blocked'].sum()
    cache_hit = df['is_hit'].sum()
    total_vol = df['bytes'].sum()

    kpis = {
        'total_requetes':       total,
        'requetes_bloquees':    blocked,
        'taux_blocage_pct':     round(blocked / total * 100, 2),
        'cache_hit_rate_pct':   round(cache_hit / total * 100, 2),
        'volume_total_gb':      round(total_vol / 1e9, 3),
        'utilisateurs_uniques': df['user'].nunique(),
        'domaines_uniques':     df['domain'].nunique(),
        'latence_moy_ms':       round(df['elapsed_ms'].mean(), 1)
    }
    return kpis


if __name__ == '__main__':
    print("🔄 Génération des logs synthétiques...")
    df = generate_synthetic_logs(5000)
    df.to_csv('logs/parsed_logs.csv', index=False)

    kpis = compute_kpis(df)
    print("\n📊 KPIs Réseau :")
    for k, v in kpis.items():
        print(f"  {k:<30} : {v}")

    print("\n✅ Logs parsés → logs/parsed_logs.csv")
