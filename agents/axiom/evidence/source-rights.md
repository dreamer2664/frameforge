# Source, rights and claim ledger — “How Old Is the Earth? Three clocks that had to be broken”

Revision r01. Every factual narration cue is listed with what it claims, the source(s) behind
it, and how certain the claim is. Sources were read on 2026-10-15. **Nothing in the film is
attributed to a person who did not say or do it, no quote is invented, and no experiment result
is fabricated.**

Key to status: **[F]** fact/easily verified · **[P]** primary or institutional source ·
**[D]** debated/qualified in the film itself · **[X]** explicitly fictionalised illustration.

## Media, fonts and tools (rights)

| Asset | Origin | Licence / rights position |
|---|---|---|
| Reference film (study only) | YouTube `XVQdhpwO75g`, retrieved with yt-dlp | Third-party copyrighted work. Kept in local cache (`agents/axiom/work/ref/`), never committed, never re-published. Not a source of any frame in my film. |
| Playpen Sans, Public Sans, Patrick Hand, Patrick Hand SC, Caveat | `github.com/google/fonts` (OFL) | SIL Open Font License 1.1; licence texts stored at `agents/axiom/assets/fonts/OFL-*.txt`. Bundling in a video is permitted, including commercial use. |
| Narration voice | `kokoro-onnx 0.6.1` runtime (MIT, thewh1teagle/kokoro-onnx) + **Kokoro-82M** model (Apache-2.0, hexgrad) | Synthetic voice `am_michael`; explicitly **not** a clone of any real person's voice. Engine/model versions and model SHA receipts: `~/.cache/frameforge/voice-models/source-receipts.json`. |
| Music and sound effects | Written for this film in `tools/mix_audio.py` (numpy: additive pads, seeded plucks, noise/whoosh/clink/paper) | Original synthesis by axiom; no sample library, no third-party recording, nothing to clear. |
| All drawings, characters, props, diagrams, type treatment | Written for this film in `film/` (Pillow/FreeType primitives) | Original work by axiom. Characters are respectful caricatures built from documented period dress — **not** likenesses of living people, no endorsement implied, no celebrity faces pasted. |
| FFmpeg 7.0.2 static build | `johnvansickle.com/ffmpeg/releases` (installed locally by `ops/bootstrap_media.py`) | GPL build used as a local tool; binary is not redistributed with the film. |

## Claim ledger (cue → claim → source → status)

### Chapter 1 — A date in the margin
- **1.1** Ussher published *Annales Veteris Testamenti* in 1650, a year-by-year chronology from creation; roughly 2,000 pages of Latin over ~20 years. Sources: Linda Hall Library, “Scientist of the Day – James Ussher” (2025); Famous-trials, “Bishop James Ussher Sets the Date for Creation”; celebratesalvation.org PDF on Ussher. **[P][F]**
- **1.2** The date on the first page: the night before **23 October 4004 BC** (Julian). Ussher's own words: “…occurred at the beginning of the night which preceded the 23rd of October in the year 710 of the Julian period”, with 4004 BC in the margin. Sources: Linda Hall Library; Famous-trials. **[P][F]**
- **1.3** From 1701 the date was printed in the margins of English (King James) Bibles and stayed there for centuries. Source: Linda Hall Library (“beginning in 1701, all editions of the King James Bible included 4004 BC in the margin at the beginning of Genesis”). **[P][F]**
- **1.4** Ussher was a serious, careful scholar using the best evidence available; his *Annales* used the Bible for only a fraction of its content. Sources: Linda Hall Library (explicitly rejecting the “blind religious recalcitrance” caricature); Ussher-Lightfoot Calendar entry (estimates the Bible underpins about a sixth of the *Annales*). **[P][F]**
- **1.5** The film's interpretation: the assumption, not the arithmetic, is the problem. This is **narrative argument**, labelled as such, not a source claim. **[X]**
- **1.6** Structural promise of the film. **[X]**

