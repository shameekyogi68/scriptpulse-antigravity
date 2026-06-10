**ScriptPulse: A Hybrid Deterministic Framework for Temporal Narrative Diagnostics in Screenplay Analysis**

| Shameek Yogi *Department of MCA* *Mangalore Institute of Technology and Engineering* *Karnataka, India* *2024mca079@mite.ac.in* | Rashmi M S *Department of MCA* *Mangalore Institute of Technology and Engineering* *Karnataka, India*  |
| :---: | :---: |

***Abstract*****—The field of automated screenplay analysis has generally focused on specific tasks such as parsing, summarization, and scene segmentation, which fail to take into account the holistic and time-dependent nature of storytelling and may lack robustness, repeatability, and interpretability. ScriptPulse represents a novel hybrid computational framework for temporal narrative diagnosis that integrates deterministic parsing, scene-based feature extraction, recursive temporal simulation, and structural agency diagnosis with confidence-calibrated governance. While the deterministic core of the system guarantees repeatability, a supplementary but optional bounded LLM layer allows for converting these diagnoses into human-interpretable reports. ScriptPulse evaluates proxies for the mathematical modeling of structural effort, dialogue momentum, recovery dynamics, and stakes distribution without the need to posit audience psychology and hence reproduces the development of screenplays. A proof-of-concept prototype in Python highlights the consistent temporal diagnostic abilities, narrative stakes analysis, and controlled interpretative reporting of the system. ScriptPulse provides a unified screenplay-specific architecture residing at the nexus of computational narratology, interpretable AI, and hybrid NLP applications.**

         ***Keywords—screenplay analysis, computational narratology, temporal narrative analysis, hybrid AI, interpretable AI, screenplay diagnostics.***

**I. INTRODUCTION**

Analysis and evaluations of the quality of pacing, escalation, consistencies in theme, and audience engagement in screenplays performed by experienced human experts in the film and television industry are also subjective processes, even though they are informative and useful. Manual evaluation is costly, time-consuming, subjective, and lacks reproducibility through computation. The lack of agreement on evaluative criteria among evaluators also poses a serious problem to manual evaluation of the screenplay. Computational narrative focuses on demonstrating the tractability of analyzing narrative structure. Structured temporal graphs, summary systems for scripts, and scene segmentation algorithms are just few of the research directions within the scope of computational narratives. Nevertheless, the vast majority of research work done in the field is still concentrated around particular NLP applications to the specific task rather than developing the comprehensive temporal diagnostic system.

Recently, there have been advancements in applying generative AI and large language models to screenplay evaluations. The major problem with such systems is that they use probabilistic inference algorithms which can easily be manipulated by prompt engineering and post-hoc rationalizations. Such systems provide no explanation about the basis of their analysis as they operate on probability distribution. Hence, they cannot be taken seriously as they are unreliable at best.

On the other hand, screenplays as structured narratives provide an opportunity for deterministic analysis. Compared to literary fiction narratives, the temporality of transitions between events in screenplays is very explicit due to the presence of Sluglines, Action, and Dialogue. Approaching screenplay analysis either scene-wise or holistically ignores its temporality property.

In order to address the above issues, we introduce ScriptPulse—a hybrid computational paradigm for the governed screenplay analysis that uses deterministic temporal structural diagnostics. As far as we know, no other screenplay system combines deterministic temporal diagnostic framework, governance-aware reliability mechanism, and bounded interpretive AI. ScriptPulse splits analysis into three separate, yet interconnected strict layers: deterministic calculations of screenplay structure, auxiliary semantics inferences, and bounded interpretive AI explanations.

Our contributions are as follows:

1) The first hybrid computational architecture for screenplay analysis tailored to temporal diagnostic tasks.

2) A deterministic proxy-based recursive temporal narrative progression model.

3) Governed confidence calibration and reliability controls.

4) Hybrid analysis pipeline with bounded interpretive AI explanations and its preservation of governance.

**II. RELATED WORK**

The related literature in the context of narrative analysis incorporates classic narratives, computational narrative analysis, screenplay-specific NLP research, and interpretable AI systems.

***A. Computational Narratology and Structural Narrative Analysis***

