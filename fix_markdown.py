import re

with open("ScriptPulse_ A Deterministic Temporal Framework for Screenplay Narrative Diagnostics.md", "r") as f:
    text = f.read()

# Replace the equations by exact string matching because regex with those garbled characters is messy
replacements = {
    "X={x1,x2,...,xT}X \\= \\{x_1, x_2, ..., x_T\\}X={x1​,x2​,...,xT​}": "$$X = \\{x_1, x_2, ..., x_T\\}$$",
    "Interpretation=f(DeterministicDiagnostics)Interpretation \\= f(Deterministic Diagnostics)Interpretation=f(DeterministicDiagnostics)": "$$Interpretation = f(\\text{Deterministic Diagnostics})$$",
    "DMt=0.7SWt+0.3VtDM_t \\= 0.7SW_t + 0.3V_tDMt​=0.7SWt​+0.3Vt​": "$$DM_t = 0.7SW_t + 0.3V_t$$",
    "Et=0.05+0.9(0.85NDt+0.15SDt)E_t \\= 0.05 + 0.9(0.85ND_t + 0.15SD_t)Et​=0.05+0.9(0.85NDt​+0.15SDt​)": "$$E_t = 0.05 + 0.9(0.85ND_t + 0.15SD_t)$$",
    "Rt=(1−Et)βR_t \\= (1-E_t)^\\betaRt​=(1−Et​)β": "$$R_t = (1 - E_t)^\\beta$$",
    "St=λSt−1+Et−RtS_t \\= \\lambda S_{t-1} + E_t - R_tSt​=λSt−1​+Et​−Rt​": "$$S_t = \\lambda S_{t-1} + E_t - R_t$$",
    "S0=0.25S_0 \\= 0.25S0​=0.25": "$$S_0 = 0.25$$",
    "St∈[0.05,0.98]S_t \\in [0.05, 0.98]St​∈[0.05,0.98]": "$$S_t \\in [0.05, 0.98]$$",
    "Conf=(1−ps)(1−pv)(1−po)Conf \\= (1-p_s)(1-p_v)(1-p_o)Conf=(1−ps​)(1−pv​)(1−po​)": "$$Conf = (1-p_s)(1-p_v)(1-p_o)$$",
    "O(n+T)O(n + T)O(n+T)": "$$O(n + T)$$",
    "λ=0.82,β=0.35\\lambda \\= 0.82,\\quad \\beta \\= 0.35λ=0.82,β=0.35": "$$\\lambda = 0.82, \\quad \\beta = 0.35$$",
    "S≈0.18S \\approx 0.18S≈0.18": "$$S \\approx 0.18$$",
    "S≈0.65S \\approx 0.65S≈0.65": "$$S \\approx 0.65$$",
    "SWtSW_tSWt​": "$SW_t$",
    "VtV_tVt​": "$V_t$",
    "NDtND_tNDt​": "$ND_t$",
    "SDtSD_tSDt​": "$SD_t$",
    "β\\betaβ": "$\\beta$",
    "StS_tSt​": "$S_t$",
    "λ\\lambdaλ": "$\\lambda$",
    "psp_sps​": "$p_s$",
    "pvp_vpv​": "$p_v$",
    "pop_opo​": "$p_o$",
    "nnn": "$n$",
    "TTT": "$T$"
}

for old, new in replacements.items():
    text = text.replace(old, new)

# References
text = text.replace("[8]", "[6]")
text = text.replace("[6]", "[5]")
text = text.replace("[9]", "[7]")
text = text.replace("[10]", "[8]")
text = text.replace("[12]", "[10]")
text = text.replace("[4], [5], [13]", "[3], [4], [11]")
text = text.replace("[2], [11]", "[2], [9]")

refs = """[1] M. Jahn, *Narratology: A Guide to the Theory of Narrative*. University of Cologne, 2005.

[2] J. Qu, “A study of narrative structure and cognitive processes in English language and literature,” *Applied Mathematics and Nonlinear Sciences*, 2025.

[3] S. Min and J. Park, “Mapping out narrative structures and dynamics using networks and textual information,” 2016.

[4] L. Konle and F. Jannidis, “Modeling plots of narrative texts as temporal graphs,” 2022.

[5] P. Papalampidi et al., “Screenplay summarization using latent narrative structure,” ACL, 2020.

[6] A. Agarwal et al., “Parsing screenplays for extracting social networks from movies,” 2014.

[7] G. Bhat et al., “Hierarchical encoders for modeling and interpreting screenplays,” 2021.

[8] T. Alrashid and R. Gaizauskas, “Automatic segmentation of narrative text into scenes,” 2025.

[9] P. Vijayaraghavan and D. Roy, “M-SENSE,” AAAI, 2023.

[10] T. Goyal et al., “SNAC,” EMNLP, 2022.

[11] H. O. Hatzel and C. Biemann, “Story embeddings,” EMNLP, 2024."""

text = re.sub(r'# \*\*REFERENCES\*\*.*', f'# **REFERENCES**\n\n{refs}', text, flags=re.DOTALL)

with open("ScriptPulse_ A Deterministic Temporal Framework for Screenplay Narrative Diagnostics.md", "w") as f:
    f.write(text)
