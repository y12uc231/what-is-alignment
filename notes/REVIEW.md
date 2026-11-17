# Review

After drafting, every section was audited sentence by sentence against the full texts of the sources it cites. Each sentence that says what a source did, found, claimed or defined was classified as supported, overreaching (true only with conditions that had been dropped, or stronger than the source), wrong, misattributed (the claim belongs to a different source or a later version of the source), or interpretation that needed to be labeled as ours, and every non-supported sentence was corrected in place. Every quotation was also checked in context, because a verbatim quotation can misrepresent a source when the sentence around it changes its meaning, and every case verdict was checked against the rules of [Section 1](../docs/01-first-principles.md) and against the verdicts of the same or similar events elsewhere in the repository.

## Counts

| Sections | Sentences checked | Corrected | Overreach | Wrong | Misattributed | Unlabeled interpretation | Other |
|---|---|---|---|---|---|---|---|
| 1, 8, 9 and the method note | 139 | 53 | 24 | 13 | 2 | 9 | 5 |
| 2 and 3 (plus 41 table rows and 20 timeline rows) | about 355 | 68 | 24 | 13 | 11 | 20 | 0 |
| 4 and 5 (plus 13 table rows) | about 530 | 42 | 23 | 17 | 1 | 1 | 0 |
| 6 | about 150 | 33 | 24 | 6 | 2 | 1 | 0 |
| 7 | about 190 | 56 | 29 | 6 | 8 | 4 | 9 |
| Total | about 1,360 | 252 | 124 | 55 | 24 | 35 | 14 |

"Other" covers open-problem claims that the corpus already partly answers (rescoped), positions quoted out of context, sources named without a citation, and one wording rule. All counts of sentences are approximate except for Sections 1, 8 and 9. In Section 8, every number was recomputed from `data/term_usage/` and the accepted-paper lists, and a second reading of 30 randomly chosen title labels agreed with 29 (the disagreement, a clinical-tutoring paper, lies between the preference-tuning and personalization senses and does not change any reported number).

## The kinds of error found

Most corrections restored conditions that a sentence had dropped. Examples: a sabotage rate reported without saying that it came from the prompt *without* an instruction to allow shutdown; a reward-tampering rate stated as below 1 in 1,000 trials when the source's bound of 1 in 1,000 applies only to tampering that also evaded detection, and tampering itself stayed below 1%; an "88%" chess-hacking figure that counts attempts of any kind rather than successful hacks; and the growth of a performance gap on safety-framed tasks that was measured during reinforcement learning, not in deployment.

Two sign errors were corrected. Ren et al. (2024) orient their benchmark scores so that higher means safer, so the reported −66.8% correlation between their sycophancy benchmark and capability means that sycophancy *worsens* as capability rises; two sections had stated the reverse.

Several attributions and dates were corrected. The phrase "intent alignment" does not occur in Christiano's 2018 post, which gave the definition; in the sources we hold the name first appears in 2020. The commonly quoted short form of Wiener's 1960 sentence keeps "cannot interfere effectively" and drops his reason (the machine acts too fast to intervene) and his closing clause. Three quotations had been dated to the first version of a paper when they appear only in a later revision. Two cases had been judged against the wrong developer's specification.

Some quotations were verbatim but misleading in context. The misuse debate is the main example: Ji et al. (2023) state both sides of the question, and Gabriel and Keeling (2025) call intent alignment "an important building block" rather than rejecting it, so both are now quoted with their qualifications.

## Changes to the framework

The audit also found places where the verdict rules were silent or inconsistent, and Section 1 was revised accordingly. Adversarial inputs are now presumed to be robustness failures unless the evidence shows the model recognized the input as prohibited. Every verdict names its principal, and harmful compliance is misuse relative to the user and, relative to the developer, an alignment failure only when the model recognized the request as prohibited. Covert principled disobedience is an alignment failure relative to the developer whatever its motive, whereas overt objection is judged against the developer's own specification, following the distinction that Anthropic's constitution and OpenAI's Model Spec both draw. Behaviors that researchers deliberately train in to study misalignment are model organisms, whereas researcher-run poisoning studies are laboratory analogues of security failures. Section 1.7's statement about scaling was narrowed to what the evidence shows: the best-documented growth of alignment failures is with optimization pressure within a training run, while the evidence on growth with capability across models is mixed. After these revisions, the verdict files were reconciled so that every event described by several sources has a single verdict.

## What could not be verified

A few claims rest on documents we could not read in full or on figures whose text did not extract cleanly, and the sections say so where they occur: three 2026 incident documents known only through Anthropic's August 2026 risk report or not read at all; one table in Meinke et al. (2024) whose values were checked against the case card rather than the extracted text; and which model produced one quoted chess transcript, which the paper does not say.