Humanities' previous literature provides evidence of narrative formal reasoning based on discourse layering and focalization \[1\], \[2\]. Moving from humanities to computer science, computational narratives further develop temporal and structural abstraction in narrative. This includes dynamic mapping of the narrative processes through evolving character networks and temporized graphs \[3\], \[4\]. From such developments, it can be concluded that narratives have some form of inherent topology that can be computationally abstracted.

However, most of the existing research specific to screenplays only considers isolated and highly specialized challenges within the field of NLP. In terms of recent advances, formal structure-based classification and automated screenplay parsing techniques have been developed \[5\]. Moreover, there have been efforts in the field of deep learning and narrative summarization through latent structures of plot twists \[6\] as well as hierarchical format encoding techniques \[7\]. Additionally, there have been advancements in semantic scene segmentation using transformers \[8\], \[9\].

Despite the aforementioned achievements, no system has yet addressed temporal diagnostics of narratives. By considering screenplays either unstructured textual data or focused solely on macro-level summarizations, they do not account for scene-wise escalations and decompression valleys that create the narrative's pace.

***B. Interpretable AI Systems and Their Governance***

The relevance of structure in the comprehension of cognitive narratives is evident in mental state modeling and protagonist goal tracking \[10\]. However, maintaining the integrity of complex systems requires reliable governance. The modular design and comparative studies in NLP have proved that hybrid AI models that combine interpretable and generative aspects outperform single-model designs that do not require any governance \[11\], \[12\].

By introducing severe risks associated with black-box unconstrained model feedback hallucinations, the need for deterministic governance grows more apparent \[11\], \[12\].

Thus, contemporary literature suffers from task-oriented specialization, probabilistic analytical volatility, and temporal framework gaps specifically for screenplays.

**III. RESEARCH GAP AND PROBLEM STATEMENT**

Upon examining existing approaches to screenplay analysis, there are various deficiencies observed. Firstly, many current approaches focus on solving disconnected analytics problems independently; for instance, the creation of a social network graph describing character interaction does not offer any information on scene timing dynamics. Secondly, narrative evolution is conventionally considered static rather than as a dynamic and cumulative process over time spanning effort, escalation, and decompression periods. Lastly, modern generative AI evaluation mechanisms sacrifice scientific replicability in favor of stochastic fluency, failing to incorporate governance-aware models for secure use.

The research problem can thus be defined as follows: What is the approach to representing screenplay narrative evolution as an explainable, replicable, and governance-aware computational process over time with bounded assistance by explanation-capable Artificial Intelligence?

The research gap can be resolved using the proposed deterministic hybrid screenplay diagnostics system.

*[Fig. 1: ScriptPulse Architecture — Six-stage pipeline: (1) Input & Governance, (2) Structural Parsing, (3) Scene Segmentation, (4) Feature Encoding, (5) Temporal Simulation + Agency Analysis, (6) Reliability Governance → optional Bounded LLM Interpretation.]*

**Fig. 1.**  ScriptPulse Architecture

**IV. PROPOSED FRAMEWORK ARCHITECTURE**

The ScriptPulse framework operates via hybrid governed computational paradigms. The framework translates screenplay inputs into deterministically reproducible temporal diagnostic outputs with deterministic analytical authority maintained throughout the pipeline. The processing pipeline includes screenplay input and governance validation, rule-based structural parsing, scene segmentation, feature encoding, temporal simulation, agency analysis, reliability governance, and interpretive reporting. The framework retains its determinism via strict governance over its hybrid semantic and interpretive modules.

***A. Input, Governance, and Structural Processing***

Input involves a governance layer prior to processing. This layer validates the proper file encoding, imposes constraints, and filters out malformed screenplays to prevent inappropriate analytical escalation from occurring. Next, structured rule-based structural parsing generates typed symbolic structures. Scene segmentation processes these structures into an analytical sequence of scenes, X \= {x₁, x₂, ..., xₜ}, where T denotes the number of unique scenes. The native sequence nature of this temporal information is critical to continuous analysis.

***B. Feature Encoding and Modality Mapping***

Features extracted are systematically mapped to discrete modality groups. Table I provides examples of the primary feature modalities and their analytical purposes.

**TABLE I Feature Categories in ScriptPulse**

