# Temprature with local ollama model
| temp | run | output |
|---|---|---|
| 0.0 | 1 | "Fueling your day, one circuit at a time." |
| 0.0 | 2 | "Fueling your day, one circuit at a time." |
| 0.0 | 3 | "Fueling your day, one circuit at a time." |
| 0.0 | 4 | "Fueling your day, one circuit at a time." |
| 0.0 | 5 | "Fueling your day, one circuit at a time." |
| 0.8 | 1 | "Fueling your day with precision and efficiency, one cup at a time." |
| 0.8 | 2 | "Fueling your day, one circuit at a time." |
| 0.8 | 3 | "Fueling your human experience with precision-crafted brews and calculated customer service." |
| 0.8 | 4 | "Fueling your day, one precision-crafted cup at a time, from the machines that make it happen." |
| 0.8 | 5 | "Brewed to perfection, calculated to perfection." |
| 1.5 | 1 | "At Gear & Grind, our robotic baristas will brew the perfect cup, every time, with precision and a hint of metallic charm." |
| 1.5 | 2 | "Brewed with precision, fueled by innovation: where every sip is a byte of perfection." |
| 1.5 | 3 | "Brewed with precision, served with a hint of synthetic charm." |
| 1.5 | 4 | "At Bionic Brew, we're always charging ahead with precision-crafted coffee and a side of metallic service." |
| 1.5 | 5 | "Brewed with precision, served with efficiency." |

# Observations
- At low temp(close to zero), with local LLM, the ouptut is same everytime, which I predict would be of the highest probability
- At T=0.8 ~ once it returned the most likely answer, other times somewhat similar and somewhat different answers
- At T=1.5, the model gave longer lined answers.

