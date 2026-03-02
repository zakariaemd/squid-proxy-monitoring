# 🌐 Monitoring Trafic — Proxy Web Squid 2024

> **Stack :** Linux · Squid · Python · Pandas · Plotly  
> **Type :** Network Security · Log Analytics · KPI Reporting

---

## 🎯 Objectif

Sécuriser et contrôler l'accès web d'un réseau local tout en produisant
des rapports d'activité réseau exploitables à partir des logs Squid.

---

## 🏗️ Architecture

```
[Clients LAN 192.168.1.0/24]
          │
          ▼
  [Squid Proxy :3128]
    ├── ACL Rules
    ├── Blocklist
    └── Access Logs
          │
          ▼
  [Log Parser Python]
          │
          ▼
  [Dashboard KPI]
```

---

## 📊 KPIs Réseau Générés

| KPI | Valeur |
|-----|--------|
| 🔢 Requêtes analysées | 5 000 |
| 🚫 Taux de blocage | ~10% |
| ⚡ Cache Hit Rate | ~25% |
| 👥 Utilisateurs uniques | 30 |
| ⏱️ Latence moyenne | ~1 010 ms |

---

## 🔒 Règles de Sécurité Configurées

- ✅ Blocage ports non standard
- ✅ Filtrage réseaux sociaux (heures de travail)
- ✅ Liste noire de domaines malveillants
- ✅ Logs rotatifs (7 jours)
- ✅ Rapports d'activité automatisés

---

## 🚀 Lancer le projet

```bash
# Parser les logs
python scripts/parse_logs.py

# Générer le dashboard
python dashboard/squid_dashboard.py
```

---

## 🛠️ Stack

![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
