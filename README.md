# Literature-Review-and-Automated-Information-Extraction-Using-LLM
## Background

As part of a Research Assistant (RA) project, we aim to systematically analyze labor-related papers published in top-tier economics journals. The goal is to extract structured information from these papers and organize it into a standardized dataset, which can support literature reviews, meta-analyses, and downstream empirical research.

This project focuses on automated information extraction from academic papers in the labor economics domain, with an emphasis on theoretical content, empirical design, data sources, and labor variable construction.

In practice, this lightweight tool is domain-agnostic and can be applied to academic research in virtually any field.


## Objectives

We aim to build a pipeline that extracts the following information from each paper:

**1. Basic Paper Metadata**

- Title

- Journal

- Abstract

- Authors

- Publication year

**2. Theoretical Content**

- Whether the paper contains a theoretical framework or model

- Extraction of the theory-related sections (if applicable)

**3. Empirical Content**

- Whether the paper is an empirical study

- Extraction of the data description section

**4. Data Origin**

- Whether the empirical data are sourced from the United States

**5. Data Level**

- Macroeconomic labor market data (e.g., aggregate employment, unemployment, wages)

- Firm-level or micro-level data (e.g., company-level employment, worker-firm matched data)

**6. Labor Variable Construction**

- Whether the paper constructs labor-related variables

- Extraction of labor variable definitions and construction methods

**7. Empirical Models**

- Extraction of the empirical models / econometric specifications used in the paper


## Motivation and Challenges

Directly calling large language models (LLMs) via APIs to parse PDFs and extract structured information has proven to be suboptimal. In contrast, web-based LLM interfaces typically apply advanced PDF preprocessing before passing content to the model, which significantly improves extraction quality.

This discrepancy motivates the development of a custom preprocessing pipeline that replicates (or approximates) the preprocessing quality of web-based LLM systems.


## Current Approach
We are experimenting with integrating MinerU, an open-source deep learning model for converting PDF files into machine-readable Markdown format.

MinerU enables:

- Improved preservation of document structure (sections, equations, tables)

- Cleaner input for downstream LLM-based information extraction

- Better alignment with academic paper layouts

- More details on MinerU can be found here:https://github.com/opendatalab/MinerU.git
