REG-21 draft 5, round-3 adversarial review (rule F): NOT READY. Six required changes, all in the text; nothing the code computes has to change (one docstring repeats a wrong sentence). Of the seven round-2 items, five are fixed and two are partly fixed. The statistic, both batch guards and the new coverage rule do what the text says.

How I worked: synthetic inputs only. No run folder was opened or listed; `find_runs` was replaced at import in every script; `withheld.DECISIONS` pointed at a temp file; `docs/decisions.md` was not read. I changed nothing in the repo. The code reviewed is commit 69ffedd. HEAD moved to deb4f41 during the review (other sessions); `git diff 69ffedd HEAD` is empty for `analysis/k3w.py`, `tests/test_k3w.py`, `analysis/withheld.py` and every helper I read. `tests/test_k3w.py`: 31 pass (28 functions, 31 collected).

Scripts, all in `/private/tmp/claude-501/-Users-chalshik-Projects-aftershock-artifacts/8c5f8396-cce6-43e6-b8a1-890bcd5373c5/scratchpad/reg21_r3_scratch/`: `a_judge.py`, `b_busy_why.py`, `c_batches_seal.py`, `d_numbers_text.py`, `e_disagree_mc.py`, `f_pooled_between.py`. Line numbers of the registration are those of `registration_draft5.md`.

**1. Round-2 required items**

1. FIXED. `k3w.py:316` (only the groups J2 judged are pooled), 321–323; text line 40; `tests/test_k3w.py:233–238`. Script a (A6): a λ = 2.2 pair at 1.30 and 1.31 leaves the pooled median at 1.00 with 6 runs pooled. The pair still enters the reported slope (`k3w.py:307–308`); the text does not say so.
2. FIXED. Lines 47–53. One gap: the λ = 2.4 bound cites REG-12's five runs; the sixth judged 2.4 run (REG-11, seed 1) has no rate cited, although "every batch-1 run has been reported".
3. PARTLY. Both P(undefined) are there and right on their own inputs (script a, A12). The slope and P(J2 inside) still do not agree (section 3).
4. FIXED. (a) `k3w.py:319`, line 66, test at 241–245. (b) Line 69. (c) `k3w.py:383–388`, line 70, test at 382–396. Two new holes in the same table: traces A and B.
5. PARTLY. The reason "no waiting gauge in W" (`k3w.py:242–243`) and the coverage rule (`k3w.py:68, 121–123`) are done. The sentence on what the gauge counts carries a SOURCE tag, but one clause is wrong against the pinned source (section 3).
6. FIXED. `k3w.py:166–176`, used at 193 (stuck arm) and 147 (reference); test at 399–403. Script d (D4): 0.099 preemptions/s × 2996.9 ÷ 5164 = 0.0575.
7. FIXED. `k3w.py:357–364`; test at 368–369; line 24 names the two configs. Script c (C2): a missing or invalid id raises and names it.

**2. Traces on which a label comes out wrong**

A. The pooled J1 is either redundant or decided by how many runs each load has (scripts f, e, a).
- When J2 is inside, the pooled median always lies between the two group medians (0 exceptions in 24,007 random tables). When both judged groups have the same label and side, the pooled label is that label (17,783 of 17,783). So the pooled label says something new only when the two groups' labels differ.
- In that case the run counts decide it. With group medians 1.03 (λ = 2.0) and 1.07 (λ = 2.4), run SD 0.01:

  | runs at 2.0 | runs at 2.4 | P(pooled "inside") |
  |---|---|---|
  | 5 | 3 | 0.86 |
  | 5 | 5 | 0.46 |
  | 5 | 6 | 0.11 |
  | 4 | 6 | 0.02 |
  | 3 | 6 | 0.01 |

- Trace A1: 2.0 = {1.02, 1.03, 1.03, 1.04, 1.045}, 2.4 = {1.048, 1.06, 1.065, 1.07, 1.07, 1.08}. Produced: J2 inside (0.0375), pooled median 1.048 "inside", `all_judged_groups_inside` False, 2.4 group median 1.0675 "outside high". Line 64 then allows "at λ = 2.0 and 2.4 … within 0.05", which is false for 2.4. Right label: 2.0 inside, 2.4 outside high.
- Trace A2: REG-11's run (the sixth at 2.4, which the plan's list did not name) flips the label alone. Without it the pooled median is 1.0485, inside; with it at 1.07 the median is 1.052, outside high.
- Trace A3: same r values, two λ = 2.0 runs left out as idle: inside becomes outside high (pooled 1.06).
- The mirror case: pooled "outside high" at 1.052 while the 2.0 group is inside at 1.03. Line 67's "r times the token work" then misdescribes 2.0.
- How likely: this is the usual case on the text's own numbers. Script a (A11) takes r = published completion rate ÷ 1.681 × a second factor in 0.98–1.00, plus noise of SD 0.005–0.02 (BELIEF as to the noise; no run read). It gives P(J2 inside) 0.81–0.95 and P(pooled inside) 0.10–0.48. In 78–100 % of the "pooled inside" tables the 2.4 group is itself outside high.
- Smallest fix (text only; the group labels, sides and the flag are already computed): a pooled sentence is allowed only when every judged group's own J1 has the pooled label and side; otherwise the sentence is per load group, with median, n and side.