| Feature Modality | Examples | Purpose |
| :---: | :---: | :---: |
| Dialogue | Speaker switches, velocity | Pacing |
| Structural | Density, entropy | Cognitive load estimation |
| Conflict | Escalation markers | Dramatic escalation |
| Stakes | Social, physical, moral | Thematic tension |
| Agency | Centrality, initiative | Agency |
| Semantic | Similarity, voice | Thematic analysis |

Prototype semantic enrichment utilizes zero-shot transformers and embedding similarity for auxiliary theme detection and voice characterization only, ensuring that primary structural calculations are unadulterated by probability-based variance.

***C. Temporal Simulation and Agency Analysis***

Temporal simulation functions as the analytical engine for ScriptPulse. Unlike static analyzers, ScriptPulse simulates narrative progression recursively through consecutive scenes, capturing escalation, persistence, and narrative decompression intrinsically.

Meanwhile, agency analysis assesses participation within the structure by analyzing narrative dialogue centrality and initiative, differentiating active plot participants from passive observers.

***D. Reliability and Interpretative Layers***

The framework automatically invokes reliability governance under mathematically unstable conditions (e.g., when insufficient token information prevents entropy calculation). Lastly, the framework may invoke an optional and bounded LLM to produce deterministic explanations for these deterministic diagnostic outputs. Mathematically, the interpretive layer is a function of the diagnostic layer, denoted as I \= f(D).

**V. MATHEMATICAL FORMULATION**

Through its focus on deterministic proxy formulations, ScriptPulse provides a tool for analyzing script development without resorting to unfounded assumptions about the psychological effects of film on audiences. The use of solely verifiable proxies ensures that analysis can be objectively reproduced. The heuristic weights assigned within the following proxy functions (e.g., 0.7 for speaker switches) were empirically tuned during initial testing on a baseline corpus of thrillers to maximize alignment with established structural turning points.

***A. Dialogue Momentum and Scene Narrative Effort***

Timing of dialogue is another significant structural consideration, particularly in terms of escalation and pacing. In a given scene, dialogue momentum (DM) is formulated as:

$$ DM = 0.7SW + 0.3V $$

where SW denotes the speaker switch frequency, and V denotes the dialogue velocity. This calculation is based on the assumption that frequent alternations between speakers indicate increased intensity within the scene.

Scene-level narrative effort (E), as an indicator of structural intensity, is defined as:

$$ E = 0.05 + 0.9(0.85ND + 0.15SD) $$

where ND denotes narrative drive, and SD denotes structural density.

$$ ND = 0.5C + 0.4S + 0.1A $$

is used as an estimate of structural conflict, narrative stakes, and affective emotional elements. Meanwhile:

$$ SD = 0.4RC + 0.6IE $$

uses referential complexity (RC) and Shannon information entropy (IE) to reflect the structural complexity of a scene. This is necessary because the information entropy model accounts for both character and location complexities.

***B. Recovery Model and Recursive Temporal State***

Narrative decompression (R), following high levels of effort, is estimated as:

$$ R = (1 - E)\beta $$

where β denotes the recovery constant, which depends on the genre and dictates the decay rate of narrative tension. Low β values produce less persistent decompression, while high β values facilitate greater recovery.

Temporal structural proxy state S at the scene level is generated recursively as:

$$ S_t = \lambda S_{t-1} + E - R \quad (1) $$

where λ denotes persistence. This recursion makes use of the boundary value condition of:

$$ S_0 = 0.25 $$

and imposes strict restrictions of:

$$ 0.05 \le S_t \le 0.98 $$

to avoid divergence.

**VI. METHODOLOGY AND IMPLEMENTATION**

The prototype implementation uses modular, governed analytical modules for deterministic diagnostics, semantic enrichment, and bounded interpretive reporting. The deterministic core computations are implemented in Python. The system design utilizes an interactive dashboard constructed using the Streamlit framework for visualization of temporal data. The additional module used for semantic enrichment uses HuggingFace Sentence Transformers (specifically the `jinaai/jina-embeddings-v2-small-en` model, 66 MB, supporting an 8,192-token context window) to derive contextual embeddings and compute thematic similarities. This model was selected over the smaller `all-MiniLM-L6-v2` due to its substantially longer context window, which allows full scene text to be encoded without truncation—a critical property for screenplay analysis where scenes can span several hundred tokens. The zero-shot classification module uses `MoritzLaurer/DeBERTa-v3-xsmall-mnli-alnli` (~140 MB) for stakes detection, sentiment categorization, and genre classification. Importantly, the interpretative module, powered by the Google Gemini API, is sandboxed strictly by the Python governance engine to avoid any hallucinatory deviations based on numerical proxies. This sandboxing is achieved by forcing the LLM to process strictly typed JSON schemas containing only the deterministic numerical data, preventing it from inventing narrative insights not present in the proxy state.

