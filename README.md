# Vanguard A/B Test: Did the New Digital Process Help Clients Finish?

An analysis of an A/B test run by **Vanguard**, a US investment management company, on a redesigned online process for its clients. We compared a **Control** group (old design) with a **Test** group (new design) to find out whether the new design led more clients to complete the process, and whether the improvement was large enough to be worth the cost.

**Team Hufflepuff:** Pariya, Pietro, Yurii · Ironhack Data Analytics Bootcamp, Module 2

- 📊 **Tableau dashboard:** [Tableau Public](https://public.tableau.com/app/profile/pariya.lakani/viz/vanguard_dashboard_final/vanguard_executive_dashboard)
- 📋 **Project board:** [Trello](https://trello.com/b/7HOtFWhm/hufflepuffteam)
- 🎤 **Presentation:** [Google Slides](https://docs.google.com/presentation/d/1qYbaWaDLsKi3lk0Xy46ItwtnvLfmSy2G/edit?usp=sharing&ouid=109599469251149380786&rtpof=true&sd=true)
- 🎈 **Streamlit App:** [Streamlit App](https://vanguardsproject.streamlit.app/)

---

## Business question

Between **March 15 and June 20, 2017**, Vanguard showed clients either the old or the new version of an online process with five steps:

`start → step_1 → step_2 → step_3 → confirm`

We wanted to answer:

1. **Who are the clients** using this online process?
2. **Did the new design work?** Did more clients reach `confirm`, finish faster, and make fewer errors?
3. **Is the improvement big enough?** Vanguard set a **5% minimum increase** in completion rate to justify the cost of the redesign.
4. **Was the experiment fair?** Were the Test and Control groups comparable, and did the test run long enough?

---

## Data

Three datasets provided for the project:

| Dataset | Content |
|---|---|
| `df_final_demo.txt` | Client demographics: age, gender, tenure, number of accounts, balance, calls and logons in the last 6 months |
| `df_final_experiment_clients.txt` | Which clients were in the Test or Control group |
| `df_final_web_data_pt_1.txt` + `pt_2.txt` | Every step each client took online, with a timestamp (two parts, combined into one) |

After cleaning, the analysis covers **50,488 clients** who took part in the experiment:
**Test 26,961 (53.4%)** and **Control 23,527 (46.6%)**.

---

## Key findings

### ✅ The new design increased completion
| Group | Completion rate |
|---|---|
| Control (old design) | **65.58%** |
| Test (new design) | **69.29%** |

The Test group's completion rate was **3.71 percentage points higher**. A **chi-square test** showed this difference is **statistically significant (p < 0.001)**, so it is very unlikely to be due to chance.

### ⚠️ But it did not reach Vanguard's 5% threshold
Reading the 5% target as **5 percentage points**, the Test group would need a completion rate of **70.58%**. With **69.29%**, the new design **does not meet the threshold**: the improvement is real, but smaller than what Vanguard set as worth the cost.

### ⏱️ Time per step: mostly faster
Clients in the Test group were **faster on `start`, `step_2` and `step_3`**, but **slower on `step_1` (+23.2%)**, which suggests that step may need more attention.

### ❌ More errors with the new design
We defined an error as a client **going back** to a previous step.
| Group | Error rate (backward steps per event) |
|---|---|
| Control | **6.90%** |
| Test | **9.25%** |

More clients finished with the new design, but more of them also went back along the way, so some parts of the new process may still be confusing.

### 🧪 Was the experiment fair?
- **Age, tenure and gender** were very similar in both groups, so the groups are comparable.
- **Balance** looked different on average because of a few very wealthy clients, so we used a **Mann-Whitney U test**: the typical (median) client was almost identical in both groups.
- The groups were **not split exactly 50/50** (53.4% vs 46.6%), which is worth keeping in mind, but with groups this large and this similar it does not change the main result.
- The Test group's advantage was **strongest early in the experiment** and had mostly disappeared from early May, so a longer test would help confirm the long-term effect.

### 👥 Who are the clients?
The typical client is **middle-aged (average age about 47)** and a **long-standing client**. More than half (**57.8%**) are between **35 and 64 years old**.

---

## Recommendations

1. **The new design helps**, but the gain is **below Vanguard's 5% target**, so the cost-benefit case is not yet strong enough on its own.
2. **Look closely at `step_1`**: it is where Test clients slowed down, and a good candidate for improvement.
3. **Investigate the higher error rate**: find which steps clients go back from most, and simplify them.
4. **Run the test longer**, or test an improved version, to check whether the advantage lasts beyond the first weeks.

---

## Methods & tools

- **Python:** pandas, numpy (cleaning, merging, KPIs)
- **Visualization:** matplotlib, seaborn, Tableau
- **Statistics:** scipy, statsmodels
  - Chi-square test of independence (completion rate, gender)
  - Chi-square goodness of fit (group split)
  - Welch's t-test (age, tenure)
  - Mann-Whitney U test (balance)
  - Two-proportion z-test (5% threshold)
- **Tools:** Jupyter Notebook, Git & GitHub, Trello (project planning)

---

| Notebooks | What they cover |
|---|---|
| 01 | Data cleaning and merging |
| 02–04 | Client behavior: overall profile, age, tenure |
| 05–07 | KPIs: completion rate, time per step, error rate |
| 08–10 | Hypothesis tests: completion rate, 5% threshold, effect by age |
| 11–12 | Experiment evaluation: group balance and experiment duration |

---

## How to run

```bash
git clone [repo-link]
cd a-b-test-analysis-vanguard
pip install -r requirements.txt
jupyter notebook
```
---

## Team

| Name | GitHub |
|---|---|
| Pariya | [pari14830](https://github.com/pari14830) |
| Pietro | [pietroguido90-design](https://github.com/pietroguido90-design) |
| Yurii | [yurii-slbv](https://github.com/yurii-slbv) |