B. "Disagree" and "mixed" fire at the tolerance edge with no difference between the batches (script e).
- Batch 1's 2.0 group (5 runs) and batch 2 (3 or 5 runs) drawn from one distribution, run SD 0.011–0.02:

  | common level | P(labels differ) |
  |---|---|
  | 1.043 (median of the five known first factors) | 0.20–0.40 |
  | 1.032 | 0.003–0.13 |
  | 1.022 | 0.02 or less |

  The contrast is at or below 0.05 in at least 93 % of those cases (over 99 % at 1.043).
- Trace: batch 1's group at 1.049 (inside), batch 2 at 1.051 (outside high), contrast 0.002. By line 69 they "disagree", batch 2 "governs" and K3 says "mixed". Right reading: the batches agree to 0.002 and both sit at the tolerance.
- How likely: the text puts the 2.0 group "near 1.03" (1.024–1.043 by its own arithmetic), so roughly 0.05–0.25 (BELIEF).
- Smallest fix (text only, no new number): differing labels count as a disagreement only when the fixed-load contrast's size is above 0.05. Otherwise both medians are reported as "at the tolerance" and neither batch governs.

C. `busy_share` and the coverage rule (script b). No wrong label that I can reach on a valid run.
- As registered: a 10 s hole passes, 11 s gives "no waiting gauge in W"; a first value at W's start + 10 s passes, + 11 s does not; one scrape per 10 s passes (90 values), per 11 s does not. Exactly 0.99 is judged (891/900, 2376/2400, 3861/3900).
- NaN rows are dropped before the coverage test (`k3w.py:121`): a random 30 % NaN passes, 12 s of NaN in a row does not. Round 2's trace B is closed.
- Not monotone: a value 10 s before W and the next 1 s into W reads "not covered", while the same frame with nothing before W is covered (`load.py:154` keeps values up to 10 s outside W). It fails closed.
- Duplicate times count twice: 9 empty scrapes written twice turn 0.990 into 0.980. Shuffled or descending rows read "not covered".
- Sparse scrapes tighten the rule: with one scrape per 10 s, one empty scrape of 90 reads 0.9889, "idle".
- Can an idle server pass? Only with at most 1 % of scrapes empty. The lull server with 5.3 % empty reads r = 0.969, so at 0.99 the cost in r is below 0.01 (BELIEF, extrapolated). Gauge values missing exactly when the line is empty, in stretches of at most 10 s, would pass; a run that passed the recorder check cannot have them (`harness/checks.py:91–106`: no failed scrape, largest gap 2 s; BELIEF, no run read).
- The same lull trace (busy 0.947, r 0.969) is a low reading from idleness alone just under the 0.95 cut; a run just above it would enter the reported second table with a similar deficit. That table's "low" side is not interpretable.
- Can a saturated server fail? Yes, by design, if its line sits in the running set. Trap at 1.681 or 1.76 req/s, gauge set to requests at the server minus N_run, 16 configs:

  | N_run | result |
  |---|---|
  | 30 or 60 | all 16 read 1.00 |
  | 90 | λ 2.0 seed 2 reads 0.986 / 0.949; REG-19 config seed 19 reads 0.997 / 0.962 |
  | 140 | 7 or 8 of the 10 λ = 2.0 configs left out, no λ = 2.4 config |

  The text states this and gives a running set of about 30. Given that number I agree it should not bite.
- A draining server passes: all-miss at λ = 1.6 below μ = 1.681 reads busy 1.00, r 0.999 and is judged; Valse and Jannesari's slope part is False. That is right for J1, and line 62's wording rule covers it.

