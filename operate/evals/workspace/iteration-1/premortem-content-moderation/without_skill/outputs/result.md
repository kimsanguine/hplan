# Pre-Mortem: Content Moderation Agent at 50k Posts/Day

## False Positives (Over-removal)

**High probability**
- Satire, irony, and sarcasm flagged as genuine harmful content
- Counter-speech ("hate speech is wrong because X") triggers same classifiers as the speech itself
- Medical/educational content about drugs, self-harm, or violence removed
- Non-English and code-switching text misclassified due to thin training data
- Reclaimed slurs used by in-group members (LGBTQ+, racial communities) removed

**Cascading effects**
- Users lose appeal trust after repeated false removals → churn
- Creators with borderline-but-legitimate content self-censor or leave
- Suppressed content creates "shadow banning" perception even if unintentional

---

## False Negatives (Under-removal)

**High probability**
- Adversarial evasion: deliberate misspellings, unicode substitution, image text, memes
- Coordinated inauthentic behavior that looks organic post-by-post
- Dog whistles and in-group coded language the model was never trained on
- Novel slurs or emerging harassment campaigns (model has a knowledge cutoff)
- Harassment through benign-seeming content ("nice post" repeated 500 times)

**Cascading effects**
- One viral harmful post at 50k/day scale can reach tens of thousands before removal
- Victims notice the failure publicly; brand damage is asymmetric to the actual rate

---

## Bias

| Dimension | Risk |
|---|---|
| Language | Worse performance on AAVE, dialects, non-English — disparate removal rates |
| Topic | Political asymmetry if training data skews ideologically |
| User type | New accounts or low-follower users may face stricter treatment (no context signal) |
| Content type | Text-only model misses image/video harm; multimodal adds its own blind spots |
| Geography | Content norms vary by country; a single model will over-moderate some cultures |

The core problem: **bias is invisible until you measure it deliberately.** Add demographic breakdowns to your precision/recall metrics before launch.

---

## Edge Cases

- **Quotes**: "The attacker said [slur]" — journalistic reporting on hate speech
- **Fiction**: Violence in creative writing, war novels, horror
- **Context collapse**: A policy debate screenshot of hateful text, posted to criticize it
- **Timestamps**: Breaking news events where posts reference violence accurately
- **Platform-native context**: Inside jokes, community memes that look hostile externally
- **Multi-post context**: Post 1 is benign, post 2 is benign, together they're harassment
- **Deleted context**: Reply to a removed post looks incoherent or suspicious without the original
- **Batch spikes**: Flash events (news, sports, live shows) generate 10x normal volume; latency increases, decisions degrade

---

## Regulatory Risk

**Immediate**
- **EU DSA** (Digital Services Act): Requires transparency reports, user appeal mechanisms, and human review for impactful decisions. A fully automated agent without appeals likely violates this.
- **GDPR / data residency**: If the model logs post content for retraining, you need lawful basis and data minimization controls.

**Near-term**
- **US state laws** (Texas HB 20, NetChoice litigation): Some laws restrict platforms from removing political speech — your moderation decisions may be litigated.
- **Child safety (CSAM)**: Mandatory reporting obligations in most jurisdictions. If your agent encounters this, it must trigger a legal workflow, not just a deletion.

**Structural**
- No audit trail → you cannot defend a removal decision if sued or investigated
- Fully automated consequential decisions on EU users may trigger **Article 22 GDPR** (right to explanation + human review)

---

## Operational / Systemic Risks

- **Model drift**: Language evolves; model quality degrades silently over weeks without a feedback loop
- **No human-in-the-loop**: At 50k/day, even 1% false positive = 500 wrongly actioned users/day
- **Appeal queue underestimated**: Users will appeal. If the queue isn't staffed, SLAs slip and legal exposure grows.
- **Single point of failure**: If the agent goes down or bugs out, what's the fallback? Zero moderation or zero posting?
- **Threshold tuning pressure**: Under-moderation gets press coverage → team tightens thresholds → over-moderation increases → repeat

---

## Recommendations Before Launch

1. **Stratified accuracy metrics** by language, content type, and user demographic — not just aggregate precision/recall
2. **Human review queue** for high-confidence removals that affect account standing (not just post removal)
3. **Mandatory appeal path** with SLA — legally required in EU, good practice everywhere
4. **Shadow mode first**: Run the agent in log-only mode for 1–2 weeks; measure what it *would* have done against human decisions
5. **Circuit breaker**: If removal rate spikes above X% in a time window, pause and alert humans
6. **Audit log**: Every decision, confidence score, model version, and timestamp — immutable, retained per your jurisdiction's requirements
7. **Legal review**: DSA compliance checklist before go-live, not after

The failure mode most likely to cause serious harm isn't the model — it's launching without the surrounding infrastructure (appeals, auditing, human escalation) that makes the model's errors recoverable.
