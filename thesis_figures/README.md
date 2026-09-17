# Figure vettoriali per la tesi

Il pacchetto contiene sei figure coerenti tra loro, disponibili in tre forme:

- `pdf/`: versione vettoriale pronta per `\includegraphics`;
- `svg/`: sorgente vettoriale modificabile con Inkscape o Illustrator;
- `latex/`: versione nativa TikZ/PGFPlots modificabile direttamente in LaTeX.

I CSV in `data/` rendono espliciti i dati usati e distinguono i valori esatti del dashboard dalle letture approssimate dei grafici.

## Preambolo LaTeX

```latex
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta,positioning,calc,decorations.pathreplacing}
```

## Inserimento consigliato dei PDF

```latex
\begin{figure}[tb]
  \centering
  \includegraphics[width=0.95\linewidth]{figures/tpm-saturation.pdf}
  \caption{Crescita del consumo di token al minuto in funzione del numero di richieste. Con il picco osservato di 263.900 token per richiesta, il limite di 4 milioni di TPM viene raggiunto a circa 15,2 richieste al minuto.}
  \label{fig:tpm-saturation}
\end{figure}
```

## Inserimento della versione TikZ/PGFPlots

```latex
\begin{figure}[tb]
  \centering
  \input{figures/latex/tpm-saturation.tex}
  \caption{Crescita del consumo di token al minuto.}
  \label{fig:tpm-saturation}
\end{figure}
```

## Figure e didascalie suggerite

1. `quota-utilization` — Utilizzo massimo osservato delle quote RPM, TPM e RPD. La scala logaritmica rende confrontabili valori compresi tra 0,0033% e 6,60%.
2. `token-profile` — Token di input e output nelle due sessioni di prova. I valori sono approssimati dalla lettura dei grafici AI Studio e non devono essere presentati come misure puntuali.
3. `tpm-saturation` — Modello di saturazione TPM ottenuto dal picco di 263.900 token per richiesta.
4. `current-architecture` — Architettura attuale e origine del collo di bottiglia dovuto all'invio quasi integrale del corpus.
5. `proposed-architecture` — Architettura proposta con retrieval selettivo, sessioni isolate, rate limiting e telemetria.
6. `latency-decomposition` — Punti di misura necessari per scomporre la latenza end-to-end senza introdurre stime non osservate.

## Nota metodologica

I valori RPM, TPM e RPD provengono direttamente dal riepilogo AI Studio. I token delle singole giornate sono invece stime grafiche. La figura sulla latenza non contiene valori numerici perché il progetto non registra ancora tempi p50, p95 o p99.

Per rigenerare SVG, HTML e CSV:

```powershell
node thesis_figures/generate_figures.mjs
```

