#!/usr/bin/env python3
"""axiom — HOW OLD IS THE EARTH? script, cue list and shot plan.

This file is DATA: narration sentences (cues), chapters, and the shot list that binds
each shot to a scene function and to the cues it covers. Timing is derived later from
the measured narration durations (timeline.py) — never from character counts.

Claim provenance for every factual sentence lives in ../evidence/source-rights.md,
keyed by cue id.
"""
from __future__ import annotations

TITLE = "How Old Is the Earth?"
SUBTITLE = "Three clocks that had to be broken"
REVISION = "r01"

CHAPTERS = [
    # ------------------------------------------------------------------ 1 ---
    dict(
        id=1, card="A date in the margin",
        sentences=[
            ("1.1", "In 1650, an Irish archbishop named James Ussher published a very large book about time: a chronology of the world, assembled year by year, from the first day of creation to his own century."),
            ("1.2", "On the first page, he wrote a date. 4004 BC, and, more precisely than most people remember, the night before the twenty-third of October."),
            ("1.3", "For the next two hundred years, that date was printed in the margins of English Bibles, which is how an enormous number of people came to know exactly how old the Earth was."),
            ("1.4", "Here is the part that makes the story worth an evening. Ussher was not a crank. He was a serious scholar who worked carefully, from the best evidence he could get his hands on."),
            ("1.5", "His mistake was not the arithmetic. It was the assumption underneath the arithmetic: that the only clock worth reading was written down in a book."),
            ("1.6", "This film is about three clocks that came after his, and why each one had to be broken before we could find the real age of the Earth."),
        ],
        shots=[
            dict(id="s01", scene="date_void", cues=["1.1", "1.2"], pre=1.2, post=1.0, bg="night"),
            dict(id="s02", scene="ussher_study", cues=["1.3"], pre=0.6, post=0.8, bg="parchment",
                 params={"size": 74}),
            dict(id="s03", scene="bible_margins", cues=["1.3"], pre=0.0, post=0.6, bg="parchment"),
            dict(id="s04", scene="bible_row", cues=["1.4"], pre=0.6, post=0.8, bg="parchment"),
            dict(id="s05", scene="ussher_writing", cues=["1.5"], pre=0.6, post=0.8, bg="parchment"),
            dict(id="s06", scene="three_clocks_tease", cues=["1.6"], pre=0.8, post=1.6, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 2 ---
    dict(
        id=2, card="Ussher's clock",
        sentences=[
            ("2.1", "Let us be fair to the man, and actually look at his clock."),
            ("2.2", "His raw material was a list of generations in Genesis. Adam is given nine hundred and thirty years. His son Seth, nine hundred and twelve. Others follow, hundreds of years each, faithfully recorded."),
            ("2.3", "If those are ages, and the list is continuous, then adding them up counts real time. The only missing piece is an anchor: one date, known from outside the Bible, to tie the end of the chain to ordinary history."),
            ("2.4", "Ussher chose the death of Nebuchadnezzar, the Babylonian king, which he could connect to surviving records. Then he counted backwards."),
            ("2.5", "He even had a view about the season. Creation, he argued, happened at the harvest, around the autumn equinox, because a year should begin when it has something to show for itself."),
            ("2.6", "The result was a genuinely precise claim: the world began on the night before the twenty-third of October, in 4004 BC."),
            ("2.7", "Two corrections while we are here. The genealogies really are in the text; he did not invent them. And the famous nine o'clock in the morning? Not his. That detail comes from a different scholar, working from a different calculation."),
        ],
        shots=[
            dict(id="s07", scene="ussher_study", cues=["2.1"], pre=0.5, post=0.6, bg="parchment",
                 params={"size": 70, "variant": "wide"}),
            dict(id="s08", scene="genealogy", cues=["2.2"], pre=0.4, post=0.6, bg="parchment"),
            dict(id="s09", scene="genealogy_anchor", cues=["2.3"], pre=0.4, post=0.6, bg="parchment"),
            dict(id="s10", scene="babylon", cues=["2.4"], pre=0.4, post=0.6, bg="parchment"),
            dict(id="s11", scene="count_back", cues=["2.4"], pre=0.0, post=0.5, bg="parchment"),
            dict(id="s12", scene="harvest", cues=["2.5"], pre=0.5, post=0.6, bg="field"),
            dict(id="s13", scene="date_stamp", cues=["2.6"], pre=0.4, post=0.8, bg="parchment"),
            dict(id="s14", scene="two_corrections", cues=["2.7"], pre=0.4, post=0.8, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 3 ---
    dict(
        id=3, card="The world did not fit",
        sentences=[
            ("3.1", "So if the arithmetic was fine and the sources were sincere, where did it go wrong?"),
            ("3.2", "Somewhere far from the study. Because a six thousand year old world has to explain everything, and the world kept producing things that did not fit."),
            ("3.3", "Egyptian king lists and Chinese records seemed to reach back further than the date allowed. That was awkward, but survivable: other kingdoms could be stretched, or dismissed."),
            ("3.4", "The fossils were harder. Why are there seashells in mountains? Why are there layers, one after another, each one asking for time?"),
            ("3.5", "The Flood answered the fossil question for a while. It explained the layers, the shells, the buried creatures, all at once, in one catastrophic year."),
            ("3.6", "But a one year flood has a problem. It has to do all of geology's work in twelve months, and the rocks do not look like they were in a hurry."),
            ("3.7", "So the date was stretched, and patched, and argued about. And eventually somebody asked the dangerous question: what if the problem is not the number? What if the problem is the clock?"),
        ],
        shots=[
            dict(id="s15", scene="study_wide", cues=["3.1"], pre=0.6, post=0.6, bg="parchment"),
            dict(id="s16", scene="archive", cues=["3.2", "3.3"], pre=0.5, post=0.8, bg="workshop"),
            dict(id="s17", scene="fossil_hill", cues=["3.4"], pre=0.5, post=0.7, bg="field"),
            dict(id="s18", scene="flood", cues=["3.5", "3.6"], pre=0.6, post=0.8, bg="ash"),
            dict(id="s19", scene="stretch_date", cues=["3.7"], pre=0.5, post=1.0, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 4 ---
    dict(
        id=4, card="The clock in the rock",
        sentences=[
            ("4.1", "Which brings us to a boat, and a rock, and one of the best sentences in the history of geology."),
            ("4.2", "In 1788, a Scottish farmer and geologist called James Hutton sailed along the coast near Edinburgh with two friends, and stopped at a place called Siccar Point."),
            ("4.3", "What he found there does not look dramatic. It looks like a mistake in a stonemason's work."),
            ("4.4", "Grey rock, standing almost vertical, like books on a shelf. And lying on top of it, in a completely different direction, red sandstone."),
            ("4.5", "The rock is a record of a sequence. Read it in order."),
            ("4.6", "First, grey sediment settles in water, in flat layers, and hardens. Then those layers are folded, and lifted, until they are standing on end. Then the top of them is worn flat by weather and sea. And then the sea returns, and lays the red sand on the worn surface."),
            ("4.7", "Every one of those steps is slow. Not a flood's worth of slow. Ordinary, patient, one day at a time slow, repeated beyond counting."),
            ("4.8", "Hutton wrote that in the Earth he could find no vestige of a beginning, and no prospect of an end."),
            ("4.9", "His friend John Playfair put it better, years later, remembering the trip: the mind, he wrote, seemed to grow giddy looking so far into the abyss of time."),
            ("4.10", "But notice what that is. It is a feeling. It is the shock of scale, not a measurement."),
            ("4.11", "Hutton proved that the Earth is deep. He never told us how deep. For that, somebody had to build a clock."),
        ],
        shots=[
            dict(id="s20", scene="coast_1788", cues=["4.1", "4.2"], pre=0.8, post=0.9, bg="cool"),
            dict(id="s21", scene="siccar_rock", cues=["4.3", "4.4"], pre=0.6, post=0.9, bg="cool"),
            dict(id="s22", scene="siccar_steps", cues=["4.5", "4.6"], pre=0.6, post=1.0, bg="cool",
                 params={"step": 0}),
            dict(id="s23", scene="siccar_slow", cues=["4.7"], pre=0.5, post=0.8, bg="cool"),
            dict(id="s24", scene="hutton_phrase", cues=["4.8"], pre=0.6, post=0.9, bg="cool"),
            dict(id="s25", scene="playfair_giddy", cues=["4.9"], pre=0.6, post=1.0, bg="cool"),
            dict(id="s26", scene="no_measurement", cues=["4.10", "4.11"], pre=0.6, post=1.4, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 5 ---
    dict(
        id=5, card="Kelvin's cooling clock",
        sentences=[
            ("5.1", "Seventy years later, the most famous physicist in Britain decided to stop talking about feelings, and put a number on it."),
            ("5.2", "William Thomson, later Lord Kelvin, had already worked out how heat moves through solid rock, and he trusted the arithmetic completely."),
            ("5.3", "His idea was a cooling ball. The Earth begins molten. Rock conducts heat badly, so the inside stays hot while the surface leaks warmth into space. Measure that leak, and you know how long the ball has been cooling."),
            ("5.4", "It is a genuinely elegant argument. One measurement, one physical law, and nothing but physics."),
            ("5.5", "In 1862 he published the answer: something like a hundred million years. Later he tightened it to twenty million, maybe forty. Shorter than that, and the planet simply could not have cooled this much."),
            ("5.6", "He applied the same physics to the Sun, and got the same kind of answer: tens of millions of years of sunlight, and no more."),
            ("5.7", "Which was terrible news for geology, which had just started to get used to deep time. And worse news for Charles Darwin, who needed a very long history for slow natural selection to work with."),
            ("5.8", "Here is what is easy to forget. Kelvin was not being stubborn. He was doing exactly what we ask scientists to do: take the physics you trust, apply it to the world, and accept the answer even when it is inconvenient."),
        ],
        shots=[
            dict(id="s27", scene="glasgow_board", cues=["5.1", "5.2"], pre=0.7, post=0.9, bg="chapel"),
            dict(id="s28", scene="cooling_ball", cues=["5.3"], pre=0.6, post=0.9, bg="deep"),
            dict(id="s29", scene="elegant_law", cues=["5.4"], pre=0.5, post=0.8, bg="parchment"),
            dict(id="s30", scene="kelvin_number", cues=["5.5"], pre=0.5, post=0.9, bg="parchment"),
            dict(id="s31", scene="measure_heat", cues=["5.5"], pre=0.0, post=0.5, bg="workshop"),
            dict(id="s32", scene="sun_budget", cues=["5.6"], pre=0.6, post=0.9, bg="night"),
            dict(id="s33", scene="darwin_worry", cues=["5.7"], pre=0.6, post=1.0, bg="parchment"),
            dict(id="s34", scene="kelvin_honest", cues=["5.8"], pre=0.6, post=1.2, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 6 ---
    dict(
        id=6, card="The heat inside",
        sentences=[
            ("6.1", "The flaw was found by a man who had worked for him."),
            ("6.2", "In 1895, John Perry pointed out that a cooling ball is a poor model of a planet. Solid rock conducts heat slowly, but a hot, soft interior does not have to conduct it at all."),
            ("6.3", "If the inside of the Earth flows, even very slowly, then heat is carried to the surface by the moving material itself. Convection, not conduction."),
            ("6.4", "And that changes the arithmetic completely. Perry got an age of two to three billion years, in 1895, from nothing but fluid dynamics."),
            ("6.5", "Nobody believed it. His paper was read, filed, and forgotten, and it stayed forgotten for about a century."),
            ("6.6", "Then reality intervened. In 1896, Henri Becquerel took a packet of uranium salts out of a drawer, and found that they had fogged a photographic plate in the dark."),
            ("6.7", "The rocks were radioactive. They had been making their own heat the whole time, quietly, from the beginning."),
            ("6.8", "Now, a correction, because this is where the standard story goes wrong. Radioactivity does not rescue Kelvin's number. Add radioactive heat into his calculation, and you still get a young Earth."),
            ("6.9", "What actually breaks his clock is Perry's point: convection. A planet whose insides move loses heat in a way Kelvin's equation simply could not see."),
            ("6.10", "But radioactivity gave geologists something much better than a repair to an old argument. It gave them a clock of their own."),
        ],
        shots=[
            dict(id="s35", scene="perry_office", cues=["6.1", "6.2"], pre=0.6, post=0.8, bg="workshop"),
            dict(id="s36", scene="convection", cues=["6.3"], pre=0.5, post=0.8, bg="deep"),
            dict(id="s37", scene="perry_number", cues=["6.4"], pre=0.4, post=0.8, bg="parchment"),
            dict(id="s38", scene="forgotten_paper", cues=["6.5"], pre=0.6, post=0.9, bg="workshop"),
            dict(id="s39", scene="becquerel_drawer", cues=["6.6"], pre=0.6, post=0.9, bg="night"),
            dict(id="s40", scene="radioactive_rock", cues=["6.7"], pre=0.5, post=0.9, bg="deep"),
            dict(id="s41", scene="heat_correction", cues=["6.8", "6.9"], pre=0.6, post=1.0, bg="parchment"),
            dict(id="s42", scene="new_clock", cues=["6.10"], pre=0.7, post=1.3, bg="deep"),
        ],
    ),
    # ------------------------------------------------------------------ 7 ---
    dict(
        id=7, card="Rutherford's hourglass",
        sentences=[
            ("7.1", "In 1904, at the Royal Institution in London, Ernest Rutherford stood up and dated a rock."),
            ("7.2", "His insight was simple and strange. Radioactive atoms decay at a rate that nothing seems to affect. You can heat them, freeze them, squeeze them, bury them for a billion years: the same fraction flips over in the same time."),
            ("7.3", "That is the definition of a good clock. It runs whether or not anyone is watching, and it does not care what happens to the room."),
            ("7.4", "Rutherford measured how much helium and lead had collected inside a mineral, did the arithmetic, and told his audience that his best sample was around five hundred million years old."),
            ("7.5", "Sitting in that audience was Lord Kelvin, whose number was, at most, a few tens of millions. Rutherford later told the story himself: he spotted the old man in the audience, braced for an argument, and watched him fall asleep."),
            ("7.6", "Then, at the crucial line, he saw Kelvin sit up, open one eye, and give him a baleful look."),
            ("7.7", "Rutherford had an escape ready. He said that Lord Kelvin had limited the age of the Earth, provided that no new source of energy was discovered. And this evening's subject, radium, was exactly such a source."),
            ("7.8", "It is a wonderful story, and here is one honest footnote: that exchange is Rutherford's own account, told years later. Treat it as a good anecdote, not a transcript."),
            ("7.9", "The idea behind it, though, is solid, and it is beautiful. Lock a radioactive element inside a crystal, and it starts an hourglass running."),
            ("7.10", "There is just one condition. For the reading to be true, the hourglass has to stay sealed."),
        ],
        shots=[
            dict(id="s43", scene="royal_institution", cues=["7.1"], pre=0.7, post=0.8, bg="chapel"),
            dict(id="s44", scene="decay_steadfast", cues=["7.2"], pre=0.5, post=0.8, bg="deep"),
            dict(id="s45", scene="good_clock", cues=["7.3"], pre=0.5, post=0.8, bg="parchment"),
            dict(id="s46", scene="rutherford_sample", cues=["7.4"], pre=0.5, post=0.8, bg="chapel"),
            dict(id="s47", scene="kelvin_asleep", cues=["7.5", "7.6"], pre=0.7, post=1.0, bg="chapel"),
            dict(id="s48", scene="escape_line", cues=["7.7"], pre=0.5, post=0.8, bg="chapel"),
            dict(id="s49", scene="footnote", cues=["7.8"], pre=0.5, post=0.9, bg="parchment"),
            dict(id="s50", scene="hourglass_start", cues=["7.9"], pre=0.6, post=0.9, bg="deep"),
            dict(id="s51", scene="seal_crack", cues=["7.10"], pre=0.6, post=1.4, bg="deep"),
        ],
    ),
    # ------------------------------------------------------------------ 8 ---
    dict(
        id=8, card="A clock that leaks",
        sentences=[
            ("8.1", "Which is a much bigger problem than it sounds."),
            ("8.2", "An hourglass is honest because nothing gets in and nothing gets out. Sand starts in the top, sand falls through the neck, and at any moment the two heaps tell you how long it has been running."),
            ("8.3", "Now imagine the same hourglass inside a rock. Three things have to be true. Nothing was in the bottom when the clock started. Nothing has been added since. And nothing has escaped."),
            ("8.4", "Real minerals fail all three. Helium leaks out of crystals. Lead migrates. Groundwater carries uranium in and out. A rock is not a sealed glass."),
            ("8.5", "The early dates were scattered for exactly this reason: hundreds of millions of years in one rock, two billion in the next, and nobody could say which was right."),
            ("8.6", "In 1907, an American chemist called Bertram Boltwood measured uranium against lead in a set of minerals, and published ages up to about two billion years. It was the first real radiometric dating, and it was openly uncertain."),
            ("8.7", "So how do you measure something, when your clock keeps disagreeing with itself?"),
        ],
        shots=[
            dict(id="s52", scene="hourglass_honest", cues=["8.1", "8.2"], pre=0.6, post=0.9, bg="parchment"),
            dict(id="s53", scene="three_assumptions", cues=["8.3"], pre=0.5, post=1.0, bg="parchment"),
            dict(id="s54", scene="helium_leak", cues=["8.4"], pre=0.5, post=0.8, bg="workshop"),
            dict(id="s55", scene="uranium_moves", cues=["8.4"], pre=0.0, post=0.6, bg="workshop"),
            dict(id="s56", scene="scatter_dates", cues=["8.5"], pre=0.5, post=0.9, bg="parchment"),
            dict(id="s57", scene="boltwood", cues=["8.6"], pre=0.6, post=0.9, bg="workshop"),
            dict(id="s58", scene="puzzle", cues=["8.7"], pre=0.6, post=1.4, bg="parchment"),
        ],
    ),
    # ------------------------------------------------------------------ 9 ---
    dict(
        id=9, card="The clean room",
        sentences=[
            ("9.1", "The answer, when it came, was to stop asking a single rock to be honest, and to ask the whole system instead."),
            ("9.2", "In 1948, a graduate student named Clair Patterson started work on a zircon crystal from a rock whose age was already known. His uranium measurements looked fine. His lead measurements were always too high."),
            ("9.3", "Every sample was contaminated. He tested everything, including his own hair. The contamination was lead, and it was everywhere: in the dust, in the water, in the solder, in the paint on the walls."),
            ("9.4", "So he built a room where lead could not get in. He acid washed every tool. He distilled his own chemicals. He filtered the air. It is considered one of the first clean laboratories in science."),
            ("9.5", "Now he needed a better clock. Instead of trusting one mineral to stay sealed for four billion years, he used the relationship between two decay chains: uranium 238 turning into lead 206, and uranium 235 turning into lead 207, at different speeds."),
            ("9.6", "Different speeds, same rock, gave him two independent readings that could check each other. And the lead locked inside an iron meteorite gave him the starting composition of the whole solar system."),
            ("9.7", "The sample was a lump of iron from Canyon Diablo, in Arizona: a fragment of the early solar system that had never been melted, rained on, or recycled."),
            ("9.8", "In 1956 he published the number. Four point five five billion years, with an uncertainty of seventy million. The age of the Earth. The age of the meteorite. The age of the solar system. All the same event."),
            ("9.9", "Seventy years later, that number has barely moved. The current figure is four point five four billion years, with an uncertainty of about one percent."),
            ("9.10", "Which is a curious kind of achievement, when you think about it. We did not measure the Earth. We measured rocks that fell out of the sky, and reasoned that we were made of the same cloud."),
        ],
        shots=[
            dict(id="s59", scene="whole_system", cues=["9.1"], pre=0.6, post=0.8, bg="parchment"),
            dict(id="s60", scene="patterson_zircon", cues=["9.2"], pre=0.6, post=0.8, bg="workshop"),
            dict(id="s61", scene="lead_everywhere", cues=["9.3"], pre=0.5, post=0.9, bg="workshop"),
            dict(id="s62", scene="clean_room", cues=["9.4"], pre=0.5, post=0.9, bg="cool"),
            dict(id="s63", scene="two_clocks", cues=["9.5", "9.6"], pre=0.6, post=1.0, bg="parchment"),
            dict(id="s64", scene="meteorite", cues=["9.7"], pre=0.6, post=0.9, bg="workshop"),
            dict(id="s65", scene="spectrometer", cues=["9.8"], pre=0.5, post=0.8, bg="workshop"),
            dict(id="s66", scene="number_1956", cues=["9.8"], pre=0.0, post=1.0, bg="parchment"),
            dict(id="s67", scene="modern_number", cues=["9.9"], pre=0.5, post=0.9, bg="parchment"),
            dict(id="s68", scene="same_cloud", cues=["9.10"], pre=0.6, post=1.4, bg="night"),
        ],
    ),
    # ----------------------------------------------------------------- 10 ---
    dict(
        id=10, card="What a clock assumes",
        sentences=[
            ("10.1", "There is an epilogue, and it belongs to Patterson."),
            ("10.2", "The lead that ruined his samples had come from somewhere, and he went looking for it. In ocean water, he found industrial lead a hundred times greater than the natural background. In ice cores from Greenland, he found lead rising sharply after the nineteen twenties."),
            ("10.3", "The source was the tetraethyl lead added to petrol, along with paint, solder and food cans. The contamination that had broken his measurements was in everybody's blood."),
            ("10.4", "He spent the rest of his career on it. Lead was removed from petrol by the mid nineteen eighties, and average blood lead levels in the United States fell by about eighty percent by the late nineties."),
            ("10.5", "So here is the pattern that runs underneath this whole story."),
            ("10.6", "Ussher's clock was careful, complete, and completely sealed inside its own evidence. Kelvin's clock was built from physics he was right about, applied to a planet he was wrong about. Rutherford's clock was honest for exactly as long as nobody asked what the rock had been doing in the meantime."),
            ("10.7", "None of them were stupid. Each one was an assumption, dressed up as a measurement."),
            ("10.8", "And the question they leave us is not really about rocks. It is about how we know anything about the past at all: which parts of the record have stayed closed, and which ones have been quietly leaking while we were not looking."),
            ("10.9", "We know how old the Earth is. We still argue about how to read the clocks inside ourselves: how much of ageing is a clock that simply counts down, and how much is a system that repairs, or fails to. That one is genuinely open."),
            ("10.10", "The rocks do not care. They just keep time."),
        ],
        shots=[
            dict(id="s69", scene="epilogue_open", cues=["10.1"], pre=0.6, post=0.8, bg="parchment"),
            dict(id="s70", scene="ocean_lead", cues=["10.2"], pre=0.5, post=0.9, bg="cool"),
            dict(id="s71", scene="ice_core", cues=["10.2"], pre=0.0, post=0.6, bg="cool"),
            dict(id="s72", scene="products", cues=["10.3"], pre=0.5, post=0.9, bg="workshop"),
            dict(id="s73", scene="blood_lead", cues=["10.4"], pre=0.5, post=0.9, bg="parchment"),
            dict(id="s74", scene="four_clocks_table", cues=["10.5", "10.6"], pre=0.7, post=1.2, bg="parchment"),
            dict(id="s75", scene="assumptions", cues=["10.7", "10.8"], pre=0.6, post=1.2, bg="parchment"),
            dict(id="s76", scene="aging_question", cues=["10.9"], pre=0.6, post=1.2, bg="night"),
            dict(id="s77", scene="end_card", cues=["10.10"], pre=0.8, post=6.0, bg="night"),
        ],
    ),
]


def all_cues():
    for ch in CHAPTERS:
        for cid, text in ch["sentences"]:
            yield ch["id"], cid, text


def all_shots():
    for ch in CHAPTERS:
        for sh in ch["shots"]:
            yield ch["id"], sh
