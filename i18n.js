/* ════════════════════════════════════════════════════════════════
   Serie A Scout Index — i18n module (vanilla JS, no deps)
   ──────────────────────────────────────────────────────────────
   - Italian (default) + English
   - Persistence in localStorage("lang")
   - Auto-detect browser lang on first visit
   - Lang switcher mounted in [data-i18n-switcher] slot (each nav has one)
   - Live re-render: no page reload on switch
   - Attributes supported:
       data-i18n="key"               → textContent
       data-i18n-html="key"          → innerHTML (use solo se la stringa
                                        contiene HTML controllato)
       data-i18n-placeholder="key"   → input/textarea placeholder
       data-i18n-title="key"         → element.title (tooltip)
       data-i18n-aria-label="key"    → aria-label
   ════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ── DIZIONARIO ──────────────────────────────────────────── */
  const I18N = {
    it: {
      /* nav comune */
      nav_home:            "Homepage",
      nav_dashboard:       "Dashboard",
      nav_validation:      "Validazione",
      nav_methodology:     "Metodologia",
      nav_back_homepage:   "Torna alla Homepage",
      nav_back_ranking:    "Torna alla classifica",
      nav_back:            "Indietro",
      nav_forward:         "Avanti",
      nav_lang_label:      "Lingua",

      /* azioni / pulsanti comuni */
      btn_search:          "Cerca",
      btn_close:           "Chiudi",
      btn_compare:         "Confronto",
      btn_methodology:     "Metodologia",
      btn_explore:         "Esplora dashboard",
      btn_see_validation:  "Vedi validazione",
      btn_read_method:     "Leggi metodologia",

      /* placeholder / messaggi */
      ph_search_player:    "Cerca giocatore…",
      msg_loading:         "Caricamento…",
      msg_no_data:         "Nessun dato disponibile",
      msg_no_results:      "Nessun risultato",

      /* termini dominio (uniformati) */
      term_players:        "Giocatori",
      term_teams:          "Squadre",
      term_ranking:        "Classifica",
      term_statistics:     "Statistiche",
      term_minutes:        "Minuti",
      term_role:           "Ruolo",
      term_team:           "Squadra",
      term_player:         "Giocatore",
      term_home:           "Casa",
      term_away:           "Trasferta",
      term_vs_top6:        "vs Top 6",
      term_vs_strong:      "Difese Solide",
      term_total:          "Totale",

      /* HOMEPAGE */
      hp_eyebrow:          "⚽ Analisi Calcio · Serie A 25/26",
      hp_tagline:          "Modello Data-Driven per il Ranking dei Giocatori",
      hp_intro:            "Un modello per valutare e ordinare i giocatori della Serie A usando metriche di performance indipendenti — corrette per la difficoltà degli avversari, stabilizzate con Bayesian Shrinkage, validate contro risultati reali.",
      hp_bullet_1:         "<strong>6 KPI indipendenti</strong> — Output, Centralità, Boost, Consistenza (basata su IQR), Indice Età (AII), Affidabilità Fisica (PRI), standardizzati con <strong>z-score winsorizzati</strong>",
      hp_bullet_2:         "<strong>406 giocatori · 21 giornate · 5 contesti</strong> — Totale, Casa, Trasferta, vs Top 6, vs Difese Solide",
      hp_bullet_3:         "<strong>Validato statisticamente</strong> — Backtest predittivo Spearman ρ=0.70, intervalli di confidenza bootstrap al 95%, stabilità ranking Kendall τ, effect size Cohen's d",
      hp_tag_xg:           "xG · xA · pesatura SOS",
      hp_tag_bayes:        "Bayesian Shrinkage",
      hp_tag_pro:          "✨ TPI Pro — AII + PRI",
      hp_tag_validated:    "Statisticamente validato",
      hp_whats_inside:     "Cosa c'è dentro",
      hp_card_dash_ttl:    "Dashboard Scout",
      hp_card_dash_body:   "Classifiche giocatori su 7 metriche, filtro squadre, confronto fino a 4 giocatori, radar TPI e analisi differenziale. Completamente responsive.",
      hp_card_dash_lnk:    "Esplora dashboard →",
      hp_card_val_ttl:     "Validazione statistica",
      hp_card_val_body:    "5 test indipendenti: Pearson r vs Fantacalcio, sovrapposizione Top 10, backtest predittivo (r=0.70), validazione AII/PRI e coerenza TPI vs TPI Pro.",
      hp_card_val_lnk:     "Vedi validazione →",
      hp_card_meth_ttl:    "Metodologia completa",
      hp_card_meth_body:   "Ogni indice spiegato con formule, motivazione e grafici interattivi. Dalla pipeline dati grezzi al TPI finale — tutti i passaggi documentati.",
      hp_card_meth_lnk:    "Leggi metodologia →",
      hp_idx_section:      "Gli indici del sistema",
      hp_idx_output_t:     "Output Adj / 90'",
      hp_idx_output_s:     "(xG+xA)/min×90 pesato per SOS — corregge la forza degli avversari",
      hp_idx_centr_t:      "Centralità Offensiva",
      hp_idx_centr_s:      "% della produzione squadra che passa dal giocatore — con Bayesian Shrinkage",
      hp_idx_boost_t:      "Team Boost Ratio",
      hp_idx_boost_s:      "xG squadra CON / SENZA — quanto vale davvero per la squadra",
      hp_idx_cons_t:       "Consistenza (basata su IQR)",
      hp_idx_cons_s:       "1 − IQR/mediana — robusto agli outlier, bounded [0,1]",
      hp_idx_aii_t:        "⭐ AII — Indice d'Età",
      hp_idx_aii_s:        "Curva gaussiana picco 27 anni — valore nel ciclo di carriera",
      hp_idx_pri_t:        "💪 PRI — Affidabilità Fisica",
      hp_idx_pri_s:        "Disponibilità + infortuni + gravità — affidabilità fisica storica",
      hp_pro_new:          "✨ Novità — TPI Pro",
      hp_pro_ttl:          "TPI Pro — 6 Dimensioni di Analisi",
      hp_pro_body:         "Il TPI classico usa 4 dimensioni offensive. Il TPI Pro aggiunge <strong style=\"color:var(--teal)\">Età Index (AII)</strong> e <strong style=\"color:var(--purp)\">Affidabilità Fisica (PRI)</strong> per uno scouting a lungo termine più accurato.",
      hp_footer_season:    "Stagione 2025/26",
      hp_footer_data:      "Dati: FBref (fonte Opta) · Transfermarkt · SosFanta · PazzidiFanta",

      /* VALIDAZIONE */
      val_title:           "Validazione del modello",
      val_subtitle:        "Cinque test indipendenti per confermare che il TPI è statisticamente valido.",
      val_pearson:         "Pearson r vs Fantacalcio",
      val_overlap:         "Sovrapposizione Top 10",
      val_backtest:        "Backtest predittivo",
      val_aii_validation:  "Validazione AII",
      val_pri_validation:  "Validazione PRI",
      val_tpi_pro_coh:     "Coerenza TPI vs TPI Pro",
      val_interpretation:  "Interpretazione",
      val_limits:          "Limiti",
      val_low:             "Basso",
      val_consistent:      "Coerente",
      val_notable_div:     "Divergenze notevoli",
      val_no_data_pro:     "Nessun dato TPI Pro",
      val_start_mysql:     "Avvia MySQL per il backtest completo",
      val_injuries:        "Infortuni",
      val_confidence:      "Confidence Score",
      val_rmse:            "RMSE",
      val_pro_players:     "Giocatori TPI Pro",
      val_aii_players:     "Giocatori con AII",
      val_pri_players:     "Giocatori con PRI",

      /* GUIDA */
      guide_title:         "Guida Completa alla Metodologia",
      guide_subtitle:      "Ogni indice, formula e scelta progettuale del Serie A Scout Index",
      guide_chapter:       "Capitolo",
      guide_formula:       "Formula",
      guide_how_calc:      "Come viene calcolato",
      guide_components:    "Componenti della formula",
      guide_base_data:     "Dati Base",
      guide_how_populate:  "Come popolare i dati",
      guide_age_curve:     "Curva AII per età",
      guide_age_age_idx:   "Age Impact Index per fascia d'età",
      guide_age_band:      "Fascia",
      guide_aff_phys:      "Affidabilità Fisica",
      guide_age_idx:       "Età Index",
      guide_centrality:    "Centralità Offensiva",
      guide_consistency:   "Consistenza",
      guide_form_ewma:     "Form EWMA",
      guide_big_match:     "Big match",
      guide_finisher:      "Finalizzatore sopra media",

      /* DASHBOARD */
      dash_title:          "Dashboard Scout",
      dash_filter_team:    "Squadra",
      dash_filter_role:    "Ruolo",
      dash_all_teams:      "Tutte",
      dash_all_roles:      "Tutti",
      dash_role_gk:        "Portiere",
      dash_role_def:       "Difensore",
      dash_role_mid:       "Centrocampista",
      dash_role_fwd:       "Attaccante",
      dash_role_gk_s:      "POR",
      dash_role_def_s:     "DIF",
      dash_role_mid_s:     "CEN",
      dash_role_fwd_s:     "ATT",
      dash_leaderboard:    "Classifica",
      dash_compare:        "Confronto",
      dash_compare_pool:   "Pool di confronto",
      dash_compare_empty:  "Aggiungi giocatori al confronto",
      dash_pick_player:    "Seleziona giocatore",
      dash_roster:         "Resto della rosa",
      dash_insufficient:   "minuti insufficienti per TPI",
      dash_diff_modal:     "Δ Differenziale",
      dash_radar:          "Radar TPI",
      dash_overview:       "Panoramica",
      dash_conversion:     "Conversione",
      dash_trend:          "Trend",
      dash_show_pro:       "Mostra TPI Pro",
      dash_hide_pro:       "Nascondi TPI Pro",
      dash_methodology:    "Metodologia",
      dash_kpi_xg90:       "xG / 90'",
      dash_kpi_xa90:       "xA / 90'",
      dash_kpi_goal90:     "Gol / 90'",
      dash_kpi_sos:        "SOS",
      dash_kpi_finish:     "Finalizzazione",
      dash_kpi_conv:       "Tasso conversione",
      dash_compare_with:   "Confronta con",
      dash_advantage:      "vantaggio",
      dash_disadvantage:   "svantaggio",
      dash_z_explain:      "Valori in z-score (σ dalla media lega).",
      dash_winter_signing: "Acquisto invernale",

      /* dashboard — chip filtro metriche */
      dash_chip_tpi:       "TPI",
      dash_chip_prospect:  "Giovani ★",
      dash_chip_output:    "Output",
      dash_chip_cen:       "Centralità",
      dash_chip_boo:       "Boost",
      dash_chip_con:       "Consistenza",
      dash_chip_conv:      "G/xG",
      dash_btn_compare:    "Confronta",
      dash_search_np:      "Nome, squadra o ruolo…",
      dash_filter_by_team: "Filtra per squadra",
      /* dashboard — titoli metrica (heading leaderboard) */
      dash_m_tpi:          "TPI Totale",
      dash_m_prospect:     "Giovani ★ — Prospect Score",
      dash_m_out:          "Output Offensivo Adj / 90'",
      dash_m_cen:          "Centralità Offensiva",
      dash_m_boo:          "Team Boost Ratio",
      dash_m_con:          "Consistenza",
      dash_m_conv:         "G / xG — Conversion",
      /* dashboard — righe leaderboard / stati */
      dash_btn_profile:    "Profilo",
      dash_btn_diff:       "Scarto",
      dash_no_filter_data: "Nessun dato disponibile per questo filtro",
      dash_roster_note:    "giocatori (minuti insufficienti per TPI)",
      dash_off_profile:    "Profilo offensivo",
      dash_filter_hot:     "Caldi",
      dash_filter_cold:    "In calo",
      dash_filter_form:    "Filtra per forma:",
      dash_form:           "Forma",
      dash_form_hot:       "in forma",
      dash_form_cold:      "in calo",
      dash_form_stable:    "stabile",
      dash_goals_short:    "gol",
      dash_vs_season:      "vs stagione",
      dash_pro_badge:      "✨ Novità — TPI Pro",
      dash_pro_ttl:        "TPI Pro: 6 Dimensioni di Analisi",
      dash_pro_body:       "Il <strong>TPI classico</strong> usa 4 dimensioni offensive (output, centralità, boost, consistenza). Il <strong>TPI Pro</strong> aggiunge <span style=\"color:var(--teal)\">Età Index (AII)</span> e <span style=\"color:var(--purp)\">Affidabilità Fisica (PRI)</span> — due indici indipendenti che cambiano la valutazione per scouting a lungo termine.",
      dash_role_full_POR:  "Portiere",
      dash_role_full_DIF:  "Difensore",
      dash_role_full_CEN:  "Centrocampista",
      dash_role_full_ATT:  "Attaccante",

      /* footer condiviso */
      footer_private:      "Uso Privato"
    },

    en: {
      /* nav comune */
      nav_home:            "Homepage",
      nav_dashboard:       "Dashboard",
      nav_validation:      "Validation",
      nav_methodology:     "Methodology",
      nav_back_homepage:   "Back to Homepage",
      nav_back_ranking:    "Back to ranking",
      nav_back:            "Back",
      nav_forward:         "Forward",
      nav_lang_label:      "Language",

      /* azioni / pulsanti comuni */
      btn_search:          "Search",
      btn_close:           "Close",
      btn_compare:         "Compare",
      btn_methodology:     "Methodology",
      btn_explore:         "Explore dashboard",
      btn_see_validation:  "See validation",
      btn_read_method:     "Read methodology",

      /* placeholder / messaggi */
      ph_search_player:    "Search player…",
      msg_loading:         "Loading…",
      msg_no_data:         "No data available",
      msg_no_results:      "No results",

      /* termini dominio */
      term_players:        "Players",
      term_teams:          "Teams",
      term_ranking:        "Ranking",
      term_statistics:     "Statistics",
      term_minutes:        "Minutes",
      term_role:           "Role",
      term_team:           "Team",
      term_player:         "Player",
      term_home:           "Home",
      term_away:           "Away",
      term_vs_top6:        "vs Top 6",
      term_vs_strong:      "Strong Defenses",
      term_total:          "Total",

      /* HOMEPAGE */
      hp_eyebrow:          "⚽ Football Analytics · Serie A 25/26",
      hp_tagline:          "Data-driven Player Ranking Model",
      hp_intro:            "A model designed to evaluate and rank Serie A players using independent performance metrics — corrected for opponent difficulty, stabilized with Bayesian Shrinkage, validated against real outcomes.",
      hp_bullet_1:         "<strong>6 independent KPIs</strong> — Output, Centrality, Boost, Consistency (IQR-based), Age Impact Index (AII), Physical Reliability (PRI), standardized with <strong>winsorized z-scores</strong>",
      hp_bullet_2:         "<strong>406 players · 21 matchdays · 5 contexts</strong> — Total, Home, Away, vs Top 6, vs Strong Defenses",
      hp_bullet_3:         "<strong>Statistically validated</strong> — Predictive backtest Spearman ρ=0.70, 95% bootstrap confidence intervals, Kendall τ ranking stability, Cohen's d effect size",
      hp_tag_xg:           "xG · xA · SOS-weighting",
      hp_tag_bayes:        "Bayesian Shrinkage",
      hp_tag_pro:          "✨ TPI Pro — AII + PRI",
      hp_tag_validated:    "Statistically Validated",
      hp_whats_inside:     "What's inside",
      hp_card_dash_ttl:    "Scout Dashboard",
      hp_card_dash_body:   "Interactive player rankings across 7 metrics, squad filter, head-to-head comparison up to 4 players, TPI radar and differential analysis. Fully responsive.",
      hp_card_dash_lnk:    "Explore dashboard →",
      hp_card_val_ttl:     "Statistical Validation",
      hp_card_val_body:    "5 independent tests: Pearson r vs Fantacalcio, Top 10 Overlap, Predictive Backtest (r=0.70), AII/PRI validation and TPI vs TPI Pro consistency check.",
      hp_card_val_lnk:     "See validation →",
      hp_card_meth_ttl:    "Full Methodology",
      hp_card_meth_body:   "Every index explained with formulas, rationale and interactive charts. From raw data pipeline to final TPI — all steps documented.",
      hp_card_meth_lnk:    "Read methodology →",
      hp_idx_section:      "System indices",
      hp_idx_output_t:     "Output Adj / 90'",
      hp_idx_output_s:     "(xG+xA)/min×90 weighted by SOS — corrects for opponent strength",
      hp_idx_centr_t:      "Offensive Centrality",
      hp_idx_centr_s:      "% of team production through the player — with Bayesian Shrinkage",
      hp_idx_boost_t:      "Team Boost Ratio",
      hp_idx_boost_s:      "Team xG WITH / WITHOUT — true value to the team",
      hp_idx_cons_t:       "Consistency (IQR-based)",
      hp_idx_cons_s:       "1 − IQR/median — robust to outlier matches, bounded [0,1]",
      hp_idx_aii_t:        "⭐ AII — Age Impact Index",
      hp_idx_aii_s:        "Gaussian curve, peak at 27 — value in the career cycle",
      hp_idx_pri_t:        "💪 PRI — Physical Reliability",
      hp_idx_pri_s:        "Availability + injuries + severity — historical physical reliability",
      hp_pro_new:          "✨ New — TPI Pro",
      hp_pro_ttl:          "TPI Pro — 6 Analysis Dimensions",
      hp_pro_body:         "The classic TPI uses 4 offensive dimensions. TPI Pro adds <strong style=\"color:var(--teal)\">Age Impact Index (AII)</strong> and <strong style=\"color:var(--purp)\">Physical Reliability (PRI)</strong> for more accurate long-term scouting.",
      hp_footer_season:    "Season 2025/26",
      hp_footer_data:      "Data: FBref (Opta source) · Transfermarkt · SosFanta · PazzidiFanta",

      /* VALIDAZIONE */
      val_title:           "Model Validation",
      val_subtitle:        "Five independent tests confirming the TPI is statistically valid.",
      val_pearson:         "Pearson r vs Fantacalcio",
      val_overlap:         "Top 10 Overlap",
      val_backtest:        "Predictive Backtest",
      val_aii_validation:  "AII Validation",
      val_pri_validation:  "PRI Validation",
      val_tpi_pro_coh:     "TPI vs TPI Pro Coherence",
      val_interpretation:  "Interpretation",
      val_limits:          "Limits",
      val_low:             "Low",
      val_consistent:      "Consistent",
      val_notable_div:     "Notable divergences",
      val_no_data_pro:     "No TPI Pro data",
      val_start_mysql:     "Start MySQL for full backtest",
      val_injuries:        "Injuries",
      val_confidence:      "Confidence Score",
      val_rmse:            "RMSE",
      val_pro_players:     "TPI Pro Players",
      val_aii_players:     "Players with AII",
      val_pri_players:     "Players with PRI",

      /* GUIDA */
      guide_title:         "Complete Methodology Guide",
      guide_subtitle:      "Every index, formula and design choice of Serie A Scout Index",
      guide_chapter:       "Chapter",
      guide_formula:       "Formula",
      guide_how_calc:      "How it is calculated",
      guide_components:    "Formula components",
      guide_base_data:     "Base Data",
      guide_how_populate:  "How to populate the data",
      guide_age_curve:     "AII curve by age",
      guide_age_age_idx:   "Age Impact Index by age band",
      guide_age_band:      "Band",
      guide_aff_phys:      "Physical Reliability",
      guide_age_idx:       "Age Index",
      guide_centrality:    "Offensive Centrality",
      guide_consistency:   "Consistency",
      guide_form_ewma:     "Form EWMA",
      guide_big_match:     "Big match",
      guide_finisher:      "Above-average finisher",

      /* DASHBOARD */
      dash_title:          "Scout Dashboard",
      dash_filter_team:    "Team",
      dash_filter_role:    "Role",
      dash_all_teams:      "All",
      dash_all_roles:      "All",
      dash_role_gk:        "Goalkeeper",
      dash_role_def:       "Defender",
      dash_role_mid:       "Midfielder",
      dash_role_fwd:       "Forward",
      dash_role_gk_s:      "GK",
      dash_role_def_s:     "DEF",
      dash_role_mid_s:     "MID",
      dash_role_fwd_s:     "FWD",
      dash_leaderboard:    "Leaderboard",
      dash_compare:        "Compare",
      dash_compare_pool:   "Compare pool",
      dash_compare_empty:  "Add players to compare",
      dash_pick_player:    "Pick player",
      dash_roster:         "Rest of the squad",
      dash_insufficient:   "insufficient minutes for TPI",
      dash_diff_modal:     "Δ Differential",
      dash_radar:          "TPI Radar",
      dash_overview:       "Overview",
      dash_conversion:     "Conversion",
      dash_trend:          "Trend",
      dash_show_pro:       "Show TPI Pro",
      dash_hide_pro:       "Hide TPI Pro",
      dash_methodology:    "Methodology",
      dash_kpi_xg90:       "xG / 90'",
      dash_kpi_xa90:       "xA / 90'",
      dash_kpi_goal90:     "Goals / 90'",
      dash_kpi_sos:        "SOS",
      dash_kpi_finish:     "Finishing",
      dash_kpi_conv:       "Conversion rate",
      dash_compare_with:   "Compare with",
      dash_advantage:      "advantage",
      dash_disadvantage:   "disadvantage",
      dash_z_explain:      "Values in z-score (σ from league mean).",
      dash_winter_signing: "Winter signing",

      /* dashboard — metric filter chips */
      dash_chip_tpi:       "TPI",
      dash_chip_prospect:  "Young ★",
      dash_chip_output:    "Output",
      dash_chip_cen:       "Centrality",
      dash_chip_boo:       "Boost",
      dash_chip_con:       "Consistency",
      dash_chip_conv:      "G/xG",
      dash_btn_compare:    "Compare",
      dash_search_np:      "Name, team or role…",
      dash_filter_by_team: "Filter by team",
      /* dashboard — metric titles (leaderboard heading) */
      dash_m_tpi:          "Total TPI",
      dash_m_prospect:     "Young ★ — Prospect Score",
      dash_m_out:          "Adj Offensive Output / 90'",
      dash_m_cen:          "Offensive Centrality",
      dash_m_boo:          "Team Boost Ratio",
      dash_m_con:          "Consistency",
      dash_m_conv:         "G / xG — Conversion",
      /* dashboard — leaderboard rows / states */
      dash_btn_profile:    "Profile",
      dash_btn_diff:       "Gap",
      dash_no_filter_data: "No data available for this filter",
      dash_roster_note:    "players (insufficient minutes for TPI)",
      dash_off_profile:    "Offensive profile",
      dash_filter_hot:     "Hot",
      dash_filter_cold:    "Cold",
      dash_filter_form:    "Filter by form:",
      dash_form:           "Form",
      dash_form_hot:       "hot",
      dash_form_cold:      "cold",
      dash_form_stable:    "stable",
      dash_goals_short:    "goals",
      dash_vs_season:      "vs season",
      dash_pro_badge:      "✨ New — TPI Pro",
      dash_pro_ttl:        "TPI Pro: 6 Analysis Dimensions",
      dash_pro_body:       "The <strong>classic TPI</strong> uses 4 offensive dimensions (output, centrality, boost, consistency). <strong>TPI Pro</strong> adds <span style=\"color:var(--teal)\">Age Index (AII)</span> and <span style=\"color:var(--purp)\">Physical Reliability (PRI)</span> — two independent indices that reshape long-term scouting evaluation.",
      dash_role_full_POR:  "Goalkeeper",
      dash_role_full_DIF:  "Defender",
      dash_role_full_CEN:  "Midfielder",
      dash_role_full_ATT:  "Forward",

      /* footer condiviso */
      footer_private:      "Private use"
    }
  };

  /* ── STATE & API ────────────────────────────────────────── */
  const SUPPORTED = ["it", "en"];
  const DEFAULT_LANG = "it";

  function detectLang() {
    const stored = localStorage.getItem("lang");
    if (stored && SUPPORTED.includes(stored)) return stored;
    const nav = (navigator.language || navigator.userLanguage || "").toLowerCase();
    return nav.startsWith("it") ? "it" : "en";
  }

  let currentLang = detectLang();

  function t(key) {
    return I18N[currentLang]?.[key] ?? I18N[DEFAULT_LANG]?.[key] ?? key;
  }

  function getLang() { return currentLang; }

  function setLang(lang) {
    if (!SUPPORTED.includes(lang)) return;
    currentLang = lang;
    try { localStorage.setItem("lang", lang); } catch (e) {}
    document.documentElement.lang = lang;
    applyI18n(document);
    document.dispatchEvent(new CustomEvent("i18n:changed", { detail: { lang } }));
  }

  /* ── DOM HYDRATION ──────────────────────────────────────── */
  function applyI18n(root) {
    root = root || document;
    root.querySelectorAll("[data-i18n]").forEach(el => {
      const k = el.getAttribute("data-i18n");
      if (k) el.textContent = t(k);
    });
    root.querySelectorAll("[data-i18n-html]").forEach(el => {
      const k = el.getAttribute("data-i18n-html");
      if (k) el.innerHTML = t(k);
    });
    root.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const k = el.getAttribute("data-i18n-placeholder");
      if (k) el.setAttribute("placeholder", t(k));
    });
    root.querySelectorAll("[data-i18n-title]").forEach(el => {
      const k = el.getAttribute("data-i18n-title");
      if (k) el.setAttribute("title", t(k));
    });
    root.querySelectorAll("[data-i18n-aria-label]").forEach(el => {
      const k = el.getAttribute("data-i18n-aria-label");
      if (k) el.setAttribute("aria-label", t(k));
    });
    /* highlight switcher active button */
    document.querySelectorAll(".i18n-switch [data-set-lang]").forEach(b => {
      b.classList.toggle("active", b.getAttribute("data-set-lang") === currentLang);
    });
  }

  /* ── SWITCHER UI ────────────────────────────────────────── */
  function injectSwitcherStyles() {
    if (document.getElementById("i18n-style")) return;
    const css = `
      .i18n-switch{display:inline-flex;align-items:center;gap:0;
        border:1px solid rgba(255,255,255,.18);border-radius:8px;overflow:hidden;
        font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Helvetica Neue",sans-serif;
        background:rgba(255,255,255,.04);height:28px}
      .i18n-switch button{background:transparent;border:none;color:rgba(235,235,245,.55);
        font-size:11px;font-weight:700;letter-spacing:.6px;padding:0 9px;height:100%;
        cursor:pointer;transition:background .15s,color .15s;text-transform:uppercase}
      .i18n-switch button:hover{color:#fff;background:rgba(255,255,255,.06)}
      .i18n-switch button.active{color:#fff;background:rgba(10,132,255,.25)}
      .i18n-switch button + button{border-left:1px solid rgba(255,255,255,.10)}
    `;
    const s = document.createElement("style");
    s.id = "i18n-style"; s.textContent = css;
    document.head.appendChild(s);
  }

  function mountSwitcher(slot) {
    if (!slot) return;
    slot.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "i18n-switch";
    wrap.setAttribute("role", "group");
    wrap.setAttribute("aria-label", t("nav_lang_label"));
    SUPPORTED.forEach(code => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = code.toUpperCase();
      b.setAttribute("data-set-lang", code);
      if (code === currentLang) b.classList.add("active");
      b.addEventListener("click", () => setLang(code));
      wrap.appendChild(b);
    });
    slot.appendChild(wrap);
  }

  function mountAllSwitchers() {
    injectSwitcherStyles();
    document.querySelectorAll("[data-i18n-switcher]").forEach(mountSwitcher);
  }

  /* ── INIT ───────────────────────────────────────────────── */
  function init() {
    document.documentElement.lang = currentLang;
    mountAllSwitchers();
    applyI18n(document);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  /* expose public API */
  window.SerieAi18n = { t, setLang, getLang, applyI18n, mountAllSwitchers };
})();