### Chapter 2 — Ussher's clock
- **2.2** The raw material is the genealogical list in Genesis, with recorded lifespans such as Adam 930 years and Seth 912 years. Source: Genesis 5:5 and 5:8 (the film treats these as *the text's* numbers, not as history). **[P][F]**
- **2.3** If the list is continuous, summing it yields time, but an external anchor is required. **Method description** of Ussher's approach; sources: AcademiaKids “Ussher–Lightfoot Calendar” (methodology section); Christianity Stack Exchange answer summarising Ussher's method. **[F]**
- **2.4** Ussher anchored his chronology using Babylonian/regnal evidence (the death of Nebuchadnezzar, 562 BC, is the anchor the film names) and counted backwards. Sources: Famous-trials (“Ussher tied the date of Nebuchadnezzar's death (562 B.C.) to the modern Julian calendar… then added 562 years to the 3,442 years of Old Testament generations”); creation.com appendix B. **Status: [D]** — the literature differs slightly on which regnal datum is used, so the film says “chose the death of Nebuchadnezzar… which he could connect to surviving records” rather than claiming an exact verse.
- **2.5** Ussher argued creation occurred at the autumn equinox/harvest, partly because the Jewish year begins then. Sources: Famous-trials (quote from Ussher about the Sunday nearest the autumnal equinox); Christianity Stack Exchange (season debate). **[P][F]**
- **2.6** Result: the night before 23 October 4004 BC. As 1.2. **[P][F]**
- **2.7** The famous “9 a.m.” is **not** Ussher's. It comes from John Lightfoot (1642): “Man created by the Trinity about the third hour of the day, or nine of the clock in the morning”, and Lightfoot's own chronology is a different year (3928/3929 BC). Sources: Grand Lodge of British Columbia page on Lightfoot (documents the misquotation by A. D. White); AcademiaKids Ussher–Lightfoot Calendar. **[P][D]** — the film says only “a different scholar, working from a different calculation”, which is exactly what the sources support.

### Chapter 3 — The world did not fit
- **3.2–3.3** Egyptian king lists and Chinese records appeared to reach back beyond the date, creating pressure on a 6,000-year chronology. This is presented as **pressure**, not as settled ancient chronology: the film's wording is “seemed to reach back further”. Context: Egyptology's king lists (Manetho, the Turin papyrus) and early Chinese dynastic records were the standard early-modern problem cases in chronologies of the world. **[D]**
- **3.4** Fossils in mountains, especially marine shells and layered strata, demanded vast time; a widely used early answer was a global flood. Standard history of geology; framed in the film as a historical argument, not as a claim about the flood itself. **[D]**
- **3.5–3.6** The flood explanation has to compress geology into one year, and the rocks “do not look like they were in a hurry” — the film's own formulation of the stratigraphic objection. **[X]**
- **3.7** Pivot question posed by the film. **[X]**

### Chapter 4 — The clock in the rock
- **4.2** Hutton visited Siccar Point in 1788 by boat with Sir James Hall and John Playfair. Source: BBC Travel, “Walk the Scottish coast that changed science” (2026, Hutton's 300th-anniversary feature). **[P][F]**
- **4.4, 4.6** The geometry: near-vertical grey greywacke beds overlain, across an erosion surface, by shallow red sandstone — read in order as deposit → fold/lift → erode → re-deposit. Source: BBC Travel; mshtanks.com field notes on Siccar Point. Standard geology. **[P][F]**
- **4.8** Hutton: “we find no vestige of a beginning, no prospect of an end” — *Theory of the Earth*, read to the Royal Society of Edinburgh, 1788. Sources: BBC Travel; mshtanks.com; multiple geology teaching sources. **[P][F]** Quote verified verbatim in the sources above.
- **4.9** Playfair (written later, remembering the trip): “The mind seemed to grow giddy by looking so far into the abyss of time.” Sources: BBC Travel; richmond.edu word-of-the-week piece; earthlearningidea PDF. **[P][F]** The film states this is a memory, written years later, rather than a live remark.
- **4.10–4.11** The film's argument: Hutton establishes depth, not duration. **Interpretation**, marked as such. **[X]**

### Chapter 5 — Kelvin's cooling clock
- **5.2–5.5** William Thomson (Lord Kelvin) modelled the Earth as a body cooling by conduction, used measured thermal gradients and conductivity, and in **1862** published an age of roughly **100 million years**, later narrowing to **20–40 million** (1897). Sources: Wikipedia “Age of Earth” (20–400 Ma in 1862; “more than 20 and less than 40 million… probably much nearer 20” in 1897); National Geographic Education; paos.colorado.edu lecture notes (98 Ma in 1862; 20–40 Ma in 1897). **Status: [F]**, with the film saying “something like a hundred million years” rather than a false precision.
- **5.6** The same reasoning applied to the Sun gave tens of millions of years of sunlight. Source: paos.colorado.edu historical summary; Braterman blog on the 1904 Royal Institution lecture (notes Kelvin's solar constraint). **[F]**
- **5.7** This was bad news for geology and for Darwin, who needed long timescales. Darwins' concern with Thomson's calculations is standard history (Darwin's letters of the late 1860s). The film phrases it as a general consequence, not as a quotation. **[F]**
- **5.8** The film's fairness argument — Kelvin was applying trusted physics rigorously. **Interpretation**, supported by Dalrymple's and England et al.'s descriptions of Kelvin's authority and rigour. **[X]**

### Chapter 6 — The heat inside
- **6.2–6.3** In **1895** John Perry argued that a hot, partly fluid interior would transport heat by **convection**, not conduction, invalidating Kelvin's assumption. Primary: Perry (1895); analysis: **England, Molnar & Richter, “John Perry's neglected critique of Kelvin's age for the Earth”, *GSA Today* 17(4), 2007**. **[P][F]**
- **6.4** Perry obtained ages of **2–3 billion years**. Source: England et al. 2007 (Perry's argument implies much older ages); summary in New World Encyclopedia / Simple Wikipedia (Perry 2–3 Ga). **[D]** — the film presents it as “Perry got an age of two to three billion years” which the summaries support; the primary paper is the authority for the convective argument itself.
- **6.5** Perry's argument was neglected and effectively forgotten for decades, rediscovered in the 2000s. Source: England et al. 2007 (“Perry's analysis was neglected or forgotten”). **[P][F]**
- **6.6** 1896: Becquerel found that uranium salts had fogged a photographic plate kept in the dark. Standard history of radioactivity (Becquerel 1896). **[F]**
- **6.7** The rocks have been generating their own heat all along (radiogenic heat). Standard geophysics. **[F]**
- **6.8–6.9** **Deliberate correction of a popular error**: adding radioactive heat to Kelvin's conduction calculation does *not* rescue it; the real flaw is convection. Sources: England, Molnar & Richter 2007 (explicitly states the popular story is incorrect and that radioactivity added to Kelvin's calculation would have left his estimate unaffected); Wikipedia “Earth's internal heat budget”. **[P][F]** — this is one of the film's differentiating claims and it is sourced to a peer-reviewed critique.
- **6.10** Radioactivity gave geologists an independent clock. Standard. **[F]**

### Chapter 7 — Rutherford's hourglass
- **7.1** Rutherford lectured at the Royal Institution, London, in **1904**, and used radioactivity to date a rock. Sources: Braterman, “Kelvin, Rutherford, and the Age of the Earth” (states a May 1904 Royal Institution lecture announcing ~500 My for a Cambrian rock); Wikipedia “Age of Earth” (1904 lecture, 40 Ma helium dating, Royal Institution anecdote). **[P][F]**
- **7.2–7.3** Radioactive decay rates are effectively constant and insensitive to temperature, pressure and chemical environment; that is what makes the decay a usable clock. Standard nuclear geochronology. **[F]**
- **7.4** His sample: on the order of **500 million years** (helium/lead method). Sources: Braterman (500 My at the Royal Institution); Wikipedia “Age of Earth” (Rutherford dated a rock at 40 Ma by helium in 1904; Boltwood then produced dates of 92–570 Ma). **Status: [D]** — the film says “around five hundred million years” attributed to the lecture and its best sample, which matches Braterman.
- **7.5–7.6** Kelvin in the audience, asleep, then sitting up with “a baleful glance”. Source: Rutherford's own account as recorded by A. S. Eve (1939), quoted in Wikipedia and on todayinsci. **[D]** — presented in the film as Rutherford's later recollection.
- **7.7** Rutherford's escape: Kelvin had limited the Earth's age “provided no new source was discovered”, and radium was such a source. Same source. **[D]**
- **7.8** The film states openly that this is an anecdote, not a transcript. **[X]** (honesty marker)
- **7.9–7.10** Locking a radioactive parent in a crystal starts an hourglass; the reading is valid only if the system stayed closed. Standard geochronology. **[F]**

### Chapter 8 — A clock that leaks
- **8.2–8.3** An hourglass works because nothing enters or leaves; radiometric dating requires the same: known initial daughter content, no addition, no loss. Standard geochronology (the “closed system” requirement). **[F]**
- **8.4** Real minerals fail these conditions: helium escapes, lead migrates, groundwater moves uranium in and out. Standard; discussed in Dalrymple's review of dating methods and in critiques. **[P][F]**
- **8.5** Early date sets were scattered (hundreds of millions to billions of years) and their reliability was openly uncertain. Sources: Dalrymple/TalkOrigins on anomalous ages and open-system behaviour; PBS “Radiometric dating finds Earth is 2.2 billion years old”. **[F]**
- **8.6** Bertram Boltwood, **1907**: measured uranium/lead in minerals and published ages reaching roughly **two billion years**; the first practical radiometric dating. Sources: PBS A Science Odyssey (1907, 2.2 billion years); ASA Wiens article (“first used in 1907”); Wikipedia “Age of Earth” (Boltwood supplied dates up to 570 Ma in 1905, and by 1907 the uranium–lead approach gave ~2 Ga). **Status: [D]** — the film says “published ages up to about two billion years”, supported by PBS.
- **8.7** The film's question. **[X]**

### Chapter 9 — The clean room
- **9.2** In **1948** Clair Patterson began work on the age problem (with Harrison Brown/George Tilton), using zircons of known age; his uranium data were consistent while his lead readings were persistently too high. Source: Wikipedia “Clair Patterson” (doctoral work from 1948; “Patterson's data typically was skewed with 'too much' lead”). **[P][F]**
- **9.3** The contamination was pervasive lead — in the laboratory, the dust, the water, and even in his own hair. Source: Wikipedia “Clair Patterson”. **[P][F]**
- **9.4** He built one of the first clean laboratories: sealing the lab against air-borne contamination, acid-cleaning apparatus, distilling chemicals. Source: Wikipedia “Clair Patterson”; chemeurope entry. **[P][F]**
- **9.5** Instead of relying on one mineral staying sealed, he used **two** uranium decay chains with different half-lives — U-238 → Pb-206 and U-235 → Pb-207 — as mutually checking clocks. Standard lead–lead dating; sources: Wikipedia (lead–lead dating), ASA Wiens. **[P][F]**
- **9.6** The lead isotopic composition locked in an iron meteorite supplies the solar system's starting composition, from which the Earth's age can be inferred. Source: **USGS, “Geologic Time: Age of the Earth”** (the best age for the Earth “is based on old, presumed single-stage leads coupled with the Pb ratios in troilite from iron meteorites, specifically the Canyon Diablo meteorite”). **[P][F]**
- **9.7** The sample: a fragment of the **Canyon Diablo** iron meteorite from Meteor Crater, Arizona — never melted, weathered or recycled since the early solar system. Source: USGS (same page); USGS image record on the Canyon Diablo fragment. **[P][F]**
- **9.8** Patterson published **4.55 ± 0.07 billion years** in 1956, “Age of Meteorites and the Earth”, *Geochimica et Cosmochimica Acta* 10: 230–237. Sources: Wikipedia; USGS; Chemeurope; fas37.org summary. **[P][F]**
- **9.9** The modern figure is **4.54 billion years with an uncertainty of about 1 %**. Source: **USGS** (“These calculations result in an age for the Earth and meteorites, and hence the Solar System, of 4.54 billion years with an uncertainty of less than 1 percent”). Wikipedia gives 4.54 ± 0.05 Ga. **[P][F]**
- **9.10** The film's closing observation — we dated the Earth by measuring rocks from the sky. **Interpretation** resting directly on the USGS reasoning. **[X]**

### Chapter 10 — What a clock assumes
- **10.2** Patterson then traced the lead contamination: industrial lead in ocean water about **100×** the natural background, and Greenland ice cores showing lead rising sharply after the 1920s. Sources: Wikipedia “Clair Patterson” (ice cores 1964/65; ocean-water comparison); kiddle/chemeurope summaries (ice cores from Greenland; >100× natural flux). **[P][F]**
- **10.3** The sources were tetraethyl lead in petrol plus paint, solder and food cans. Source: Wikipedia “Clair Patterson”. **[P][F]**
- **10.4** Lead was removed from petrol in the United States by **1986** (mandatory unleaded from 1975), and average blood lead levels fell by about **80 % by the late 1990s**. Sources: Wikipedia “Clair Patterson”; kiddle summary. **[P][F]**
- **10.6** The four-clocks comparison table: each clock with the assumption it depends on. **Film synthesis** of the sourced material above. **[X]**
- **10.8** The closing question about which records stayed closed. **Interpretation.** **[X]**
- **10.9** Biological ageing: how much is a countdown versus active repair, and how much repair capacity declines — explicitly presented as an **open question**, not a settled answer. (Deliberately no number, no mechanism claimed.) **[D]**
- **10.10** Closing line. **[X]**

## Debated, contested or deliberately softened in the film

1. **Perry's exact figure (2–3 Ga)** is reported here as the outcome of his argument, sourced to
   secondary summaries; the primary 1895 paper argues the convective case rather than publishing
   a single headline number in the form the film states. The film says “Perry got an age of two
   to three billion years” — a **reported estimate**, and it is the argument, not the digit, that
   the chapter turns on.
2. **Rutherford's lecture detail** (500 My, Kelvin asleep, the baleful glance) is **anecdote**:
   the remark is recorded by a biographer from Rutherford's later retelling. The film flags this
   in narration and on screen (“Rutherford's own account, told years later”; “a good anecdote,
   not a transcript”).
3. **Ussher's anchor datum**: the film names Nebuchadnezzar's death because the secondary
   literature names it, while noting in this ledger that sources differ on the precise regnal
   synchronism used.
4. **Boltwood's numbers** differ across sources (570 Ma in 1905, ~2 Ga in 1907). The film uses the
   higher figure with “about”, and attributes the leap in scale to him rather than a precise date.
5. **The flood-as-geology chapter** is presented as a historical episode in how the strata were
   explained, not as a claim about any flood event.
6. **The “radioactivity fixed Kelvin” story is deliberately contradicted** using England, Molnar &
   Richter (2007); viewers who know the popular version are told plainly that it is wrong.

## What the film does *not* claim

- No claim that science “proved religion wrong”. Ussher is presented as a competent scholar inside
  his own evidentiary world; the film's argument is about clocks, not about belief.
- No claim that radiometric dating is assumption-free. Chapter 8 exists precisely to show the
  assumptions and the failure modes.
- No claim about consciousness, free will, quantum effects or death — the reference film's
  favourite territory — beyond one sentence that ageing is genuinely unresolved.
- No invented quotations: the three quoted lines in the film (Ussher's date, Hutton's “no vestige
  of a beginning”, Playfair's “abyss of time”) are each verified in the sources above.

## Reproduce the research

```bash
# reference study (kept out of git)
python3 -m yt_dlp -f "bv*[height<=720]+ba/b[height<=720]" -o 'work/ref/ref17.%(ext)s' https://www.youtube.com/watch?v=XVQdhpwO75g
python3 agents/axiom/tools/frames.py agents/axiom/work/ref/ref17.mp4 --out agents/axiom/work/ref-inspect --every 15
```