D. `_why` (script b, B6–B8; 48 states). Every state gets a right reason, with two trivial misses against line 32.
- "no work rate" is listed only when no other reason applies (`k3w.py:246`). A run with no ok request in W reads "no later turn in W" only.
- `left_out` carries no r (`k3w.py:295`); the r is in `rows`. A run that did not enter has no r at all.

E. `batch1_runs` (script c, C1–C2). Could not break it.
- 13 distinct ids, no glob character, none matching a seal pattern (likewise the five reference ids). So an id matches at most one folder and never a sealed one.
- Two folders for one id raise; a missing or invalid one raises; an exception inside `find_runs` propagates and prints no table.

F. `withheld.lifted` and `batch2_runs` (script c, C3–C4).
- Lifts the seal and should not:
  - an interim heading in result form (`[RESULT] REG-19, interim: …`);
  - a part result (`[RESULT] REG-19 seed-18 control rerun …`) or a withdrawal;
  - an id with a non-digit suffix (`REG-19b`, `REG-19-rerun`, `REG-19.1`; likewise `E1b`);
  - any line that begins `## <date> · [RESULT] REG-19` without being a heading, e.g. inside a code fence or in a pasted draft or review. The test is on lines, not headings (`withheld.py:46–47`). This review contains no such line.
- Does not lift and should (all fail closed): the id not first (`[RESULT] K1: REG-19's …`), a joint heading with REG-19 second, two spaces, a separator other than `·`, a date with a time.
- After an interim heading, `batch2_runs` returns seeds 15–17 and the one computation is spent. The only guard is line 94, a promise about REG-19's log.
- Seeds 15, 16, 18, 19 (a gap), a missing seed 15, or two valid runs of a seed all raise, as line 26 says. What happens next is not registered (required item 4).

G. `reg21_table(2)` and the contrast (script c, C5).
- Batch 1's 2.0-group median is identical in both tables.
- Fewer than 3 judged runs in batch 1's 2.0 group gives a NaN contrast; so does an undefined batch 2.
- No leak from the 0.95 table. With batch 2 undefined at 0.99 and "outside high" at 0.95, the top-level J1 stays undefined and the contrast NaN (`k3w.py:370, 386`). The nested table reuses the key names `J1`, `J2`; cosmetic.
- The contrast is not contained. If one of batch 1's folders is missing, or a batch-1 row raises, when batch 2 is computed, batch 2's whole table is lost (`k3w.py:384`).
- Batch 1's group label and side are not in batch 2's table.

H. `reference` (script c, C6).
- The containment hides nothing judged. U is computed outside the `try`: an ok request without a first token still stops the table; one without `t_end` gives `gauges_error` and the same mean.
- One failing gauge drops all reported values of that reference run, the busy share included (`k3w.py:147`, a single `update`).
- A pinned run that idled (U 3169, busy 0.32) is accepted and moves U_off from 5165 to 4765. This is as registered ("not held to the busy precondition"); the reported busy share is the only guard.

I. `_gauges` and the redo proxy (script d, D4).
- Arithmetic and units are right. The counter name is right (`vllm/v1/metrics/loggers.py:739`).
- It is NaN, with no message, when the counter is missing or goes down.
- It is an upper bound for the caching-on arm and close to the value for the caching-off arm, so equal proxies do not mean equal redone work. Alternative 1 says as much.

J. `vj_rule` (script d, D5).
- Need at the configured rate: 0.0199, 0.0324, 0.0449 sessions/s at λ = 2.0, 2.2, 2.4.
- `slope_part` and `trapped` use the realized need, which ranges 0.012–0.043 over seeds 2–6 at λ = 2.0. The text does not say which need gives the count of line 43.
- No code computes that count or calls `stats.cp_upper` (the function exists, `analysis/stats.py:9`).

**3. The text against the code and the numbers**

Sentences that are wrong or that the code does not do:
1. Line 30 and `k3w.py:17–19`: the gauge "is the scheduler's waiting queues without the deferred requests". The pinned source says the opposite for the gauge.
   - `Scheduler.make_stats` does subtract the deferred ones for the field `num_waiting_reqs` (`scheduler.py:2943–2948`).
   - `PrometheusStatLogger.record` adds them back before setting `vllm:num_requests_waiting` (`vllm/v1/metrics/loggers.py:1150–1154`). The series without them is `vllm:num_requests_waiting_by_reason{reason="capacity"}`.
   - So the gauge is `len(waiting) + len(kv_holding_waiting)`, deferred included. A preempted request with stale output is deferred (`scheduler.py:933–938`) and counted.
   - The clause that matters for the label is right: the running set is not counted (`scheduler.py:2610`). No label changes.