The custom screenplay parser parses screenplays according to standard formats and maps scenes hierarchically. Temporal recursive simulation module then computes proxy states for each scene hierarchically in time. Additionally, the reliability governance module monitors those computations to identify any mathematically unstable regions that can result in future hallucinations generated by the LLM layer. The core computational engine remains linear at O(n \+ T), where n is the number of lines in the screenplay; T is the length of the movie.

*[Fig. 2: Tension/Conflict Timeline — Attentional Signal (S_t) plotted against scene sequence (1–176) for The Godfather. X-axis: Scene index. Y-axis: Proxy state S_t ∈ [0.05, 0.98]. Three structural phases visible: gradual build-up (Scenes 1–30), escalation with sustained peaks (Scenes 85–90), and climax build-up with overload regions (Scenes 140–165).]*

**Fig. 2.**  Tension/Conflict Timeline Graph

*[Fig. 3: Stakes Distribution — Normalized donut chart for The Godfather (176 scenes). Social: 31.8%, Physical: 26.1%, Moral: 26.1%, Existential: 9.1%, Emotional: 6.8%. Dominant stakes profile matches the crime-drama genre expectation of social consequence and physical danger.]*

**Fig. 3.**  Stakes Distribution Donut Graph

**VII. RESULTS AND DISCUSSION**

A modular Python implementation of ScriptPulse was created as a prototype to test the architectural claims through analysis. The prototype analysis used the fully-formatted professional screenplay for *The Godfather*—an English crime-thriller selected for its well-established three-act structure and critical acclaim—containing exactly 176 scenes.

***A. Temporal Progression Trajectories***

As a result of the recursive temporal simulation, the analysis produced a unified macro-structural progression trajectory instead of isolated analyses per scene. The methodology helped to detect gradual progression, decompression periods, and structural turning-point estimations. Figure 2 illustrates the temporal tension and conflict build-up charted precisely by scene sequence.

We were able to discern three clearly-defined structural phases using the recursive proxy state approach. First, there is a deliberate build-up at the narrative setup stage (Scenes 1–30). Then, there was an escalation phase accompanied by sustained peaks in the dialogue momentum (Scenes 85–90). Lastly, the chart displayed sustained overload areas before progressing to the climax build-up (Scenes 140–165).

This specific progression trajectory underscores the ability of the proposed framework to map three-act paradigms into measurable data. As evident from our temporal progression model, there are dips in the proxy state after experiencing high dialogue momentum peaks, signifying the modeled decompression effect. In other words, deterministic progression modeling allows to make sense of progression diagnostics without resorting to the non-transparent black box approach to prediction.

***B. Stakes Distribution and Structural Agency***

Figure 3 represents the normalized stakes profile for the analyzed screenplay. The stakes detection algorithm detected a high proportion of social stakes (31.8%), balanced physical (26.1%) and moral stakes (26.1%), moderate existential stakes (9.1%), and low emotional stakes (6.8%). These stakes distribution parameters match the screenplay's genre profile where social consequence and physical danger prevail.

Moreover, the narrative agency analysis module enabled us to isolate disparities in structural narrative involvement by comparing active and passive narrative roles based on their conversational initiative combined with structural significance of each scene.

In this regard, the hybrid semantic enrichment module played the role of auxiliary analysis support, whereas the bounded LLM interpretation was responsible for translating the deterministic diagnostics results into a human-readable form.

***C. Comparative Positioning***

ScriptPulse proposes a unique architectural paradigm compared to the conventional approaches discussed above, which are summarized in Table II.

**TABLE II — Screenplay Analysis Approaches Comparison**

| Method | Temporal Modeling | Reproducibility | Interpretability | Governance |
| :---: | :---: | :---: | :---: | :---: |
| Static NLP Tools | ✗ No | High | High | None |
| Text Summarization | ✗ No | Medium | Low | None |
| Deep Neural Models | Partial | Low | ✗ Black-box | None |
| Generative AI (LLMs) | Partial | ✗ Non-deterministic | ✗ Opaque | None |
| *ScriptPulse (Proposed)* | ✓ Recursive scene-level | ✓ Deterministic core | ✓ Proxy-grounded | ✓ Confidence-calibrated |

*Note: ScriptPulse's primary limitation is reliance on proxy-based heuristics rather than empirically validated psychological models. The commercial product layer (v1.0) extends the research prototype with a scoring interface, persona-responsive dashboard, and LLM-generated coverage memos. This paper describes the deterministic research core.*

**VIII. LIMITATIONS**

Though powerful, ScriptPulse utilizes a deterministic structural proxy rather than an empirical model based on psychology of the audience. Hence, the state of temporal proxy in itself is just a deterministically computed state and does not guarantee any psychological impact on the human spectator at all.

Additionally, the parser depends on adherence to screenplay formatting standards, hence making it susceptible to errors in parsing. In fact, the mathematical models themselves incorporate heuristic values rather than empirically proven ones. Semantic enrichment modules themselves operate under limited probabilistic constraints and hence can be useful only for secondary interpretations. Lastly, there were no HCI tests conducted or expert readings validated within the scope of this project.

**IX. CONCLUSION**

We have introduced ScriptPulse, a hybrid-governed computational framework for temporal narrative diagnostics within screenplay documents. ScriptPulse effectively conceives cinematic screenplay creation as a deterministic, recursive temporal process, expanding traditional approaches by moving beyond linguistically grounded metrics and ungoverned LLM-generated comments.

Due to a separation of deterministic analytic governance from a probabilistic interpretation aid, the approach improves interpretability and reproducibility of results relative to purely machine learning-based approaches. The prototype implementation proves the technical feasibility of the deterministic governing architecture for screenplay diagnostics.

We provide a rigorous architectural framework for future research in computational narratology and intelligent hybrid narratives. In the immediate future, we will focus on embedding this architecture into the screenwriting software environment as a diagnostic tool as well as on empirical calibrating of our proxy formulations on large screenplay corpus. The source code and anonymized dataset for ScriptPulse will be made publicly available upon publication to ensure full reproducibility.

**REFERENCES.** 

\[1\]M. Jahn, Narratology: A Guide to the Theory of Narrative. Cologne, Germany: University of Cologne, 2005\.

\[2\]J. Qu, "A study of narrative structure and cognitive processes in English language and literature," Applied Mathematics and Nonlinear Sciences, vol. 10, no. 1, 2025\.

\[3\]S. Min and J. Park, "Mapping out narrative structures and dynamics using networks and textual information," arXiv preprint arXiv:1604.03029, 2016\.

\[4\]L. Konle and F. Jannidis, "Modeling plots of narrative texts as temporal graphs," in Proc. Computational Humanities Research Conference, 2022\.

\[5\]G. Agarwal, A. Balasubramanian, J. Zheng, and S. Dash, "Parsing screenplays for extracting social networks from movies," in Proc. CLFL Workshop, 2014\.

\[6\]P. Papalampidi, F. Keller, L. Frermann, and M. Lapata, "Screenplay summarization using latent narrative structure," in Proc. Association for Computational Linguistics (ACL), 2020\.

\[7\]G. Bhat, A. Saluja, M. Dye, and J. Florjanczyk, "Hierarchical encoders for modeling and interpreting screenplays," in Proc. Workshop on Narrative Understanding (WNU), 2021\.

\[8\]T. Alrashid and R. Gaizauskas, "Automatic segmentation of narrative text into scenes according to SceneML," in CEUR Workshop Proceedings, 2025\.

\[9\]D. Fried et al., "Learning temporal segmentation from narration and observation," in Proc. Association for Computational Linguistics (ACL), 2020\.

\[10\]P. Vijayaraghavan and D. Roy, "M-SENSE: Modeling narrative structure using protagonist mental representations," in Proc. AAAI Conference on Artificial Intelligence, 2023\.

\[11\]Z. C. Lipton, "The mythos of model interpretability," Queue, vol. 16, no. 3, pp. 31–57, 2018\.

\[12\]C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," Nature Machine Intelligence, vol. 1, no. 5, pp. 206–215, 2019\.