2. Line 32: "every reason that applies" and "their r is listed beside them" (trace D).
3. Line 79: "a readout that raises … does not stop the table". The fixed-load contrast can stop batch 2's table (trace G).
4. Line 91: "The command raises before" REG-19's final result. The code cannot tell a final heading from an interim one in result form; the sentence holds only through line 94.
5. Line 26: "a heading that only quotes those words lifts nothing". True for a heading with another tag first; a non-heading line that begins with the pattern lifts.
6. Minor:
   - FILE(analysis/k3w.py:55) is the id list; `batch1_runs` is at 357.
   - "U_off ÷ mean served prompt" (line 63) has no function.
   - The slope includes the 2.2 pair.

Numbers recomputed and right (script d):
- Windows [1680, 2580), [1680, 5580), [1680, 4080).
- 3072 = 2176 + 256 × 3.5; mean prompt = 3200 − 1024 × first-turn share.
- First factors 1.023–1.052 (median 1.043) at λ = 2.0 and 1.065–1.089 at 2.4; second factor 0.982–1.000 (0.993–0.995 at REG-17's share).
- Group medians 1.024–1.043 and 1.045–1.089; spread 0.022–0.046 with one second factor for both groups.
- −1.5 % and +0.4 %; 0.05 is a third of 0.15.
- 0.8 × 0.95 × 0.85 = 0.646; P(batch 2 undefined) 0.235 with five runs and 0.437 with four. With three runs it is 0.725, which the text does not give.
- Synthetic claims of line 19: r 0.9993 and 1.0004; batch of 16 or 64 0.9965–0.9997; think × 6 0.9996–0.9999; fixed cost 0.9924 and 0.9895; traps 1.100 and 0.922; the load-dependent server fails J2 at 0.077; 8 % redone in the reference reads 1.0795.
- 31 tests, and each "new since draft 4" item has one.

Numbers that do not agree with each other (lines 56–57, BELIEF in the text):
- "P(J2 outside) ≈ 0.35" against "0.02 to 0.04 between the groups, which agrees with that P". On the text's own arithmetic the spread's median is 0.034 and P(outside) is 0.05–0.19 (script a, A11). To reach 0.35 the difference of group medians needs an SD near 0.04–0.05, and r ≈ completion rate ÷ 1.681 × second factor is close to an identity.
- "λ = 2.4 inside ≈ 0.35" against "the λ = 2.4 group's near 1.05 to 1.08": the simulation gives 0.001–0.09.
- "P(J2 undefined) ≈ 0.02": independent runs at 0.92 give 0.005. The text's value is the cautious one; not wrong.

**4. Strongest alternative for each outcome**

- **J1 inside.** Any saturated engine with under 5 % reuse does about the cache-off token work, trap or not (trace C, the draining server). The backlog slope separates them and is reported. A second alternative is cancellation: dev mode or the day speeds the cold arm while redone prefill slows it. The pieces are named (alternatives 1 and 3), the cancellation is not.
- **J1 outside, high.** The reference pays for redone prefill and the cold arm re-hits its own freed blocks. Named, with the redo proxy, which bounds it and does not measure it. Not named: the arms also differ in `loadgen_force_close` (true in every burst config, absent in the sweep; script d, D1). It is client-side and unlikely to matter; E1 would show it.
- **J1 outside, low.** Named: redone prefill in the cold arm. Not named for this branch:
  - bookkeeping and eviction cost of a full pool with caching on, which the cache-off arm does not pay (step D's caching-off control would separate it);
  - up to 1 % idle time allowed by the precondition;
  - requests with a first token in W that never finish, which U leaves out.
- **J2 inside.** The tolerance is as wide as the expected difference, so "inside" was predictable (0.81–0.95 on the text's numbers). Named ("nearly fixed in advance").
- **J2 outside, a group outside.** Day. Named; nothing in batch 1 separates it. Not named: which runs pass the busy precondition differs by load (trace C, N_run 140).
- **J2 outside, every group inside.** Two groups on either side of 1, or the day. The branch also lets a model F prediction "at another load" carry the spread as its error. A spread between two loads that coincide with two days is no error bar for a third load.
- **Batch 2 against batch 1.** Both sit at the tolerance and the labels differ by noise (trace B). Not named.
- **Contrast above 0.05.** Day or window, both named. Not named: other seeds, and selection (busy over 2400 s and cold at 4080 s are stricter filters). The readout that separates window from day is batch 2's r over its first 900 s of W. It is not registered, and line 93 forbids adding it later.

**5. Decisions, and whether it should run**

- Every outcome changes only a ceiling on wording; the registration says so (line 61). Two outcomes could later change a claim: J2 outside with a group outside (no model F prediction at other loads), and J1 low (a proposal for C2's condition 4).
- On the text's own numbers batch 1 is close to decided: J2 inside, and the pooled J1 a coin flip that the lowest λ = 2.4 run settles. Its value is in the reported readouts (per-run r, both arms' gauges and redo proxy), not in its labels.
- "One judged item on unread data and one retrospective reading" is fair, with two caveats. Batch 2's J1 is undefined with probability 0.24–0.44 (0.73 with three runs). And it is strongly predicted by batch 1's same-load group, so it mostly measures drift between days.
- Still claiming more than the data carry: line 64 (trace A), line 69's "mixed" (trace B), and line 66's error bar for another load.
- Should it run: yes, at 0 GPU hours, after the changes below.

**6. Verdict: NOT READY**

Required. It is READY when these six are done; 1–5 are text only.
1. Lines 64 and 67: allow a pooled sentence only when every judged group's own J1 has the pooled label and side; otherwise give the sentence per load group (trace A).
2. Line 69: count differing labels as a disagreement, and K3 as "mixed", only when the contrast's size is above 0.05; otherwise report both medians as "at the tolerance" (trace B).
3. Line 30 and the docstring at `k3w.py:17–19`: say the gauge is the waiting queues with the deferred requests included, and cite `PrometheusStatLogger.record`.
4. Line 26 or 93: register now what happens when batch 2 raises on a gap or on two valid runs of a seed. Either batch 2 is then not computed, or a fixed rule picks the runs. "The cause is fixed" would otherwise be a choice of runs made after REG-19's outcomes are public. The bundle's delegation note names a REG-19 rerun, so this is reachable.
5. Lines 56–57: change P(J2 outside) and P(λ = 2.4 group inside) to what the text's own bounds give, or state the extra spread they assume and its source; strike "agrees with that P" unless shown.
6. Make three sentences exact, in text or code:
   - line 32 ("every reason", "their r beside them");
   - line 79 (the contrast is not contained);
   - line 91 (the code cannot tell an interim heading; line 94 is the guard).

Optional:
- Register now, reported only, batch 2's r (and REG-15's) over the first 900 s of W. It cannot be added later.
- Contain the contrast in a `try`, and put batch 1's group label and side into it.
- Report the midpoint of the two group medians beside the pooled median.
- Say that the 0.95 table carries no wording and that near 0.95 idleness alone moves r by about 0.03.
- Tighten `lifted`: no letter, dot or dash after the id, and skip fenced lines. Have batch 2 need all five seeds or a "final" marker.
- Line 66: drop "at another load" or limit it to 2.0–2.4.
- Name `loadgen_force_close` among the arm differences.
- Say the slope includes the 2.2 pair, and which need gives the count of line 43.
- Say where 10 s comes from; the registered scrape-gap limit is 2 s.
- Compute the reference's contained values one by one.
- Cite REG-11's known rate in "What was known".
- Have the command refuse to run when `analysis/` or `tests/` is dirty.

**7. What I could not check**

- Any real run: `k1.cold_backlogged`, the gauges and `cached_tokens` on real frames; whether an ok request ever lacks a first token (it would stop the table); whether the 13 + 5 folders exist; "`ls runs`, names only".
- Anything in `docs/` outside the bundle:
  - the published rates and shares the bounds rest on;
  - the cited lines of `experiment-plan.md` and `claims.md`;
  - REG-19's run order;
  - "has not been computed by anyone";
  - whether `decisions.md` already holds a line that lifts REG-19's seal under the new test. One command answers this without showing content: `withheld.lifted('[RESULT] REG-19')` must print False.
- vLLM: I read `get_request_counts`, `make_stats`, `PrometheusStatLogger.record`, `_preempt_request` and the deferral sites. I did not trace how the client's `cached_tokens` is filled for a preempted request beyond `scheduler.py:1074–1081` (first prefill only), nor async scheduling.
- Not run: `tests/test_withheld.py` (it reads the real `decisions.md` and the run inventory) and the full `uv run pytest` (`check_docs` reads the docs).
- `analysis/e1.py:241` waits for a `[RESULT] REG-21` heading, which batch 1's result alone would satisfy. Seen in a grep only; outside the bundle.
- Older runs were checked by older versions of `harness/checks.py`. That their scrape gaps are at most 2 s is a BELIEF.
